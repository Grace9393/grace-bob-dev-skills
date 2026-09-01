from __future__ import annotations

import json
import sqlite3
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
ENGINE_STATE = REPO / "skills" / "agent-state-engine" / "scripts" / "agent_state.py"
BID_STATE = REPO / "skills" / "ibm-bid-navigator" / "scripts" / "bid_state.py"
sys.path.insert(0, str(REPO / "skills" / "agent-state-engine" / "scripts"))

from agent_state.cli import execute_schema  # noqa: E402


def run_script(script: Path, cwd: Path, *args: str, expect_ok: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        [sys.executable, str(script), *args],
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )
    if expect_ok and result.returncode != 0:
        raise AssertionError(f"command failed: {args}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}")
    if not expect_ok and result.returncode == 0:
        raise AssertionError(f"command unexpectedly succeeded: {args}\nstdout:\n{result.stdout}")
    return result


def run_cmd(cwd: Path, *args: str, expect_ok: bool = True) -> subprocess.CompletedProcess[str]:
    return run_script(BID_STATE, cwd, *args, expect_ok=expect_ok)


def run_engine(cwd: Path, *args: str, expect_ok: bool = True) -> subprocess.CompletedProcess[str]:
    return run_script(ENGINE_STATE, cwd, *args, expect_ok=expect_ok)


def db(cwd: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(cwd / "tmp" / "ibm-bid-project.sqlite")
    conn.row_factory = sqlite3.Row
    return conn


def engine_db(cwd: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(cwd / "tmp" / "agent-state.sqlite")
    conn.row_factory = sqlite3.Row
    return conn


def init_bid_project(cwd: Path) -> None:
    run_cmd(cwd, "init")
    run_cmd(cwd, "create-work", "Bid lifecycle", "--type", "operation", "--key", "bid_lifecycle", "--priority", "1")
    children = [
        ("Requirements analysis", "requirement", "requirements_analysis", "opportunity_assessment", "1", "ibm-bid-requirements-analysis"),
        ("Strategic positioning", "skill_task", "strategic_positioning", "strategic_positioning", "2", "ibm-bid-strategic-positioning"),
        ("Pricing strategy", "skill_task", "pricing_strategy", "strategic_positioning", "3", "ibm-bid-pricing-strategy"),
        ("Solution architecture", "skill_task", "solution_architecture", "solution_architecture", "4", "ibm-bid-solution-architect"),
        ("Answer drafting", "answer", "answer_drafting", "content_development", "5", "ibm-bid-writer"),
        ("Fact check", "review", "fact_check", "technical_assurance", "6", "ibm-bid-fact-checker"),
    ]
    for title, item_type, key, phase, priority, tag in children:
        run_cmd(
            cwd,
            "add-child",
            "WI-0001",
            title,
            "--type",
            item_type,
            "--key",
            key,
            "--phase",
            phase,
            "--priority",
            priority,
            "--tag",
            tag,
        )
    run_cmd(cwd, "link", "WI-0002", "WI-0003", "--policy", "mark_outdated")
    run_cmd(cwd, "link", "WI-0002", "WI-0004", "--policy", "mark_outdated")
    run_cmd(cwd, "link", "WI-0002", "WI-0005", "--policy", "block_until_refreshed")
    run_cmd(cwd, "link", "WI-0003", "WI-0006", "--policy", "mark_needs_review")
    run_cmd(cwd, "link", "WI-0004", "WI-0006", "--policy", "mark_outdated")
    run_cmd(cwd, "link", "WI-0005", "WI-0006", "--policy", "block_until_refreshed")
    run_cmd(cwd, "link", "WI-0006", "WI-0007", "--policy", "mark_needs_review")


def test_bid_state_init_creates_project_work_items_and_dashboard(tmp_path: Path) -> None:
    init_bid_project(tmp_path)
    run_cmd(tmp_path, "validate", "--strict")

    conn = db(tmp_path)
    assert conn.execute("SELECT COUNT(*) FROM project").fetchone()[0] == 1
    assert conn.execute("SELECT COUNT(*) FROM work_item").fetchone()[0] == 7
    assert conn.execute("SELECT COUNT(*) FROM work_dependency").fetchone()[0] == 7
    assert (tmp_path / "tmp" / "ibm-bid-project.md").exists()


def test_bid_state_accepts_bid_friendly_create_source_options(tmp_path: Path) -> None:
    run_cmd(tmp_path, "init")
    source = tmp_path / "inputs" / "client_docs" / "itt.md"
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_text("ITT content", encoding="utf-8")

    run_cmd(
        tmp_path,
        "create-source",
        "--path",
        str(source),
        "--title",
        "Ofgem xRM/CRM Salesforce SI ITT",
        "--doc-type",
        "ITT",
        "--purpose",
        "Primary procurement document",
    )

    conn = db(tmp_path)
    row = conn.execute("SELECT title, asset_type FROM source_asset WHERE label='DOC-0001'").fetchone()
    version = conn.execute("SELECT change_note FROM source_asset_version WHERE label='DOCV-0001'").fetchone()
    assert row["title"] == "Ofgem xRM/CRM Salesforce SI ITT"
    assert row["asset_type"] == "ITT"
    assert version["change_note"] == "Primary procurement document"


def test_bid_state_list_assets_lists_registered_sources(tmp_path: Path) -> None:
    run_cmd(tmp_path, "init")
    source = tmp_path / "inputs" / "client_docs" / "itt.md"
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_text("ITT content", encoding="utf-8")
    run_cmd(tmp_path, "create-source", "Client ITT", "--type", "ITT", "--path", str(source), "--version-label", "v1")

    result = run_cmd(tmp_path, "list-assets")

    assert "DOC-0001 ITT Client ITT" in result.stdout
    assert str(source) in result.stdout


def test_bid_state_list_assets_supports_json(tmp_path: Path) -> None:
    run_cmd(tmp_path, "init")
    source = tmp_path / "inputs" / "client_docs" / "itt.md"
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_text("ITT content", encoding="utf-8")
    run_cmd(tmp_path, "create-source", "Client ITT", "--type", "ITT", "--path", str(source), "--version-label", "v1")

    result = run_cmd(tmp_path, "list-assets", "--json")
    assets = json.loads(result.stdout)

    assert assets[0]["label"] == "DOC-0001"
    assert assets[0]["asset_type"] == "ITT"
    assert assets[0]["title"] == "Client ITT"


def test_bid_state_context_without_subcommand_lists_targets(tmp_path: Path) -> None:
    run_cmd(tmp_path, "init")
    run_cmd(tmp_path, "create-work", "Requirements Analysis", "--type", "task", "--key", "requirements_analysis")

    result = run_cmd(tmp_path, "context")

    assert "Available context targets:" in result.stdout
    assert "WI-0001 ready current Requirements Analysis" in result.stdout
    assert "bid_state.py context build --work-item WI-0001" in result.stdout


def test_bid_state_context_shortcuts_show_and_build(tmp_path: Path) -> None:
    run_cmd(tmp_path, "init")
    run_cmd(tmp_path, "create-work", "Requirements Analysis", "--type", "task", "--key", "requirements_analysis")

    missing = run_cmd(tmp_path, "context", "WI-0001")
    assert "Context pack missing for WI-0001" in missing.stdout

    built = run_cmd(tmp_path, "context", "build", "WI-0001")
    assert "WI-0001.md" in built.stdout

    shown = run_cmd(tmp_path, "context", "WI-0001")
    assert "WI-0001.md" in shown.stdout
    assert "status: current" in shown.stdout


def test_bid_state_context_summary_supports_json(tmp_path: Path) -> None:
    run_cmd(tmp_path, "init")
    run_cmd(tmp_path, "create-work", "Requirements Analysis", "--type", "task", "--key", "requirements_analysis")

    result = run_cmd(tmp_path, "context", "--json")
    items = json.loads(result.stdout)

    assert items[0]["label"] == "WI-0001"
    assert items[0]["context_exists"] is False


def test_bid_state_add_children_accepts_titles_shortcut(tmp_path: Path) -> None:
    run_cmd(tmp_path, "init")
    run_cmd(tmp_path, "create-work", "Phase 0", "--type", "phase", "--key", "phase_0")

    run_cmd(
        tmp_path,
        "add-children",
        "WI-0001",
        "--titles",
        "Requirements Analysis",
        "Hot Buttons Extraction",
        "Strategic Positioning",
        "--type",
        "skill_task",
        "--tag",
        "ibm-bid-navigator",
    )

    conn = db(tmp_path)
    rows = conn.execute("SELECT title, item_type, tag FROM work_item WHERE parent_work_item_id IS NOT NULL ORDER BY label").fetchall()
    assert [row["title"] for row in rows] == [
        "Requirements Analysis",
        "Hot Buttons Extraction",
        "Strategic Positioning",
    ]
    assert {row["item_type"] for row in rows} == {"skill_task"}
    assert {row["tag"] for row in rows} == {"ibm-bid-navigator"}


def test_bid_state_claim_uses_default_agent_id_when_omitted(tmp_path: Path) -> None:
    run_cmd(tmp_path, "init")
    run_cmd(tmp_path, "create-work", "Requirements Analysis", "--type", "task", "--key", "requirements_analysis")

    run_cmd(tmp_path, "claim", "WI-0001")

    conn = db(tmp_path)
    claim = conn.execute("SELECT agent_id, status FROM work_item_claim").fetchone()
    work = conn.execute("SELECT status FROM work_item WHERE label='WI-0001'").fetchone()
    assert claim["agent_id"] == "bid-navigator-agent"
    assert claim["status"] == "active"
    assert work["status"] == "in_progress"


def test_bid_state_claim_preserves_explicit_agent_id(tmp_path: Path) -> None:
    run_cmd(tmp_path, "init")
    run_cmd(tmp_path, "create-work", "Requirements Analysis", "--type", "task", "--key", "requirements_analysis")

    run_cmd(tmp_path, "claim", "WI-0001", "--agent-id", "cline")

    conn = db(tmp_path)
    claim = conn.execute("SELECT agent_id FROM work_item_claim").fetchone()
    assert claim["agent_id"] == "cline"


def test_agent_state_direct_generic_profile_init_render_and_validate(tmp_path: Path) -> None:
    run_engine(tmp_path, "--profile", "generic", "init", "--name", "Generic Project")
    listed = run_engine(tmp_path, "list-projects")
    assert "PRJ-0001  Generic Project  profile=generic" in listed.stdout
    run_engine(tmp_path, "create-work", "Parent workflow", "--type", "operation", "--key", "parent")
    run_engine(tmp_path, "add-child", "WI-0001", "Review requirement A", "--type", "review")
    run_engine(tmp_path, "render")
    run_engine(tmp_path, "validate", "--strict")

    conn = engine_db(tmp_path)
    project = conn.execute("SELECT profile, name FROM project").fetchone()
    assert project["profile"] == "generic"
    assert project["name"] == "Generic Project"
    render_state = conn.execute("SELECT rendered_at, updated_at FROM render_state").fetchone()
    assert render_state["rendered_at"]
    assert render_state["updated_at"]
    assert (tmp_path / "tmp" / "agent-state.md").exists()


def test_agent_state_direct_label_generation_after_9999(tmp_path: Path) -> None:
    run_engine(tmp_path, "--profile", "generic", "init")
    conn = engine_db(tmp_path)
    project_id = conn.execute("SELECT id FROM project").fetchone()["id"]
    now = "2026-05-05T00:00:00Z"
    conn.execute(
        """
        INSERT INTO work_item(
          id, project_id, label, work_item_key, item_type, title, status,
          validity_status, priority, created_at, updated_at
        )
        VALUES ('label-test', ?, 'WI-9999', 'label_test', 'task', 'Label test',
          'ready', 'current', 3, ?, ?)
        """,
        (project_id, now, now),
    )
    conn.commit()

    run_engine(tmp_path, "create-work", "After 9999", "--type", "task", "--key", "after_9999")
    row = conn.execute("SELECT label FROM work_item WHERE work_item_key='after_9999'").fetchone()
    assert row["label"] == "WI-10000"


def test_execute_schema_does_not_force_commit() -> None:
    conn = sqlite3.connect(":memory:")
    conn.execute("BEGIN")
    execute_schema(conn)
    conn.rollback()
    tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='project'").fetchall()
    assert tables == []


def test_schema_artifact_source_has_project_id() -> None:
    conn = sqlite3.connect(":memory:")
    execute_schema(conn)
    columns = {
        row[1]
        for row in conn.execute("PRAGMA table_info(artifact_source)").fetchall()
    }
    assert "project_id" in columns


def test_claim_blocks_second_agent_and_complete_requires_owner(tmp_path: Path) -> None:
    init_bid_project(tmp_path)
    run_cmd(tmp_path, "claim", "WI-0002", "--agent-id", "agent-1", "--expected-row-version", "1")

    second = run_cmd(
        tmp_path,
        "claim",
        "WI-0002",
        "--agent-id",
        "agent-2",
        "--expected-row-version",
        "2",
        expect_ok=False,
    )
    assert "already has an active claim" in second.stderr

    wrong_owner = run_cmd(
        tmp_path,
        "complete",
        "WI-0002",
        "--agent-id",
        "agent-2",
        "--expected-row-version",
        "2",
        expect_ok=False,
    )
    assert "No active claim" in wrong_owner.stderr

    run_cmd(tmp_path, "complete", "WI-0002", "--agent-id", "agent-1", "--expected-row-version", "2")
    conn = db(tmp_path)
    row = conn.execute("SELECT status FROM work_item WHERE label='WI-0002'").fetchone()
    assert row["status"] == "complete"
    active_claims = conn.execute("SELECT COUNT(*) FROM work_item_claim WHERE status='active'").fetchone()[0]
    assert active_claims == 0


def test_claim_blocked_by_incomplete_upstream(tmp_path: Path) -> None:
    run_engine(tmp_path, "--profile", "generic", "init", "--name", "Dep Test")
    run_engine(tmp_path, "create-work", "Step A", "--type", "task", "--key", "step_a")
    run_engine(tmp_path, "create-work", "Step B", "--type", "task", "--key", "step_b")
    run_engine(tmp_path, "link", "WI-0001", "WI-0002", "--policy", "mark_needs_review")

    blocked = run_engine(tmp_path, "claim", "WI-0002", "--agent-id", "agent-1", expect_ok=False)
    assert "blocked by incomplete upstream work items" in blocked.stderr
    assert "WI-0001" in blocked.stderr

    run_engine(tmp_path, "claim", "WI-0001", "--agent-id", "agent-1", "--expected-row-version", "1")
    run_engine(tmp_path, "complete", "WI-0001", "--agent-id", "agent-1", "--expected-row-version", "2", "--summary", "done")
    run_engine(tmp_path, "claim", "WI-0002", "--agent-id", "agent-1", "--expected-row-version", "1")

    conn = engine_db(tmp_path)
    assert conn.execute("SELECT status FROM work_item WHERE label='WI-0002'").fetchone()["status"] == "in_progress"


def test_heartbeat_renews_lease(tmp_path: Path) -> None:
    run_engine(tmp_path, "--profile", "generic", "init", "--name", "Heartbeat Test")
    run_engine(tmp_path, "create-work", "Long task", "--type", "task", "--key", "long_task")
    run_engine(tmp_path, "claim", "WI-0001", "--agent-id", "agent-1", "--expected-row-version", "1", "--lease-minutes", "60")

    conn = engine_db(tmp_path)
    before = conn.execute("SELECT expires_at, heartbeat_at FROM work_item_claim WHERE status='active'").fetchone()

    run_engine(tmp_path, "heartbeat", "WI-0001", "--agent-id", "agent-1", "--lease-minutes", "120")

    after = conn.execute("SELECT expires_at, heartbeat_at FROM work_item_claim WHERE status='active'").fetchone()
    assert after["expires_at"] > before["expires_at"]
    assert after["heartbeat_at"] >= before["heartbeat_at"]


def test_next_skips_blocked_until_refreshed_and_strict_validate_flags_zombie_claims(tmp_path: Path) -> None:
    run_engine(tmp_path, "--profile", "generic", "init", "--name", "Next Test")
    run_engine(tmp_path, "create-work", "Parent op", "--type", "operation", "--key", "parent_op")
    run_engine(tmp_path, "add-child", "WI-0001", "Hard blocked child", "--type", "task", "--key", "hard_blocked")
    run_engine(tmp_path, "add-child", "WI-0001", "Available child", "--type", "task", "--key", "available")

    conn = engine_db(tmp_path)
    conn.execute("UPDATE work_item SET validity_status='blocked_until_refreshed' WHERE work_item_key='hard_blocked'")
    conn.commit()

    result = run_engine(tmp_path, "next", "WI-0001")
    assert "available" in result.stdout
    assert "hard_blocked" not in result.stdout

    # --strict validate should flag expired active claims
    run_engine(tmp_path, "claim", "WI-0002", "--agent-id", "agent-1", "--expected-row-version", "1")
    conn.execute("UPDATE work_item_claim SET expires_at='2000-01-01T00:00:00Z' WHERE status='active'")
    conn.commit()
    result = run_engine(tmp_path, "validate", "--strict", expect_ok=False)
    assert "expired active claim" in result.stderr

    # --strict validate should flag in_progress with no active claim
    conn.execute("UPDATE work_item SET status='in_progress' WHERE label='WI-0003'")
    conn.execute("UPDATE work_item_claim SET status='released' WHERE status='active'")
    conn.commit()
    result = run_engine(tmp_path, "validate", "--strict", expect_ok=False)
    assert "in_progress with no active claim" in result.stderr


def test_claim_next_batches_ready_children_for_parallel_agents(tmp_path: Path) -> None:
    run_engine(tmp_path, "--profile", "generic", "init", "--name", "Claim Next Test")
    run_engine(tmp_path, "create-work", "Parent op", "--type", "operation", "--key", "parent_op")
    run_engine(tmp_path, "add-child", "WI-0001", "Ready A", "--type", "task", "--key", "ready_a", "--priority", "1")
    run_engine(tmp_path, "add-child", "WI-0001", "Ready B", "--type", "task", "--key", "ready_b", "--priority", "2")
    run_engine(tmp_path, "add-child", "WI-0001", "Ready C", "--type", "task", "--key", "ready_c", "--priority", "3")
    run_engine(tmp_path, "add-child", "WI-0001", "Blocked child", "--type", "task", "--key", "blocked_child", "--priority", "4")
    run_engine(tmp_path, "add-child", "WI-0001", "Dependent child", "--type", "task", "--key", "dependent_child", "--priority", "5")
    run_engine(tmp_path, "link", "WI-0002", "WI-0006")

    conn = engine_db(tmp_path)
    conn.execute("UPDATE work_item SET validity_status='blocked_until_refreshed' WHERE label='WI-0005'")
    conn.commit()

    result = run_engine(tmp_path, "claim-next", "WI-0001", "--limit", "3", "--agent-id-prefix", "subagent")
    claims = json.loads(result.stdout)
    assert [claim["work_item_label"] for claim in claims] == ["WI-0002", "WI-0003", "WI-0004"]
    assert [claim["agent_id"] for claim in claims] == ["subagent-1", "subagent-2", "subagent-3"]
    assert [claim["work_item_row_version"] for claim in claims] == [2, 2, 2]

    rows = conn.execute("SELECT label, status, row_version FROM work_item ORDER BY label").fetchall()
    state = {row["label"]: (row["status"], row["row_version"]) for row in rows}
    assert state["WI-0002"] == ("in_progress", 2)
    assert state["WI-0003"] == ("in_progress", 2)
    assert state["WI-0004"] == ("in_progress", 2)
    assert state["WI-0005"] == ("ready", 1)
    assert state["WI-0006"] == ("ready", 1)

    result = run_engine(tmp_path, "claim-next", "WI-0001", "--limit", "3", "--agent-id-prefix", "subagent", "--start-index", "4")
    assert json.loads(result.stdout) == []


def test_claim_next_single_agent_requires_single_limit(tmp_path: Path) -> None:
    run_engine(tmp_path, "--profile", "generic", "init", "--name", "Single Agent Claim Next Test")
    run_engine(tmp_path, "create-work", "Parent op", "--type", "operation", "--key", "parent_op")
    run_engine(tmp_path, "add-child", "WI-0001", "Ready A", "--type", "task", "--key", "ready_a")

    result = run_engine(tmp_path, "claim-next", "WI-0001", "--limit", "2", "--agent-id", "subagent-1", expect_ok=False)
    assert "--agent-id can only be used when --limit is 1" in result.stderr

    result = run_engine(tmp_path, "claim-next", "WI-0001", "--agent-id", "subagent-1")
    claims = json.loads(result.stdout)
    assert claims[0]["work_item_label"] == "WI-0002"
    assert claims[0]["agent_id"] == "subagent-1"


def test_claim_next_filters_children_by_single_tag(tmp_path: Path) -> None:
    run_engine(tmp_path, "--profile", "generic", "init", "--name", "Tagged Claim Next Test")
    run_engine(tmp_path, "create-work", "Parent op", "--type", "operation", "--key", "parent_op")
    run_engine(tmp_path, "add-child", "WI-0001", "Draft answer", "--type", "task", "--key", "draft_answer", "--tag", "writer")
    run_engine(tmp_path, "add-child", "WI-0001", "Fact check answer", "--type", "task", "--key", "fact_check_answer", "--tag", "reviewer")
    run_engine(tmp_path, "add-child", "WI-0001", "Untagged coordination", "--type", "task", "--key", "coordination")

    result = run_engine(tmp_path, "claim-next", "WI-0001", "--limit", "5", "--agent-id-prefix", "writer-agent", "--tag", "writer")
    claims = json.loads(result.stdout)
    assert [claim["work_item_label"] for claim in claims] == ["WI-0002"]
    assert claims[0]["tag"] == "writer"
    assert claims[0]["agent_id"] == "writer-agent-1"

    result = run_engine(tmp_path, "claim-next", "WI-0001", "--limit", "5", "--agent-id-prefix", "review-agent", "--tag", "reviewer")
    claims = json.loads(result.stdout)
    assert [claim["work_item_label"] for claim in claims] == ["WI-0003"]
    assert claims[0]["tag"] == "reviewer"

    conn = engine_db(tmp_path)
    statuses = {
        row["work_item_key"]: row["status"]
        for row in conn.execute("SELECT work_item_key, status FROM work_item ORDER BY label").fetchall()
    }
    assert statuses["draft_answer"] == "in_progress"
    assert statuses["fact_check_answer"] == "in_progress"
    assert statuses["coordination"] == "ready"


def test_add_children_accepts_tags_and_show_children_displays_them(tmp_path: Path) -> None:
    run_engine(tmp_path, "--profile", "generic", "init", "--name", "Tagged Children Test")
    run_engine(tmp_path, "create-work", "Parent op", "--type", "operation", "--key", "parent_op")
    children_file = tmp_path / "children.yaml"
    children_file.write_text(
        "children:\n"
        "  - title: Draft answer\n"
        "    key: draft_answer\n"
        "    tag: writer\n"
        "  - title: Review answer\n"
        "    key: review_answer\n"
        "    tag: reviewer\n",
        encoding="utf-8",
    )

    run_engine(tmp_path, "add-children", "WI-0001", "--file", str(children_file))
    result = run_engine(tmp_path, "show", "WI-0001", "--children")
    assert "tag=writer" in result.stdout
    assert "tag=reviewer" in result.stdout


def test_expire_claims_releases_stale_work_item(tmp_path: Path) -> None:
    init_bid_project(tmp_path)
    run_cmd(
        tmp_path,
        "claim",
        "WI-0002",
        "--agent-id",
        "agent-1",
        "--expected-row-version",
        "1",
        "--lease-minutes",
        "1",
    )
    conn = db(tmp_path)
    conn.execute("UPDATE work_item_claim SET expires_at='2000-01-01T00:00:00Z' WHERE status='active'")
    conn.commit()

    run_cmd(tmp_path, "expire-claims")

    claim = conn.execute("SELECT status, release_reason FROM work_item_claim").fetchone()
    work = conn.execute("SELECT status FROM work_item WHERE label='WI-0002'").fetchone()
    assert claim["status"] == "expired"
    assert claim["release_reason"] == "expired"
    assert work["status"] == "ready"


def test_claim_reaps_expired_claim_before_acquiring(tmp_path: Path) -> None:
    init_bid_project(tmp_path)
    run_cmd(tmp_path, "claim", "WI-0002", "--agent-id", "agent-1", "--expected-row-version", "1")
    conn = db(tmp_path)
    conn.execute("UPDATE work_item_claim SET expires_at='2000-01-01T00:00:00Z' WHERE status='active'")
    conn.commit()

    # Expiry resets work_item.status but does not bump row_version, so agent-2
    # can claim with the version it observed before the expiry.
    run_cmd(tmp_path, "claim", "WI-0002", "--agent-id", "agent-2", "--expected-row-version", "2")

    claims = conn.execute("SELECT agent_id, status FROM work_item_claim ORDER BY claimed_at, agent_id").fetchall()
    assert [(row["agent_id"], row["status"]) for row in claims] == [
        ("agent-1", "expired"),
        ("agent-2", "active"),
    ]


def test_source_revision_proposes_reviewed_impacts_and_preserves_completion(tmp_path: Path) -> None:
    init_bid_project(tmp_path)
    run_cmd(tmp_path, "claim", "WI-0002", "--agent-id", "agent-1", "--expected-row-version", "1")
    run_cmd(tmp_path, "complete", "WI-0002", "--agent-id", "agent-1", "--expected-row-version", "2")

    source_dir = tmp_path / "inputs" / "client_docs"
    source_dir.mkdir(parents=True, exist_ok=True)
    (source_dir / "pricing-v1.txt").write_text("pricing v1\n", encoding="utf-8")
    (source_dir / "pricing-v2.txt").write_text("pricing v2 revised\n", encoding="utf-8")

    run_cmd(
        tmp_path,
        "create-source",
        "Pricing Schedule",
        "--type",
        "pricing_schedule",
        "--path",
        "./inputs/client_docs/pricing-v1.txt",
        "--version-label",
        "v1",
    )
    run_cmd(
        tmp_path,
        "revise-source-document",
        "DOC-0001",
        "--path",
        "./inputs/client_docs/pricing-v2.txt",
        "--version-label",
        "v2",
        "--change-note",
        "Client revised pricing",
    )

    conn = db(tmp_path)
    proposed = conn.execute("SELECT COUNT(*) FROM impact WHERE status='proposed'").fetchone()[0]
    assert proposed >= 1

    run_cmd(tmp_path, "approve-impact", "IMP-0001", "--reviewed-by", "human")
    run_cmd(tmp_path, "apply-approved-impacts", "DOCV-0002")

    completed = conn.execute("SELECT status FROM work_item WHERE label='WI-0002'").fetchone()
    assert completed["status"] == "complete"
    applied = conn.execute("SELECT status FROM impact WHERE label='IMP-0001'").fetchone()
    assert applied["status"] == "applied"


def test_context_and_graph_are_generated_files(tmp_path: Path) -> None:
    init_bid_project(tmp_path)
    run_cmd(tmp_path, "context", "build", "--work-item", "WI-0004")
    run_cmd(tmp_path, "render")
    run_cmd(tmp_path, "render-graph")

    context = tmp_path / "tmp" / "context-packs" / "WI-0004.md"
    graph = tmp_path / "tmp" / "ibm-bid-project-graph.mmd"
    dashboard = tmp_path / "tmp" / "ibm-bid-project.md"
    assert "generated_from_event_id" in context.read_text(encoding="utf-8")
    assert "flowchart TD" in graph.read_text(encoding="utf-8")
    assert "## Work Items" in dashboard.read_text(encoding="utf-8")


def test_add_child_and_add_children_expand_work_graph(tmp_path: Path) -> None:
    init_bid_project(tmp_path)

    run_cmd(
        tmp_path,
        "add-child",
        "WI-0001",
        "Wireframe Q1 service management",
        "--type",
        "answer",
        "--key",
        "wireframe_q1_service_management",
        "--phase",
        "content_development",
        "--source-work-item",
        "WI-0002",
    )

    batch = tmp_path / "children.yaml"
    batch.write_text(
        """
children:
  - title: Answer Q1 service management
    key: answer_q1_service_management
    type: answer
    phase: content_development
    dependencies:
      - upstream: WI-0008
        policy: mark_outdated
  - title: Fact check Q1 service management
    key: fact_check_q1_service_management
    type: review
    phase: technical_assurance
    dependencies:
      - upstream: WI-0009
        policy: mark_needs_review
""".strip(),
        encoding="utf-8",
    )
    run_cmd(tmp_path, "add-children", "WI-0001", "--file", str(batch), "--source-work-item", "WI-0002")

    conn = db(tmp_path)
    rows = conn.execute(
        "SELECT label, work_item_key, parent_work_item_id FROM work_item WHERE work_item_key LIKE '%q1_service_management' ORDER BY label"
    ).fetchall()
    assert [row["work_item_key"] for row in rows] == [
        "wireframe_q1_service_management",
        "answer_q1_service_management",
        "fact_check_q1_service_management",
    ]
    dep_count = conn.execute(
        """
        SELECT COUNT(*) FROM work_dependency dep
        JOIN work_item down ON down.id = dep.downstream_work_item_id
        WHERE down.work_item_key IN ('answer_q1_service_management', 'fact_check_q1_service_management')
        """
    ).fetchone()[0]
    assert dep_count == 2

    events = [
        row["detail_json"]
        for row in conn.execute("SELECT detail_json FROM event_log WHERE event_type='work_item_created'")
    ]
    assert any('"source_work_item":"WI-0002"' in event for event in events)


# ---------------------------------------------------------------------------
# Direct engine CLI tests — generic profile, no bid wrapper
# ---------------------------------------------------------------------------

def _init(tmp_path: Path) -> None:
    run_engine(tmp_path, "--profile", "generic", "init", "--name", "Test Project")


def test_direct_show_and_show_children(tmp_path: Path) -> None:
    _init(tmp_path)
    run_engine(tmp_path, "create-work", "Parent op", "--type", "operation", "--key", "parent_op")
    run_engine(tmp_path, "add-child", "WI-0001", "Child A", "--type", "task", "--key", "child_a")
    run_engine(tmp_path, "add-child", "WI-0001", "Child B", "--type", "task", "--key", "child_b")

    result = run_engine(tmp_path, "show", "WI-0001")
    assert '"work_item_key": "parent_op"' in result.stdout

    result = run_engine(tmp_path, "show", "WI-0001", "--children")
    assert "Child A" in result.stdout
    assert "Child B" in result.stdout


def test_direct_release_returns_work_item_to_ready(tmp_path: Path) -> None:
    _init(tmp_path)
    run_engine(tmp_path, "create-work", "Task", "--type", "task", "--key", "the_task")
    run_engine(tmp_path, "claim", "WI-0001", "--agent-id", "agent-1", "--expected-row-version", "1")
    run_engine(tmp_path, "release", "WI-0001", "--agent-id", "agent-1", "--reason", "handing off")

    conn = engine_db(tmp_path)
    assert conn.execute("SELECT status FROM work_item WHERE label='WI-0001'").fetchone()["status"] == "ready"
    claim = conn.execute("SELECT status, release_reason FROM work_item_claim").fetchone()
    assert claim["status"] == "released"
    assert claim["release_reason"] == "handing off"


def test_direct_expire_claims_via_engine(tmp_path: Path) -> None:
    _init(tmp_path)
    run_engine(tmp_path, "create-work", "Task", "--type", "task", "--key", "the_task")
    run_engine(tmp_path, "claim", "WI-0001", "--agent-id", "agent-1", "--expected-row-version", "1")

    conn = engine_db(tmp_path)
    conn.execute("UPDATE work_item_claim SET expires_at='2000-01-01T00:00:00Z' WHERE status='active'")
    conn.commit()

    result = run_engine(tmp_path, "expire-claims")
    assert "Expired 1 claim(s)" in result.stdout

    assert conn.execute("SELECT status FROM work_item_claim").fetchone()["status"] == "expired"
    assert conn.execute("SELECT status FROM work_item WHERE label='WI-0001'").fetchone()["status"] == "ready"


def test_direct_create_artifact(tmp_path: Path) -> None:
    _init(tmp_path)
    run_engine(tmp_path, "create-work", "Write section", "--type", "task", "--key", "write_section")
    run_engine(tmp_path, "create-artifact", "Executive Summary", "--type", "document", "--owner", "WI-0001")

    conn = engine_db(tmp_path)
    row = conn.execute("SELECT artifact_key, owner_work_item_id FROM artifact WHERE label='ART-0001'").fetchone()
    wi_id = conn.execute("SELECT id FROM work_item WHERE label='WI-0001'").fetchone()["id"]
    assert row["artifact_key"] == "executive_summary"
    assert row["owner_work_item_id"] == wi_id

    bad = run_engine(tmp_path, "create-artifact", "Bad", "--type", "document", "--owner", "WI-9999", expect_ok=False)
    assert "ERROR" in bad.stderr


def test_direct_source_revision_and_impact_workflow(tmp_path: Path) -> None:
    _init(tmp_path)
    run_engine(tmp_path, "create-work", "Analyse docs", "--type", "task", "--key", "analyse")
    run_engine(tmp_path, "create-work", "Write report", "--type", "task", "--key", "report")
    run_engine(tmp_path, "link", "WI-0001", "WI-0002", "--policy", "mark_needs_review")

    src = tmp_path / "inputs" / "doc.txt"
    src.parent.mkdir(parents=True)
    src.write_text("v1 content", encoding="utf-8")
    run_engine(tmp_path, "create-source", "Client doc", "--type", "document", "--path", str(src), "--version-label", "v1")

    src.write_text("v2 revised", encoding="utf-8")
    run_engine(tmp_path, "revise-source", "SRC-0001", "--path", str(src), "--version-label", "v2", "--change-note", "Major revision")

    conn = engine_db(tmp_path)
    assert conn.execute("SELECT COUNT(*) FROM impact WHERE status='proposed'").fetchone()[0] >= 1

    result = run_engine(tmp_path, "review-impacts", "SRCV-0002")
    assert "IMP-0001" in result.stdout

    run_engine(tmp_path, "approve-impact", "IMP-0001", "--reviewed-by", "human")
    run_engine(tmp_path, "apply-approved-impacts", "SRCV-0002")

    assert conn.execute("SELECT status FROM impact WHERE label='IMP-0001'").fetchone()["status"] == "applied"
    validity = conn.execute("SELECT validity_status FROM work_item WHERE label='WI-0001'").fetchone()["validity_status"]
    assert validity == "needs_review"


def test_direct_reject_impact_leaves_work_item_current(tmp_path: Path) -> None:
    _init(tmp_path)
    run_engine(tmp_path, "create-work", "Task A", "--type", "task", "--key", "task_a")

    src = tmp_path / "inputs" / "doc.txt"
    src.parent.mkdir(parents=True)
    src.write_text("v1", encoding="utf-8")
    run_engine(tmp_path, "create-source", "Doc", "--type", "document", "--path", str(src), "--version-label", "v1")
    src.write_text("v2", encoding="utf-8")
    run_engine(tmp_path, "revise-source", "SRC-0001", "--path", str(src), "--version-label", "v2")

    run_engine(tmp_path, "reject-impact", "IMP-0001", "--reviewed-by", "human", "--reason", "Not related")
    run_engine(tmp_path, "apply-approved-impacts", "SRCV-0002")

    conn = engine_db(tmp_path)
    assert conn.execute("SELECT status FROM impact WHERE label='IMP-0001'").fetchone()["status"] == "rejected"
    assert conn.execute("SELECT validity_status FROM work_item WHERE label='WI-0001'").fetchone()["validity_status"] == "current"


def test_direct_context_build_and_staleness_detection(tmp_path: Path) -> None:
    _init(tmp_path)
    run_engine(tmp_path, "create-work", "Analyse", "--type", "task", "--key", "analyse")
    run_engine(tmp_path, "context", "build", "--work-item", "WI-0001")

    context_file = tmp_path / "tmp" / "context-packs" / "WI-0001.md"
    assert context_file.exists()
    assert "generated_from_event_id" in context_file.read_text(encoding="utf-8")

    result = run_engine(tmp_path, "context", "show", "WI-0001")
    assert "current" in result.stdout

    run_engine(tmp_path, "create-work", "Another task", "--type", "task", "--key", "another")
    result = run_engine(tmp_path, "context", "show", "WI-0001")
    assert "stale" in result.stdout


def test_direct_render_graph_produces_mermaid(tmp_path: Path) -> None:
    _init(tmp_path)
    run_engine(tmp_path, "create-work", "Task A", "--type", "task", "--key", "task_a")
    run_engine(tmp_path, "create-work", "Task B", "--type", "task", "--key", "task_b")
    run_engine(tmp_path, "link", "WI-0001", "WI-0002", "--policy", "mark_needs_review")
    run_engine(tmp_path, "render-graph")

    graph_file = tmp_path / "tmp" / "agent-state-graph.mmd"
    assert graph_file.exists()
    content = graph_file.read_text(encoding="utf-8")
    assert "flowchart TD" in content
    assert "WI_0001" in content
    assert "mark_needs_review" in content


def test_direct_add_children_from_yaml_file_with_dependencies(tmp_path: Path) -> None:
    _init(tmp_path)
    run_engine(tmp_path, "create-work", "Parent op", "--type", "operation", "--key", "parent_op")
    run_engine(tmp_path, "create-work", "Prerequisite", "--type", "task", "--key", "prereq")

    children_file = tmp_path / "children.yaml"
    children_file.write_text(
        "children:\n"
        "  - title: Step one\n"
        "    key: step_one\n"
        "    type: task\n"
        "    dependencies:\n"
        "      - upstream: WI-0002\n"
        "        policy: mark_outdated\n"
        "  - title: Step two\n"
        "    key: step_two\n"
        "    type: task\n",
        encoding="utf-8",
    )
    run_engine(tmp_path, "add-children", "WI-0001", "--file", str(children_file))

    conn = engine_db(tmp_path)
    keys = [r["work_item_key"] for r in conn.execute("SELECT work_item_key FROM work_item ORDER BY label").fetchall()]
    assert "step_one" in keys
    assert "step_two" in keys

    dep = conn.execute("""
        SELECT dep.invalidation_policy FROM work_dependency dep
        JOIN work_item up ON up.id = dep.upstream_work_item_id
        JOIN work_item down ON down.id = dep.downstream_work_item_id
        WHERE up.label='WI-0002' AND down.work_item_key='step_one'
    """).fetchone()
    assert dep is not None
    assert dep["invalidation_policy"] == "mark_outdated"


def test_direct_init_from_template_file(tmp_path: Path) -> None:
    profile_dir = tmp_path / "profile"
    template_dir = profile_dir / "workflow-templates"
    template_dir.mkdir(parents=True)

    (profile_dir / "profile.yaml").write_text("profile: generic\nname: Template Project\n", encoding="utf-8")
    (template_dir / "simple.yaml").write_text(
        "work_items:\n"
        "  - title: Discovery\n"
        "    key: discovery\n"
        "    type: task\n"
        "    status: ready\n"
        "  - title: Analysis\n"
        "    key: analysis\n"
        "    type: task\n"
        "    status: not_started\n"
        "  - title: Report\n"
        "    key: report\n"
        "    type: task\n"
        "    status: not_started\n"
        "dependencies:\n"
        "  - upstream: discovery\n"
        "    downstream: analysis\n"
        "    policy: mark_needs_review\n"
        "  - upstream: analysis\n"
        "    downstream: report\n"
        "    policy: mark_outdated\n",
        encoding="utf-8",
    )

    run_engine(
        tmp_path,
        "--profile-config", str(profile_dir / "profile.yaml"),
        "init", "--template", "simple",
    )

    conn = engine_db(tmp_path)
    assert conn.execute("SELECT COUNT(*) FROM work_item").fetchone()[0] == 3
    assert conn.execute("SELECT COUNT(*) FROM work_dependency").fetchone()[0] == 2

    policies = {r[0] for r in conn.execute("SELECT invalidation_policy FROM work_dependency").fetchall()}
    assert policies == {"mark_needs_review", "mark_outdated"}
