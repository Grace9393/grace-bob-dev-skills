from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import os
import re
import sqlite3
import sys
import tempfile
import uuid
from collections import deque
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - PyYAML is available in this repo.
    yaml = None


ENGINE_DIR = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ENGINE_DIR / "assets" / "schema.sql"
POLICY_SEVERITY = {
    "none": 0,
    "mark_needs_review": 1,
    "mark_outdated": 2,
    "block_until_refreshed": 3,
}
POLICY_TO_VALIDITY = {
    "none": "current",
    "mark_needs_review": "needs_review",
    "mark_outdated": "outdated",
    "block_until_refreshed": "blocked_until_refreshed",
}


class CommandError(RuntimeError):
    pass


@dataclass(frozen=True)
class RuntimeConfig:
    db_path: Path
    cwd: Path
    profile: str
    profile_config: Path | None
    profile_data: dict[str, Any]


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def make_id() -> str:
    return str(uuid.uuid4())


def json_dumps(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    data = parse_simple_yaml(text) if yaml is None else yaml.safe_load(text) or {}
    if not isinstance(data, dict):
        raise CommandError(f"Expected mapping in YAML file: {path}")
    return data


def parse_scalar(value: str) -> Any:
    value = value.strip()
    if value == "":
        return ""
    if value in {"true", "false"}:
        return value == "true"
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [parse_scalar(part.strip()) for part in inner.split(",")]
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    with contextlib.suppress(ValueError):
        return int(value)
    return value


def parse_simple_yaml(text: str) -> dict[str, Any]:
    """Parse the small YAML subset used by profile assets when PyYAML is absent."""
    root: dict[str, Any] = {}
    stack: list[tuple[int, Any]] = [(-1, root)]
    pending_key: dict[int, str] = {}

    def parent_for(indent: int) -> Any:
        while stack and indent <= stack[-1][0]:
            stack.pop()
        return stack[-1][1]

    lines = [line.rstrip() for line in text.splitlines() if line.strip() and not line.lstrip().startswith("#")]
    for raw in lines:
        indent = len(raw) - len(raw.lstrip(" "))
        stripped = raw.strip()
        parent = parent_for(indent)

        if stripped.startswith("- "):
            item_text = stripped[2:].strip()
            if not isinstance(parent, list):
                grand = stack[-2][1] if len(stack) >= 2 else None
                key = None
                if isinstance(grand, dict):
                    for candidate_key, candidate_value in grand.items():
                        if candidate_value is parent:
                            key = candidate_key
                            break
                if not isinstance(grand, dict) or key is None:
                    raise CommandError("Unsupported YAML list structure")
                new_list: list[Any] = []
                grand[key] = new_list
                stack[-1] = (stack[-1][0], new_list)
                parent = new_list
            if ":" in item_text:
                key, value = item_text.split(":", 1)
                item: dict[str, Any] = {key.strip(): parse_scalar(value)}
                parent.append(item)
                stack.append((indent, item))
            else:
                parent.append(parse_scalar(item_text))
            continue

        if ":" not in stripped:
            raise CommandError(f"Unsupported YAML line: {raw}")
        key, value = stripped.split(":", 1)
        key = key.strip()
        value = value.strip()
        if isinstance(parent, list):
            raise CommandError("Unsupported YAML mapping inside list without item marker")
        if value:
            parent[key] = parse_scalar(value)
        else:
            parent[key] = {}
            pending_key[indent] = key
            stack.append((indent, parent[key]))

    return root


def default_db_path(profile: str, cwd: Path) -> Path:
    if profile == "ibm_bid":
        return cwd / "tmp" / "ibm-bid-project.sqlite"
    return cwd / "tmp" / "agent-state.sqlite"


def connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA journal_mode=WAL")
    migrate_existing_schema(conn)
    return conn


def execute_schema(conn: sqlite3.Connection) -> None:
    for statement in split_sql_script(SCHEMA_PATH.read_text(encoding="utf-8")):
        conn.execute(statement)
    ensure_column(conn, "work_item", "tag", "TEXT")


def ensure_column(conn: sqlite3.Connection, table: str, column: str, definition: str) -> None:
    columns = {row["name"] if isinstance(row, sqlite3.Row) else row[1] for row in conn.execute(f"PRAGMA table_info({table})")}
    if column not in columns:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def migrate_existing_schema(conn: sqlite3.Connection) -> None:
    exists = one(conn, "SELECT name FROM sqlite_master WHERE type='table' AND name='work_item'")
    if exists:
        ensure_column(conn, "work_item", "tag", "TEXT")


def split_sql_script(script: str) -> list[str]:
    statements: list[str] = []
    current: list[str] = []
    for line in script.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("--"):
            continue
        current.append(line)
        if stripped.endswith(";"):
            statements.append("\n".join(current).rstrip().rstrip(";"))
            current = []
    if current:
        statements.append("\n".join(current))
    return statements


def event(conn: sqlite3.Connection, project_id: str | None, event_type: str, entity_type: str | None = None,
          entity_id: str | None = None, agent_id: str | None = None, detail: dict[str, Any] | None = None) -> int:
    cur = conn.execute(
        """
        INSERT INTO event_log(project_id, event_type, entity_type, entity_id, agent_id, detail_json, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (project_id, event_type, entity_type, entity_id, agent_id, json_dumps(detail or {}), utc_now()),
    )
    return int(cur.lastrowid)


def one(conn: sqlite3.Connection, sql: str, params: tuple[Any, ...] = ()) -> sqlite3.Row | None:
    return conn.execute(sql, params).fetchone()


def all_rows(conn: sqlite3.Connection, sql: str, params: tuple[Any, ...] = ()) -> list[sqlite3.Row]:
    return list(conn.execute(sql, params).fetchall())


def require_project(conn: sqlite3.Connection) -> sqlite3.Row:
    row = one(conn, "SELECT * FROM project ORDER BY created_at LIMIT 1")
    if row is None:
        raise CommandError("No project found. Run init first.")
    return row


def label_prefix(entity: str, profile: str = "generic") -> str:
    if profile == "ibm_bid":
        return {
            "project": "PRJ",
            "work_item": "WI",
            "source_asset": "DOC",
            "source_asset_version": "DOCV",
            "artifact": "ART",
            "artifact_version": "ARTV",
            "impact": "IMP",
        }[entity]
    return {
        "project": "PRJ",
        "work_item": "WI",
        "source_asset": "SRC",
        "source_asset_version": "SRCV",
        "artifact": "ART",
        "artifact_version": "ARTV",
        "impact": "IMP",
    }[entity]


def next_label(conn: sqlite3.Connection, project_id: str | None, entity: str, profile: str) -> str:
    prefix = label_prefix(entity, profile)
    table = entity
    number_start = len(prefix) + 2
    if entity == "project":
        row = one(
            conn,
            "SELECT COALESCE(MAX(CAST(SUBSTR(label, ?) AS INTEGER)), 0) AS max_num FROM project WHERE label LIKE ?",
            (number_start, f"{prefix}-%"),
        )
    else:
        row = one(
            conn,
            f"""
            SELECT COALESCE(MAX(CAST(SUBSTR(label, ?) AS INTEGER)), 0) AS max_num
            FROM {table}
            WHERE project_id=? AND label LIKE ?
            """,
            (number_start, project_id, f"{prefix}-%"),
        )
    max_num = int(row["max_num"]) if row else 0
    return f"{prefix}-{max_num + 1:04d}"


def slug(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "_", value.strip().lower()).strip("_")
    return cleaned or "item"


def resolve_entity(conn: sqlite3.Connection, label_or_id: str) -> tuple[str, sqlite3.Row]:
    table_by_prefix = {
        "PRJ": "project",
        "WI": "work_item",
        "SRC": "source_asset",
        "DOC": "source_asset",
        "SRCV": "source_asset_version",
        "DOCV": "source_asset_version",
        "ART": "artifact",
        "ARTV": "artifact_version",
        "IMP": "impact",
    }
    prefix = label_or_id.split("-", 1)[0]
    tables = [table_by_prefix[prefix]] if prefix in table_by_prefix else [
        "project", "work_item", "source_asset", "source_asset_version", "artifact", "artifact_version", "impact"
    ]
    for table in tables:
        row = one(conn, f"SELECT * FROM {table} WHERE id=? OR label=?", (label_or_id, label_or_id))
        if row is not None:
            return table, row
    raise CommandError(f"Unknown label or id: {label_or_id}")


def sha256_file(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as tmp:
            tmp.write(content)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, path)
    except Exception:
        if tmp_path is not None:
            with contextlib.suppress(FileNotFoundError):
                tmp_path.unlink()
        raise


def resolve_path(config: RuntimeConfig, value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return config.cwd / path


def output_path(config: RuntimeConfig, key: str, fallback: str) -> Path:
    paths = config.profile_data.get("paths", {}) if config.profile_data else {}
    return resolve_path(config, paths.get(key, fallback))


def context_dir(config: RuntimeConfig) -> Path:
    return output_path(config, "context_packs", "./tmp/context-packs")


def impact_dir(config: RuntimeConfig) -> Path:
    return output_path(config, "impact_reports", "./tmp/impact-reports")


def dashboard_path(config: RuntimeConfig) -> Path:
    return output_path(config, "dashboard", "./tmp/agent-state.md")


def graph_path(config: RuntimeConfig) -> Path:
    return output_path(config, "graph", "./tmp/agent-state-graph.mmd")


def load_profile_config(args: argparse.Namespace, cwd: Path) -> RuntimeConfig:
    profile = getattr(args, "profile", None) or "generic"
    profile_config = Path(args.profile_config).resolve() if getattr(args, "profile_config", None) else None
    profile_data = load_yaml(profile_config) if profile_config else {}
    if profile_config:
        profile_data = expand_skill_dir(profile_data, profile_config.parent.parent)
    if profile_data.get("profile"):
        profile = str(profile_data["profile"])
    db_path = Path(args.db).resolve() if getattr(args, "db", None) else default_db_path(profile, cwd)
    return RuntimeConfig(db_path=db_path, cwd=cwd, profile=profile, profile_config=profile_config, profile_data=profile_data)


def expand_skill_dir(value: Any, skill_dir: Path) -> Any:
    if isinstance(value, str):
        return value.replace("$SKILL_DIR", str(skill_dir))
    if isinstance(value, list):
        return [expand_skill_dir(item, skill_dir) for item in value]
    if isinstance(value, dict):
        return {key: expand_skill_dir(item, skill_dir) for key, item in value.items()}
    return value


@contextlib.contextmanager
def transaction(conn: sqlite3.Connection):
    try:
        conn.execute("BEGIN IMMEDIATE")
        yield
    except Exception:
        conn.rollback()
        raise
    else:
        conn.commit()


def create_project(conn: sqlite3.Connection, config: RuntimeConfig, name: str) -> sqlite3.Row:
    now = utc_now()
    project_id = make_id()
    label = next_label(conn, None, "project", config.profile)
    conn.execute(
        """
        INSERT INTO project(id, label, profile, name, root_path, metadata_json, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (project_id, label, config.profile, name, str(config.cwd), json_dumps({"profile_config": str(config.profile_config) if config.profile_config else None}), now, now),
    )
    event(conn, project_id, "project_initialized", "project", project_id, detail={"label": label, "profile": config.profile})
    return require_project(conn)


def create_work(conn: sqlite3.Connection, project_id: str, profile: str, title: str, item_type: str = "task",
                key: str | None = None, parent: str | None = None, phase: str | None = None,
                status: str = "ready", description: str | None = None, priority: int = 3,
                source_work_item: str | None = None, tag: str | None = None) -> sqlite3.Row:
    parent_id = None
    if parent:
        table, parent_row = resolve_entity(conn, parent)
        if table != "work_item":
            raise CommandError("Parent must be a work item")
        parent_id = parent_row["id"]
    now = utc_now()
    item_id = make_id()
    label = next_label(conn, project_id, "work_item", profile)
    work_key = key or slug(title)
    conn.execute(
        """
        INSERT INTO work_item(
          id, project_id, label, parent_work_item_id, work_item_key, item_type, title, description, tag,
          phase, status, priority, created_at, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (item_id, project_id, label, parent_id, work_key, item_type, title, description, tag, phase, status, priority, now, now),
    )
    detail = {"label": label, "title": title}
    if tag:
        detail["tag"] = tag
    if source_work_item:
        source_table, source_row = resolve_entity(conn, source_work_item)
        if source_table != "work_item":
            raise CommandError("Source work item must be a work item")
        detail["source_work_item"] = source_row["label"]
    event(conn, project_id, "work_item_created", "work_item", item_id, detail=detail)
    return one(conn, "SELECT * FROM work_item WHERE id=?", (item_id,))


def create_source(conn: sqlite3.Connection, project_id: str, profile: str, title: str, asset_type: str,
                  key: str | None = None, path: str | None = None, version_label: str = "v1",
                  change_note: str | None = None) -> sqlite3.Row:
    now = utc_now()
    asset_id = make_id()
    label = next_label(conn, project_id, "source_asset", profile)
    asset_key = key or slug(title)
    conn.execute(
        """
        INSERT INTO source_asset(id, project_id, label, asset_key, asset_type, title, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (asset_id, project_id, label, asset_key, asset_type, title, now, now),
    )
    event(conn, project_id, "source_asset_created", "source_asset", asset_id, detail={"label": label, "title": title})
    if path:
        add_source_version(conn, project_id, profile, asset_id, path, version_label, change_note)
    return one(conn, "SELECT * FROM source_asset WHERE id=?", (asset_id,))


def add_source_version(conn: sqlite3.Connection, project_id: str, profile: str, asset_id: str, path: str,
                       version_label: str, change_note: str | None = None) -> sqlite3.Row:
    now = utc_now()
    row = one(conn, "SELECT COALESCE(MAX(version_number), 0) AS max_version FROM source_asset_version WHERE source_asset_id=?", (asset_id,))
    version_number = int(row["max_version"]) + 1
    version_id = make_id()
    label = next_label(conn, project_id, "source_asset_version", profile)
    digest = sha256_file(Path(path))
    conn.execute(
        """
        INSERT INTO source_asset_version(
          id, project_id, label, source_asset_id, version_number, version_label, path, sha256,
          change_note, created_at, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (version_id, project_id, label, asset_id, version_number, version_label, path, digest, change_note, now, now),
    )
    conn.execute(
        "UPDATE source_asset SET current_version_id=?, row_version=row_version+1, updated_at=? WHERE id=?",
        (version_id, now, asset_id),
    )
    event(conn, project_id, "source_asset_version_created", "source_asset_version", version_id,
          detail={"label": label, "version_label": version_label, "path": path})
    return one(conn, "SELECT * FROM source_asset_version WHERE id=?", (version_id,))


def create_artifact(conn: sqlite3.Connection, project_id: str, profile: str, title: str, artifact_type: str,
                    owner: str, key: str | None = None, path: str | None = None) -> sqlite3.Row:
    table, owner_row = resolve_entity(conn, owner)
    if table != "work_item":
        raise CommandError("Artifact owner must be a work item")
    now = utc_now()
    artifact_id = make_id()
    label = next_label(conn, project_id, "artifact", profile)
    artifact_key = key or slug(title)
    conn.execute(
        """
        INSERT INTO artifact(id, project_id, label, artifact_key, artifact_type, title, path, owner_work_item_id, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (artifact_id, project_id, label, artifact_key, artifact_type, title, path, owner_row["id"], now, now),
    )
    event(conn, project_id, "artifact_created", "artifact", artifact_id, detail={"label": label, "title": title})
    return one(conn, "SELECT * FROM artifact WHERE id=?", (artifact_id,))


def active_claim(conn: sqlite3.Connection, work_item_id: str, agent_id: str | None = None) -> sqlite3.Row | None:
    if agent_id:
        return one(conn, "SELECT * FROM work_item_claim WHERE work_item_id=? AND agent_id=? AND status='active'",
                   (work_item_id, agent_id))
    return one(conn, "SELECT * FROM work_item_claim WHERE work_item_id=? AND status='active'", (work_item_id,))


def expire_claims(conn: sqlite3.Connection, project_id: str, now: str | None = None) -> list[sqlite3.Row]:
    now = now or utc_now()
    expired = all_rows(
        conn,
        "SELECT * FROM work_item_claim WHERE project_id=? AND status='active' AND expires_at <= ?",
        (project_id, now),
    )
    for claim in expired:
        conn.execute(
            """
            UPDATE work_item_claim
            SET status='expired', released_at=?, release_reason='expired', row_version=row_version+1
            WHERE id=?
            """,
            (now, claim["id"]),
        )
        has_other_active = one(
            conn,
            "SELECT id FROM work_item_claim WHERE work_item_id=? AND status='active' AND id!=?",
            (claim["work_item_id"], claim["id"]),
        )
        if not has_other_active:
            conn.execute(
                """
                UPDATE work_item
                SET status='ready', updated_at=?
                WHERE id=? AND status='in_progress'
                """,
                (now, claim["work_item_id"]),
            )
        event(
            conn,
            project_id,
            "work_item_claim_expired",
            "work_item",
            claim["work_item_id"],
            claim["agent_id"],
            {"claim_id": claim["id"]},
        )
    return expired


def incomplete_upstream_blockers(conn: sqlite3.Connection, work_item_id: str) -> list[sqlite3.Row]:
    return all_rows(
        conn,
        """
        SELECT up.* FROM work_dependency dep
        JOIN work_item up ON up.id = dep.upstream_work_item_id
        WHERE dep.downstream_work_item_id=? AND up.status!='complete'
        """,
        (work_item_id,),
    )


def claim_work_item(
    conn: sqlite3.Connection,
    project_id: str,
    work: sqlite3.Row,
    agent_id: str,
    lease_minutes: int,
    expired_claim_count: int = 0,
) -> sqlite3.Row:
    now_dt = datetime.now(UTC).replace(microsecond=0)
    now = now_dt.isoformat().replace("+00:00", "Z")
    expires = (now_dt + timedelta(minutes=lease_minutes)).isoformat().replace("+00:00", "Z")
    claim_id = make_id()
    conn.execute(
        """
        INSERT INTO work_item_claim(id, project_id, work_item_id, agent_id, status, claimed_at, heartbeat_at, expires_at)
        VALUES (?, ?, ?, ?, 'active', ?, ?, ?)
        """,
        (claim_id, project_id, work["id"], agent_id, now, now, expires),
    )
    conn.execute(
        "UPDATE work_item SET status='in_progress', row_version=row_version+1, updated_at=? WHERE id=?",
        (now, work["id"]),
    )
    event(
        conn,
        project_id,
        "work_item_claimed",
        "work_item",
        work["id"],
        agent_id,
        {"label": work["label"], "expired_claims_reaped": expired_claim_count},
    )
    return one(conn, "SELECT * FROM work_item_claim WHERE id=?", (claim_id,))


def check_expected_version(row: sqlite3.Row, expected: int | None) -> None:
    if expected is not None and int(row["row_version"]) != expected:
        raise CommandError(f"Stale row version for {row['label']}: expected {expected}, current {row['row_version']}")


def render_dashboard(conn: sqlite3.Connection, config: RuntimeConfig) -> Path:
    project = require_project(conn)
    latest_event = one(conn, "SELECT COALESCE(MAX(id), 0) AS id FROM event_log WHERE project_id=?", (project["id"],))["id"]
    rows = all_rows(conn, "SELECT * FROM work_item WHERE project_id=? ORDER BY label", (project["id"],))
    impacts = all_rows(conn, "SELECT * FROM impact WHERE project_id=? AND status IN ('proposed','approved') ORDER BY label", (project["id"],))
    lines = [
        f"# {project['name']} State",
        "",
        f"- project: {project['label']}",
        f"- profile: {project['profile']}",
        f"- rendered_from_event_id: {latest_event}",
        "",
        "## Work Items",
        "",
    ]
    if not rows:
        lines.append("_No work items._")
    for row in rows:
        parent = ""
        if row["parent_work_item_id"]:
            prow = one(conn, "SELECT label FROM work_item WHERE id=?", (row["parent_work_item_id"],))
            parent = f" parent={prow['label']}" if prow else ""
        lines.append(
            f"- [{row['status']}] {row['label']} {row['title']} "
            f"(type={row['item_type']}, tag={row['tag'] or 'none'}, validity={row['validity_status']}, "
            f"row_version={row['row_version']}{parent})"
        )
    lines.extend(["", "## Open Impacts", ""])
    if not impacts:
        lines.append("_No proposed or approved impacts._")
    for impact in impacts:
        target = ""
        if impact["work_item_id"]:
            wi = one(conn, "SELECT label FROM work_item WHERE id=?", (impact["work_item_id"],))
            target = wi["label"] if wi else "unknown"
        elif impact["artifact_id"]:
            art = one(conn, "SELECT label FROM artifact WHERE id=?", (impact["artifact_id"],))
            target = art["label"] if art else "unknown"
        lines.append(f"- {impact['label']} {impact['status']} -> {target}: {impact['impact_type']} ({impact['invalidation_policy']})")
    path = dashboard_path(config)
    atomic_write(path, "\n".join(lines) + "\n")
    now = utc_now()
    conn.execute(
        """
        INSERT INTO render_state(project_id, output_path, rendered_from_event_id, rendered_at, updated_at)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(project_id, output_path) DO UPDATE SET
          rendered_from_event_id=excluded.rendered_from_event_id,
          rendered_at=excluded.rendered_at,
          updated_at=excluded.updated_at,
          row_version=render_state.row_version+1
        """,
        (project["id"], str(path), latest_event, now, now),
    )
    event(conn, project["id"], "dashboard_rendered", "render_state", str(path), detail={"event_id": latest_event})
    return path


def render_graph(conn: sqlite3.Connection, config: RuntimeConfig) -> Path:
    project = require_project(conn)
    lines = ["flowchart TD"]
    items = all_rows(conn, "SELECT * FROM work_item WHERE project_id=? ORDER BY label", (project["id"],))
    if not items:
        lines.append('  empty["No work items"]')
    for item in items:
        tag = f" / tag:{item['tag']}" if item["tag"] else ""
        label = f"{item['label']} {item['title']}\\n{item['status']} / {item['validity_status']}{tag}"
        lines.append(f'  {item["label"].replace("-", "_")}["{label}"]')
    deps = all_rows(conn, "SELECT * FROM work_dependency WHERE project_id=?", (project["id"],))
    for dep in deps:
        upstream = one(conn, "SELECT label FROM work_item WHERE id=?", (dep["upstream_work_item_id"],))
        downstream = one(conn, "SELECT label FROM work_item WHERE id=?", (dep["downstream_work_item_id"],))
        if upstream and downstream:
            lines.append(
                f'  {upstream["label"].replace("-", "_")} -->|{dep["invalidation_policy"]}| {downstream["label"].replace("-", "_")}'
            )
    path = graph_path(config)
    atomic_write(path, "\n".join(lines) + "\n")
    event(conn, project["id"], "graph_rendered", "render_state", str(path))
    return path


def load_template(config: RuntimeConfig, name: str | None) -> dict[str, Any]:
    if not name or not config.profile_config:
        return {}
    template_dir = config.profile_config.parent / "workflow-templates"
    return load_yaml(template_dir / f"{name}.yaml")


def initialize_from_template(conn: sqlite3.Connection, project: sqlite3.Row, config: RuntimeConfig, template_name: str | None) -> None:
    template = load_template(config, template_name)
    id_by_key: dict[str, str] = {}
    for spec in template.get("work_items", []):
        row = create_work(
            conn, project["id"], config.profile,
            title=spec["title"],
            item_type=spec.get("item_type", "task"),
            key=spec.get("key"),
            parent=spec.get("parent"),
            phase=spec.get("phase"),
            status=spec.get("status", "ready"),
            description=spec.get("description"),
            priority=int(spec.get("priority", 3)),
            tag=spec.get("tag"),
        )
        id_by_key[spec.get("key", row["work_item_key"])] = row["label"]
    for dep in template.get("dependencies", []):
        upstream = id_by_key.get(dep["upstream"], dep["upstream"])
        downstream = id_by_key.get(dep["downstream"], dep["downstream"])
        link_work_items(conn, project["id"], upstream, downstream, dep.get("policy", "mark_needs_review"))
    if template:
        event(conn, project["id"], "workflow_template_loaded", "project", project["id"], detail={"template": template_name})


def link_work_items(conn: sqlite3.Connection, project_id: str, upstream_label: str, downstream_label: str, policy: str) -> sqlite3.Row:
    if policy not in POLICY_SEVERITY:
        raise CommandError(f"Unsupported invalidation policy: {policy}")
    up_table, up = resolve_entity(conn, upstream_label)
    down_table, down = resolve_entity(conn, downstream_label)
    if up_table != "work_item" or down_table != "work_item":
        raise CommandError("Dependencies can only link work items")
    now = utc_now()
    dep_id = make_id()
    conn.execute(
        """
        INSERT INTO work_dependency(id, project_id, upstream_work_item_id, downstream_work_item_id, invalidation_policy, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(project_id, upstream_work_item_id, downstream_work_item_id) DO UPDATE SET
          invalidation_policy=excluded.invalidation_policy,
          row_version=work_dependency.row_version+1,
          updated_at=excluded.updated_at
        """,
        (dep_id, project_id, up["id"], down["id"], policy, now, now),
    )
    event(conn, project_id, "work_dependency_linked", "work_dependency", dep_id,
          detail={"upstream": up["label"], "downstream": down["label"], "policy": policy})
    return one(conn, "SELECT * FROM work_dependency WHERE project_id=? AND upstream_work_item_id=? AND downstream_work_item_id=?",
               (project_id, up["id"], down["id"]))


def downstream_impacts(conn: sqlite3.Connection, project_id: str, start_work_ids: list[str],
                       initial_policy: str = "mark_needs_review") -> dict[str, str]:
    result: dict[str, str] = {}
    queue: deque[tuple[str, str]] = deque((work_id, initial_policy) for work_id in start_work_ids)
    seen: set[tuple[str, str]] = set()
    while queue:
        work_id, incoming_policy = queue.popleft()
        if (work_id, incoming_policy) in seen:
            continue
        seen.add((work_id, incoming_policy))
        current = result.get(work_id, "none")
        if POLICY_SEVERITY[incoming_policy] > POLICY_SEVERITY[current]:
            result[work_id] = incoming_policy
        deps = all_rows(conn, "SELECT * FROM work_dependency WHERE project_id=? AND upstream_work_item_id=?",
                        (project_id, work_id))
        for dep in deps:
            edge_policy = dep["invalidation_policy"]
            next_policy = edge_policy if POLICY_SEVERITY[edge_policy] > POLICY_SEVERITY[incoming_policy] else incoming_policy
            queue.append((dep["downstream_work_item_id"], next_policy))
    return result


def generate_impacts(conn: sqlite3.Connection, project: sqlite3.Row, config: RuntimeConfig, version: sqlite3.Row) -> list[sqlite3.Row]:
    source = one(conn, "SELECT * FROM source_asset WHERE id=?", (version["source_asset_id"],))
    rules_dir = config.profile_config.parent / "impact-rules" if config.profile_config else None
    rules = load_yaml(rules_dir / "default.yaml") if rules_dir else {}
    matching_rules = [
        rule for rule in rules.get("source_rules", [])
        if rule.get("source_asset_type") in (source["asset_type"], "*")
    ]
    start_policy: dict[str, str] = {}
    for rule in matching_rules:
        types = set(rule.get("target_work_item_types", []))
        if types:
            placeholders = ",".join("?" for _ in types)
            rows = all_rows(
                conn,
                f"SELECT id FROM work_item WHERE project_id=? AND item_type IN ({placeholders})",
                (project["id"], *sorted(types)),
            )
        else:
            rows = all_rows(conn, "SELECT id FROM work_item WHERE project_id=?", (project["id"],))
        rule_policy = rule.get("policy", "mark_needs_review")
        for row in rows:
            current = start_policy.get(row["id"], "none")
            if POLICY_SEVERITY[rule_policy] > POLICY_SEVERITY[current]:
                start_policy[row["id"]] = rule_policy
    if not matching_rules:
        rows = all_rows(conn, "SELECT id FROM work_item WHERE project_id=? AND status!='complete'", (project["id"],))
        for row in rows:
            start_policy[row["id"]] = "mark_needs_review"
        matching_rules = [{"impact_type": "source_changed", "policy": "mark_needs_review", "confidence": "medium"}]

    policy_by_work: dict[str, str] = {}
    for work_id, direct_policy in sorted(start_policy.items()):
        propagated = downstream_impacts(conn, project["id"], [work_id], direct_policy)
        propagated[work_id] = direct_policy
        for target_id, target_policy in propagated.items():
            current = policy_by_work.get(target_id, "none")
            if POLICY_SEVERITY[target_policy] > POLICY_SEVERITY[current]:
                policy_by_work[target_id] = target_policy

    created: list[sqlite3.Row] = []
    now = utc_now()
    ordered_impacts: list[tuple[str, str, sqlite3.Row]] = []
    for work_id, policy in policy_by_work.items():
        wi = one(conn, "SELECT label, title FROM work_item WHERE id=?", (work_id,))
        if wi:
            ordered_impacts.append((work_id, policy, wi))
    for work_id, policy, wi in sorted(ordered_impacts, key=lambda item: item[2]["label"]):
        label = next_label(conn, project["id"], "impact", config.profile)
        impact_id = make_id()
        rule = matching_rules[0]
        conn.execute(
            """
            INSERT INTO impact(
              id, project_id, label, source_asset_version_id, work_item_id, impact_type,
              invalidation_policy, confidence, status, rationale, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'proposed', ?, ?, ?)
            """,
            (
                impact_id, project["id"], label, version["id"], work_id,
                rule.get("impact_type", "source_changed"), policy, rule.get("confidence", "medium"),
                f"{source['label']} {version['version_label']} may affect {wi['label']} {wi['title']}",
                now, now,
            ),
        )
        created.append(one(conn, "SELECT * FROM impact WHERE id=?", (impact_id,)))
    event(conn, project["id"], "impacts_proposed", "source_asset_version", version["id"],
          detail={"count": len(created), "source": source["label"], "version": version["label"]})
    return created


def build_context(conn: sqlite3.Connection, config: RuntimeConfig, work_label: str) -> Path:
    project = require_project(conn)
    table, work = resolve_entity(conn, work_label)
    if table != "work_item":
        raise CommandError("Context can only be built for a work item")
    latest_event = int(one(conn, "SELECT COALESCE(MAX(id), 0) AS id FROM event_log WHERE project_id=?", (project["id"],))["id"])
    path = context_dir(config) / f"{work['label']}.md"
    policy_path = ""
    if config.profile_config:
        candidate = config.profile_config.parent / "context-policies" / f"{work['item_type']}.yaml"
        if candidate.exists():
            policy_path = str(candidate)
    deps = all_rows(
        conn,
        """
        SELECT wi.* FROM work_dependency dep
        JOIN work_item wi ON wi.id = dep.upstream_work_item_id
        WHERE dep.downstream_work_item_id=?
        ORDER BY wi.label
        """,
        (work["id"],),
    )
    sources = all_rows(conn, "SELECT * FROM source_asset WHERE project_id=? ORDER BY label", (project["id"],))
    artifacts = all_rows(conn, "SELECT * FROM artifact WHERE project_id=? AND owner_work_item_id=? ORDER BY label",
                         (project["id"], work["id"]))
    lines = [
        "---",
        "context_pack:",
        f"  work_item: {work['label']}",
        f"  generated_from_event_id: {latest_event}",
        f"  generated_at: {utc_now()}",
        f"  policy: {policy_path}",
        "  policy_schema_version: 1",
        "---",
        "",
        f"# Context Pack: {work['label']} {work['title']}",
        "",
        "## Current Work Item",
        "",
        f"- status: {work['status']}",
        f"- validity_status: {work['validity_status']}",
        f"- row_version: {work['row_version']}",
        f"- type: {work['item_type']}",
        f"- tag: {work['tag'] or 'none'}",
        "",
        "## Upstream Dependencies",
        "",
    ]
    lines.extend([f"- {dep['label']} {dep['title']} ({dep['status']} / {dep['validity_status']})" for dep in deps] or ["_None._"])
    lines.extend(["", "## Source Assets", ""])
    lines.extend([f"- {src['label']} {src['title']} ({src['asset_type']})" for src in sources] or ["_None._"])
    lines.extend(["", "## Owned Artifacts", ""])
    lines.extend([f"- {art['label']} {art['title']} -> {art['path'] or '(no path)'}" for art in artifacts] or ["_None._"])
    atomic_write(path, "\n".join(lines) + "\n")
    event(conn, project["id"], "context_pack_built", "work_item", work["id"], detail={"path": str(path), "event_id": latest_event})
    return path


def show_context(conn: sqlite3.Connection, config: RuntimeConfig, work_label: str) -> str:
    project = require_project(conn)
    _, work = resolve_entity(conn, work_label)
    path = context_dir(config) / f"{work['label']}.md"
    latest_event = int(one(
        conn,
        "SELECT COALESCE(MAX(id), 0) AS id FROM event_log WHERE project_id=? AND event_type != 'context_pack_built'",
        (project["id"],),
    )["id"])
    if not path.exists():
        return f"Context pack missing for {work['label']}: {path}"
    text = path.read_text(encoding="utf-8")
    match = re.search(r"generated_from_event_id:\s*(\d+)", text)
    generated = int(match.group(1)) if match else -1
    status = "current" if generated >= latest_event else f"stale (generated {generated}, latest {latest_event})"
    return f"{path}\nstatus: {status}"


def validate_db(conn: sqlite3.Connection, strict: bool = False) -> list[str]:
    issues: list[str] = []
    required_tables = [
        "project", "work_item", "work_dependency", "source_asset", "source_asset_version",
        "artifact", "artifact_version", "artifact_source", "impact", "work_item_claim",
        "event_log", "render_state",
    ]
    existing = {row["name"] for row in all_rows(conn, "SELECT name FROM sqlite_master WHERE type='table'")}
    for table in required_tables:
        if table not in existing:
            issues.append(f"missing table: {table}")
    if issues:
        return issues
    for row in all_rows(conn, "SELECT label FROM impact WHERE work_item_id IS NULL AND artifact_id IS NULL"):
        issues.append(f"impact has no target: {row['label']}")
    for row in all_rows(conn, "SELECT work_item_id, COUNT(*) c FROM work_item_claim WHERE status='active' GROUP BY work_item_id HAVING c > 1"):
        issues.append(f"multiple active claims for work_item_id {row['work_item_id']}")
    if strict:
        for row in all_rows(conn, """
            SELECT wi.label FROM work_item wi
            WHERE wi.status = 'in_progress'
            AND NOT EXISTS (
                SELECT 1 FROM work_item_claim c
                WHERE c.work_item_id = wi.id AND c.status = 'active'
            )
        """):
            issues.append(f"work item in_progress with no active claim: {row['label']}")
        now = utc_now()
        for row in all_rows(conn, """
            SELECT wi.label FROM work_item_claim c
            JOIN work_item wi ON wi.id = c.work_item_id
            WHERE c.status = 'active' AND c.expires_at <= ?
        """, (now,)):
            issues.append(f"expired active claim on {row['label']}")
    return issues


def print_row(row: sqlite3.Row) -> None:
    print(json.dumps(dict(row), indent=2, sort_keys=True))


def cmd_init(args: argparse.Namespace, config: RuntimeConfig) -> None:
    conn = connect(config.db_path)
    with transaction(conn):
        execute_schema(conn)
        existing = one(conn, "SELECT * FROM project ORDER BY created_at LIMIT 1")
        if existing:
            project = existing
            print(f"Project already initialized: {project['label']} ({config.db_path})")
            return
        for key in ("tmp", "inputs", "outputs", "context_packs", "impact_reports"):
            paths = config.profile_data.get("paths", {})
            if key in paths:
                resolve_path(config, paths[key]).mkdir(parents=True, exist_ok=True)
        project = create_project(conn, config, args.name or config.profile_data.get("name", "Agent State Project"))
        initialize_from_template(conn, project, config, getattr(args, "template", None))
        render_dashboard(conn, config)
    print(f"Initialized {project['label']} at {config.db_path}")


def cmd_create_work(args: argparse.Namespace, config: RuntimeConfig) -> None:
    conn = connect(config.db_path)
    with transaction(conn):
        project = require_project(conn)
        row = create_work(
            conn,
            project["id"],
            project["profile"],
            args.title,
            args.type,
            args.key,
            args.parent,
            args.phase,
            args.status,
            args.description,
            args.priority,
            getattr(args, "source_work_item", None),
            getattr(args, "tag", None),
        )
    print_row(row)


def load_children_specs(path: Path) -> list[dict[str, Any]]:
    data = load_yaml(path) if path.suffix.lower() in {".yaml", ".yml"} else json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and "children" in data:
        data = data["children"]
    if not isinstance(data, list):
        raise CommandError("add-children expects a YAML/JSON list or an object with a children list")
    specs: list[dict[str, Any]] = []
    for index, item in enumerate(data, start=1):
        if not isinstance(item, dict):
            raise CommandError(f"Child spec {index} must be a mapping")
        if not item.get("title"):
            raise CommandError(f"Child spec {index} is missing title")
        specs.append(item)
    return specs


def cmd_add_children(args: argparse.Namespace, config: RuntimeConfig) -> None:
    conn = connect(config.db_path)
    specs = load_children_specs(resolve_path(config, args.file))
    created: list[sqlite3.Row] = []
    with transaction(conn):
        project = require_project(conn)
        for spec in specs:
            row = create_work(
                conn,
                project["id"],
                project["profile"],
                str(spec["title"]),
                str(spec.get("type", spec.get("item_type", args.type))),
                spec.get("key"),
                args.parent,
                spec.get("phase", args.phase),
                str(spec.get("status", args.status)),
                spec.get("description"),
                int(spec.get("priority", args.priority)),
                args.source_work_item,
                spec.get("tag", args.tag),
            )
            created.append(row)
            for dep in spec.get("dependencies", []):
                if not isinstance(dep, dict):
                    raise CommandError(f"dependencies for {row['label']} must be mappings")
                if dep.get("upstream"):
                    link_work_items(conn, project["id"], str(dep["upstream"]), row["label"], dep.get("policy", "mark_needs_review"))
                if dep.get("downstream"):
                    link_work_items(conn, project["id"], row["label"], str(dep["downstream"]), dep.get("policy", "mark_needs_review"))
        event(
            conn,
            project["id"],
            "work_items_batch_created",
            "work_item",
            args.parent,
            detail={"count": len(created), "source_work_item": args.source_work_item},
        )
    for row in created:
        print(f"{row['label']} {row['title']}")


def cmd_create_source(args: argparse.Namespace, config: RuntimeConfig) -> None:
    conn = connect(config.db_path)
    with transaction(conn):
        project = require_project(conn)
        row = create_source(conn, project["id"], project["profile"], args.title, args.type, args.key, args.path, args.version_label, args.change_note)
    print_row(row)


def cmd_create_artifact(args: argparse.Namespace, config: RuntimeConfig) -> None:
    conn = connect(config.db_path)
    with transaction(conn):
        project = require_project(conn)
        row = create_artifact(conn, project["id"], project["profile"], args.title, args.type, args.owner, args.key, args.path)
    print_row(row)


def cmd_show(args: argparse.Namespace, config: RuntimeConfig) -> None:
    conn = connect(config.db_path)
    table, row = resolve_entity(conn, args.label)
    print_row(row)
    if args.children and table == "work_item":
        children = all_rows(conn, "SELECT * FROM work_item WHERE parent_work_item_id=? ORDER BY priority, label", (row["id"],))
        print("\nchildren:")
        for child in children:
            tag = f" tag={child['tag']}" if child["tag"] else ""
            print(f"- {child['label']} {child['status']} {child['validity_status']}{tag} {child['title']} row_version={child['row_version']}")


def cmd_list_projects(args: argparse.Namespace, config: RuntimeConfig) -> None:
    conn = connect(config.db_path)
    execute_schema(conn)
    projects = all_rows(conn, "SELECT * FROM project ORDER BY created_at, label")
    if not projects:
        print(f"No projects found in {config.db_path}")
        return
    for project in projects:
        print(
            f"{project['label']}  {project['name']}  "
            f"profile={project['profile']}  db={config.db_path}"
        )


def cmd_next(args: argparse.Namespace, config: RuntimeConfig) -> None:
    conn = connect(config.db_path)
    table, parent = resolve_entity(conn, args.label)
    if table != "work_item":
        raise CommandError("next requires a parent work item")
    children = all_rows(conn, "SELECT * FROM work_item WHERE parent_work_item_id=? AND status NOT IN ('complete','cancelled') ORDER BY priority, label", (parent["id"],))
    for child in children:
        blockers = incomplete_upstream_blockers(conn, child["id"])
        if not blockers and child["validity_status"] in ("current", "needs_review", "outdated"):
            print_row(child)
            return
    print("No ready child work item")


def cmd_claim_next(args: argparse.Namespace, config: RuntimeConfig) -> None:
    if args.limit < 1:
        raise CommandError("--limit must be at least 1")
    if args.agent_id and args.limit != 1:
        raise CommandError("--agent-id can only be used when --limit is 1")
    conn = connect(config.db_path)
    claimed: list[dict[str, Any]] = []
    with transaction(conn):
        project = require_project(conn)
        expired = expire_claims(conn, project["id"])
        table, parent = resolve_entity(conn, args.parent)
        if table != "work_item":
            raise CommandError("claim-next requires a parent work item")
        tag_filter = ""
        params: list[Any] = [parent["id"]]
        if args.tag:
            tag_filter = "AND tag=?"
            params.append(args.tag)
        children = all_rows(
            conn,
            f"""
            SELECT * FROM work_item
            WHERE parent_work_item_id=?
              AND status IN ('not_started','ready','needs_review')
              AND validity_status IN ('current','needs_review','outdated')
              {tag_filter}
            ORDER BY priority, label
            """,
            tuple(params),
        )
        next_agent_index = args.start_index
        for child in children:
            if len(claimed) >= args.limit:
                break
            if active_claim(conn, child["id"]):
                continue
            if incomplete_upstream_blockers(conn, child["id"]):
                continue
            agent_id = args.agent_id or f"{args.agent_id_prefix}-{next_agent_index}"
            claim = claim_work_item(
                conn,
                project["id"],
                child,
                agent_id,
                args.lease_minutes,
                len(expired),
            )
            claimed.append(
                {
                    "work_item_label": child["label"],
                    "work_item_title": child["title"],
                    "work_item_row_version": int(child["row_version"]) + 1,
                    "tag": child["tag"],
                    "agent_id": agent_id,
                    "claim_id": claim["id"],
                    "expires_at": claim["expires_at"],
                }
            )
            next_agent_index += 1
        event(
            conn,
            project["id"],
            "work_items_batch_claimed",
            "work_item",
            parent["id"],
            detail={"parent": parent["label"], "count": len(claimed), "limit": args.limit, "tag": args.tag},
        )
    print(json.dumps(claimed, indent=2, sort_keys=True))


def cmd_link(args: argparse.Namespace, config: RuntimeConfig) -> None:
    conn = connect(config.db_path)
    with transaction(conn):
        project = require_project(conn)
        row = link_work_items(conn, project["id"], args.upstream, args.downstream, args.policy)
    print_row(row)


def cmd_claim(args: argparse.Namespace, config: RuntimeConfig) -> None:
    conn = connect(config.db_path)
    with transaction(conn):
        project = require_project(conn)
        expired = expire_claims(conn, project["id"])
        table, work = resolve_entity(conn, args.label)
        if table != "work_item":
            raise CommandError("claim requires a work item")
        check_expected_version(work, args.expected_row_version)
        if active_claim(conn, work["id"]):
            raise CommandError(f"{work['label']} already has an active claim")
        blockers = incomplete_upstream_blockers(conn, work["id"])
        if blockers:
            labels = ", ".join(row["label"] for row in blockers)
            raise CommandError(f"{work['label']} is blocked by incomplete upstream work items: {labels}")
        row = claim_work_item(conn, project["id"], work, args.agent_id, args.lease_minutes, len(expired))
    print_row(row)


def cmd_expire_claims(args: argparse.Namespace, config: RuntimeConfig) -> None:
    conn = connect(config.db_path)
    with transaction(conn):
        project = require_project(conn)
        expired = expire_claims(conn, project["id"], args.now)
    print(f"Expired {len(expired)} claim(s)")


def cmd_release(args: argparse.Namespace, config: RuntimeConfig) -> None:
    conn = connect(config.db_path)
    with transaction(conn):
        project = require_project(conn)
        _, work = resolve_entity(conn, args.label)
        claim = active_claim(conn, work["id"], args.agent_id)
        if not claim:
            raise CommandError(f"No active claim for {work['label']} by {args.agent_id}")
        now = utc_now()
        conn.execute("UPDATE work_item_claim SET status='released', released_at=?, release_reason=?, row_version=row_version+1 WHERE id=?",
                     (now, args.reason, claim["id"]))
        conn.execute("UPDATE work_item SET status='ready', row_version=row_version+1, updated_at=? WHERE id=? AND status='in_progress'",
                     (now, work["id"]))
        event(conn, project["id"], "work_item_released", "work_item", work["id"], args.agent_id)
    print(f"Released {work['label']}")


def cmd_heartbeat(args: argparse.Namespace, config: RuntimeConfig) -> None:
    conn = connect(config.db_path)
    with transaction(conn):
        project = require_project(conn)
        _, work = resolve_entity(conn, args.label)
        claim = active_claim(conn, work["id"], args.agent_id)
        if not claim:
            raise CommandError(f"No active claim for {work['label']} by {args.agent_id}")
        now_dt = datetime.now(UTC).replace(microsecond=0)
        expires = now_dt + timedelta(minutes=args.lease_minutes)
        conn.execute("UPDATE work_item_claim SET heartbeat_at=?, expires_at=?, row_version=row_version+1 WHERE id=?",
                     (now_dt.isoformat().replace("+00:00", "Z"), expires.isoformat().replace("+00:00", "Z"), claim["id"]))
        event(conn, project["id"], "work_item_heartbeat", "work_item", work["id"], args.agent_id)
    print(f"Heartbeat updated for {work['label']}")


def cmd_complete(args: argparse.Namespace, config: RuntimeConfig) -> None:
    conn = connect(config.db_path)
    with transaction(conn):
        project = require_project(conn)
        _, work = resolve_entity(conn, args.label)
        check_expected_version(work, args.expected_row_version)
        claim = active_claim(conn, work["id"], args.agent_id)
        if not claim:
            raise CommandError(f"No active claim for {work['label']} by {args.agent_id}")
        now = utc_now()
        conn.execute(
            "UPDATE work_item SET status='complete', completed_at=?, row_version=row_version+1, updated_at=? WHERE id=?",
            (now, now, work["id"]),
        )
        conn.execute("UPDATE work_item_claim SET status='released', released_at=?, release_reason='completed', row_version=row_version+1 WHERE id=?",
                     (now, claim["id"]))
        event(conn, project["id"], "work_item_completed", "work_item", work["id"], args.agent_id, {"summary": args.summary})
    print(f"Completed {work['label']}")


def cmd_revise_source(args: argparse.Namespace, config: RuntimeConfig) -> None:
    conn = connect(config.db_path)
    with transaction(conn):
        project = require_project(conn)
        table, source = resolve_entity(conn, args.label)
        if table != "source_asset":
            raise CommandError("revise-source requires a source asset")
        version = add_source_version(conn, project["id"], project["profile"], source["id"], args.path, args.version_label, args.change_note)
        impacts = generate_impacts(conn, project, config, version)
        report = impact_dir(config) / f"{version['label']}-impacts.md"
        lines = [f"# Impact Report: {version['label']}", "", f"Source: {source['label']} {source['title']}", ""]
        for impact in impacts:
            target = one(conn, "SELECT label, title FROM work_item WHERE id=?", (impact["work_item_id"],))
            lines.append(f"- {impact['label']} -> {target['label']} {target['title']}: {impact['invalidation_policy']} ({impact['confidence']})")
        atomic_write(report, "\n".join(lines) + "\n")
        event(conn, project["id"], "source_revised", "source_asset_version", version["id"], detail={"report": str(report)})
    print_row(version)
    print(f"Impact report: {report}")


def cmd_review_impacts(args: argparse.Namespace, config: RuntimeConfig) -> None:
    conn = connect(config.db_path)
    table, version = resolve_entity(conn, args.label)
    if table != "source_asset_version":
        raise CommandError("review-impacts requires a source asset version")
    impacts = all_rows(conn, "SELECT * FROM impact WHERE source_asset_version_id=? ORDER BY label", (version["id"],))
    for impact in impacts:
        print_row(impact)


def cmd_approve_impact(args: argparse.Namespace, config: RuntimeConfig) -> None:
    update_impact_status(args, config, "approved")


def cmd_reject_impact(args: argparse.Namespace, config: RuntimeConfig) -> None:
    update_impact_status(args, config, "rejected")


def update_impact_status(args: argparse.Namespace, config: RuntimeConfig, status: str) -> None:
    conn = connect(config.db_path)
    with transaction(conn):
        project = require_project(conn)
        table, impact = resolve_entity(conn, args.label)
        if table != "impact":
            raise CommandError("Expected impact label")
        now = utc_now()
        conn.execute(
            "UPDATE impact SET status=?, reviewed_by=?, reviewed_at=?, review_note=?, row_version=row_version+1, updated_at=? WHERE id=?",
            (status, args.reviewed_by, now, getattr(args, "reason", None), now, impact["id"]),
        )
        event(conn, project["id"], f"impact_{status}", "impact", impact["id"], args.reviewed_by)
    print(f"{status}: {impact['label']}")


def cmd_apply_impacts(args: argparse.Namespace, config: RuntimeConfig) -> None:
    conn = connect(config.db_path)
    with transaction(conn):
        project = require_project(conn)
        table, version = resolve_entity(conn, args.label)
        if table != "source_asset_version":
            raise CommandError("apply-approved-impacts requires a source asset version")
        impacts = all_rows(conn, "SELECT * FROM impact WHERE source_asset_version_id=? AND status='approved'", (version["id"],))
        now = utc_now()
        for impact in impacts:
            if impact["work_item_id"] and impact["invalidation_policy"] != "none":
                validity = POLICY_TO_VALIDITY[impact["invalidation_policy"]]
                conn.execute(
                    "UPDATE work_item SET validity_status=?, row_version=row_version+1, updated_at=? WHERE id=?",
                    (validity, now, impact["work_item_id"]),
                )
            conn.execute("UPDATE impact SET status='applied', row_version=row_version+1, updated_at=? WHERE id=?", (now, impact["id"]))
        event(conn, project["id"], "approved_impacts_applied", "source_asset_version", version["id"], detail={"count": len(impacts)})
    print(f"Applied {len(impacts)} approved impacts")


def cmd_context(args: argparse.Namespace, config: RuntimeConfig) -> None:
    conn = connect(config.db_path)
    if args.context_command == "build":
        with transaction(conn):
            path = build_context(conn, config, args.work_item)
        print(path)
    elif args.context_command == "show":
        print(show_context(conn, config, args.label))


def cmd_render(args: argparse.Namespace, config: RuntimeConfig) -> None:
    conn = connect(config.db_path)
    with transaction(conn):
        path = render_dashboard(conn, config)
    print(path)


def cmd_render_graph(args: argparse.Namespace, config: RuntimeConfig) -> None:
    conn = connect(config.db_path)
    with transaction(conn):
        path = render_graph(conn, config)
    print(path)


def cmd_validate(args: argparse.Namespace, config: RuntimeConfig) -> None:
    conn = connect(config.db_path)
    execute_schema(conn)
    issues = validate_db(conn, strict=args.strict)
    if issues:
        for issue in issues:
            print(f"ERROR: {issue}", file=sys.stderr)
        raise CommandError(f"Validation failed with {len(issues)} issue(s)")
    print("Validation OK")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="agent_state.py")
    parser.add_argument("--db")
    parser.add_argument("--profile", default="generic")
    parser.add_argument("--profile-config")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("init")
    p.add_argument("--name")
    p.add_argument("--template")
    p.set_defaults(func=cmd_init)

    p = sub.add_parser("create-work")
    p.add_argument("title")
    p.add_argument("--type", default="task")
    p.add_argument("--key")
    p.add_argument("--parent")
    p.add_argument("--phase")
    p.add_argument("--tag")
    p.add_argument("--status", default="ready")
    p.add_argument("--description")
    p.add_argument("--priority", type=int, default=3)
    p.add_argument("--source-work-item")
    p.set_defaults(func=cmd_create_work)

    p = sub.add_parser("add-child")
    p.add_argument("parent")
    p.add_argument("title")
    p.add_argument("--type", default="task")
    p.add_argument("--key")
    p.add_argument("--phase")
    p.add_argument("--tag")
    p.add_argument("--status", default="ready")
    p.add_argument("--description")
    p.add_argument("--priority", type=int, default=3)
    p.add_argument("--source-work-item")
    p.set_defaults(func=cmd_create_work)

    p = sub.add_parser("add-children")
    p.add_argument("parent")
    p.add_argument("--file", required=True)
    p.add_argument("--type", default="task")
    p.add_argument("--phase")
    p.add_argument("--tag")
    p.add_argument("--status", default="ready")
    p.add_argument("--priority", type=int, default=3)
    p.add_argument("--source-work-item")
    p.set_defaults(func=cmd_add_children)

    p = sub.add_parser("create-source")
    p.add_argument("title")
    p.add_argument("--type", default="document")
    p.add_argument("--key")
    p.add_argument("--path")
    p.add_argument("--version-label", default="v1")
    p.add_argument("--change-note")
    p.set_defaults(func=cmd_create_source)

    p = sub.add_parser("create-artifact")
    p.add_argument("title")
    p.add_argument("--type", default="artifact")
    p.add_argument("--owner", required=True)
    p.add_argument("--key")
    p.add_argument("--path")
    p.set_defaults(func=cmd_create_artifact)

    p = sub.add_parser("show")
    p.add_argument("label")
    p.add_argument("--children", action="store_true")
    p.set_defaults(func=cmd_show)

    p = sub.add_parser("list-projects")
    p.set_defaults(func=cmd_list_projects)

    p = sub.add_parser("next")
    p.add_argument("label")
    p.set_defaults(func=cmd_next)

    p = sub.add_parser("link")
    p.add_argument("upstream")
    p.add_argument("downstream")
    p.add_argument("--policy", default="mark_needs_review", choices=sorted(POLICY_SEVERITY))
    p.set_defaults(func=cmd_link)

    p = sub.add_parser("claim")
    p.add_argument("label")
    p.add_argument("--agent-id", required=True)
    p.add_argument("--expected-row-version", type=int)
    p.add_argument("--lease-minutes", type=int, default=60)
    p.set_defaults(func=cmd_claim)

    p = sub.add_parser("claim-next")
    p.add_argument("parent")
    p.add_argument("--limit", type=int, default=1)
    p.add_argument("--agent-id")
    p.add_argument("--agent-id-prefix", default="agent")
    p.add_argument("--start-index", type=int, default=1)
    p.add_argument("--tag")
    p.add_argument("--lease-minutes", type=int, default=60)
    p.set_defaults(func=cmd_claim_next)

    p = sub.add_parser("expire-claims")
    p.add_argument("--now")
    p.set_defaults(func=cmd_expire_claims)

    p = sub.add_parser("heartbeat")
    p.add_argument("label")
    p.add_argument("--agent-id", required=True)
    p.add_argument("--lease-minutes", type=int, default=60)
    p.set_defaults(func=cmd_heartbeat)

    p = sub.add_parser("release")
    p.add_argument("label")
    p.add_argument("--agent-id", required=True)
    p.add_argument("--reason", default="released")
    p.set_defaults(func=cmd_release)

    p = sub.add_parser("complete")
    p.add_argument("label")
    p.add_argument("--agent-id", required=True)
    p.add_argument("--expected-row-version", type=int)
    p.add_argument("--summary")
    p.set_defaults(func=cmd_complete)

    p = sub.add_parser("revise-source")
    p.add_argument("label")
    p.add_argument("--path", required=True)
    p.add_argument("--version-label", required=True)
    p.add_argument("--change-note")
    p.set_defaults(func=cmd_revise_source)

    p = sub.add_parser("review-impacts")
    p.add_argument("label")
    p.set_defaults(func=cmd_review_impacts)

    p = sub.add_parser("approve-impact")
    p.add_argument("label")
    p.add_argument("--reviewed-by", required=True)
    p.set_defaults(func=cmd_approve_impact)

    p = sub.add_parser("reject-impact")
    p.add_argument("label")
    p.add_argument("--reviewed-by", required=True)
    p.add_argument("--reason")
    p.set_defaults(func=cmd_reject_impact)

    p = sub.add_parser("apply-approved-impacts")
    p.add_argument("label")
    p.set_defaults(func=cmd_apply_impacts)

    p = sub.add_parser("context")
    ctx_sub = p.add_subparsers(dest="context_command", required=True)
    cp = ctx_sub.add_parser("build")
    cp.add_argument("--work-item", required=True)
    sp = ctx_sub.add_parser("show")
    sp.add_argument("label")
    p.set_defaults(func=cmd_context)

    p = sub.add_parser("render")
    p.set_defaults(func=cmd_render)

    p = sub.add_parser("render-graph")
    p.add_argument("--template")
    p.set_defaults(func=cmd_render_graph)

    p = sub.add_parser("validate")
    p.add_argument("--strict", action="store_true")
    p.set_defaults(func=cmd_validate)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    config = load_profile_config(args, Path.cwd())
    try:
        args.func(args, config)
    except CommandError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    except sqlite3.IntegrityError as exc:
        print(f"ERROR: database constraint failed: {exc}", file=sys.stderr)
        return 2
    return 0
