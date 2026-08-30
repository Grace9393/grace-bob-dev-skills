#!/usr/bin/env python3
"""Scan the local source cache, classify every SKILL.md, emit index.json +
references/catalogue.md.

Two classifications are applied to every skill:

  portability -- can this actually run under Claude Code / Bob?
      portable      self-contained, install and use
      needs-host    the prose transfers; the tool calls need OpenAkita's runtime,
                    its MCP servers, or a China-platform API key
      host-builtin  a wrapper around the host agent's own tool surface
                    (read-file, glob, browser-click...). Claude Code already has
                    these natively -- installing them creates collisions.
      duplicate     the same skill is already available to Grace from
                    anthropic-skills or another AA source
      repo-local    only meaningful inside its own repository

  model -- the tier this skill's work should run on, per the model-router rule
      (route on COST OF BEING WRONG, not on how important the project feels):
      haiku   one right answer, checkable in seconds, high volume
      opus    runs unattended for many steps, or a wrong answer is expensive
      sonnet  everything else (the default)
      fable   never assigned automatically -- escalation only, after Opus 5 has
              actually failed twice with a complete prompt

Usage:
    python build_catalogue.py                       # uses default cache
    python build_catalogue.py --cache <dir> --out <pack root>
"""
import argparse
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
PACK = os.path.dirname(os.path.dirname(HERE))          # grace-skill-pack/
SKILLDIR = os.path.dirname(HERE)                       # grace-skills/

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "dist", "build"}

# ---------------------------------------------------------------- model tiers

# Explicit judgements. Anything not listed falls through to the keyword rules.
MODEL_OVERRIDE = {
    # --- opus: unattended multi-step, or an expensive-to-undo answer ----------
    "leader": "opus",                    # writes the brief another agent runs blind
    "dbs-agent-migration": "opus",       # rewrites a repo's rule files across agents
    "dbs-decision": "opus",              # long-lived decision knowledge base
    "dbs-knowledge": "opus",             # builds + prunes a knowledge base on disk
    "dbs-content-system": "opus",        # restructures an entire content archive
    "dbs-good-question": "opus",         # its output is a spec other agents execute
    "decide": "opus",                    # architecture decision records
    "db-migrations": "opus",             # schema migrations; wrong = data loss
    "superset-orchestration": "opus",    # multi-agent orchestration
    "redesign": "opus",
    "skill-creator": "opus",
    "mcp-builder": "opus",
    "obra/superpowers@systematic-debugging": "opus",
    "obra/superpowers@writing-plans": "opus",
    "openakita/skills@baidu-deep-research": "opus",
    "hv-analysis": "opus",               # multi-stage research -> PDF deliverable
    "crawl4ai": "opus",                  # long unattended crawls
    # --- sonnet: pinned to stop the keyword rules over-promoting them --------
    "chinese-novelist": "sonnet",        # "plot architecture" is not architecture
    "dbs-slowisfast": "sonnet",          # a diagnostic conversation, not a build
    "superset": "sonnet",                # thin CLI wrapper; the orchestration
                                         # skill next to it is the opus one
    "notebooklm-research": "sonnet",
    # --- haiku: mechanical, checkable, high volume ---------------------------
    "dbs-ai-check": "haiku",
    "dbs-xhs-title": "haiku",
    "dbs-restore": "haiku",
    "dbs-save": "haiku",
    "dbs-skill-cleaner": "haiku",
    "neat-freak": "haiku",
    "storage-analyzer": "haiku",
    "ticket-format": "haiku",
    "openakita/skills@datetime-tool": "haiku",
    "openakita/skills@file-manager": "haiku",
    "openakita/skills@changelog-generator": "haiku",
    "openakita/skills@video-downloader": "haiku",
    "subtitle-craft": "haiku",
    "footage-gate": "haiku",
    "translate": "haiku",
    "aihot": "haiku",                    # fetch a feed and summarise it
}

HAIKU_KEYWORDS = re.compile(
    r"(ocr|screenshot|download|rename|格式化|清理|归档|标签|提取字段|翻译一|"
    r"list-|get-|read-|write-|delete-|glob|grep|browser-|desktop-)", re.I)
OPUS_KEYWORDS = re.compile(
    r"(migration|migrate|orchestrat|architecture|refactor|deep research|"
    r"深度研究|迁移|架构|编排|长期|决策工程|unattended)", re.I)

EFFORT = {"haiku": "-", "sonnet": "high", "opus": "high", "fable": "high"}

# ------------------------------------------------------------- portability

# Bundled with Anthropic's anthropic-skills plugin or already in the AA corpus.
DUPLICATE = {
    "algorithmic-art", "canvas-design", "code-review", "doc-coauthoring",
    "docx", "pdf", "pptx", "xlsx", "mcp-builder", "skill-creator",
    "theme-factory", "web-artifacts-builder", "webapp-testing",
    "slack-gif-creator", "frontend-design", "seedance-video",
    "image-understanding", "image-understander", "pretty-mermaid",
}

# Skills whose tool calls need an OpenAkita account, a China-platform API key,
# or a vendor MCP server that is not connected here.
NEEDS_HOST = re.compile(
    r"^(baidu|tencent|amap|didi|fliggy|taobaoke|douyin|xiaohongshu|xiaodu|"
    r"netease|bilibili|qq-|wecom|feishu|dingtalk|wechat-article|apify|"
    r"gmail-automation|google-calendar|github-automation|smtp-|miaoda|"
    r"moltbook|youtube-summarizer|obsidian-skills|tongyi-|happyhorse|"
    r"avatar-studio|clip-sense|omni-post|media-post|seedance)", re.I)


# ---------------------------------------------------------------- licences

# Repo-level fallback, read off each repo's LICENSE file on 2026-08-07.
REPO_LICENCE = {
    "dbskill": "CC BY-NC 4.0",
    "openakita": "AGPL-3.0",
    "khazix-skills": "MIT",
    "notebooklm-skill": "MIT",
    "crawl4ai": "Apache-2.0",
    "superset": "Elastic-2.0",
    "finger-frame-effect-lucy": "none",
}

# Sniff patterns for a per-skill LICENSE file. 14 openakita skills ship their
# own Apache-2.0 licence (they are Anthropic's bundled skills, vendored in), so
# the repo licence is a fallback, not the answer.
LICENCE_SNIFF = [
    (re.compile(r"Apache License", re.I), "Apache-2.0"),
    (re.compile(r"^MIT License", re.I | re.M), "MIT"),
    (re.compile(r"GNU AFFERO", re.I), "AGPL-3.0"),
    (re.compile(r"GNU GENERAL PUBLIC", re.I), "GPL"),
    (re.compile(r"BSD", re.I), "BSD"),
    (re.compile(r"NonCommercial", re.I), "CC BY-NC 4.0"),
    (re.compile(r"Elastic License", re.I), "Elastic-2.0"),
]

# permissive  = use freely, attribution only
# noncommercial = personal/learning only; NOT for billed client work
# copyleft    = obligations attach to distribution or hosted use
# proprietary = source-available with use restrictions
# unlicensed  = no grant at all; default is all rights reserved
LICENCE_CLASS = {
    "Apache-2.0": "permissive", "MIT": "permissive", "BSD": "permissive",
    "CC BY-NC 4.0": "noncommercial",
    "AGPL-3.0": "copyleft", "GPL": "copyleft",
    "Elastic-2.0": "proprietary",
    "none": "unlicensed",
}


def detect_licence(skill_dir, repo):
    """Per-skill LICENSE wins over the repo default."""
    try:
        for fn in os.listdir(skill_dir):
            if fn.upper().startswith("LICEN"):
                head = open(os.path.join(skill_dir, fn), encoding="utf-8",
                            errors="replace").read(4000)
                for pat, name in LICENCE_SNIFF:
                    if pat.search(head):
                        return name, True
    except OSError:
        pass
    return REPO_LICENCE.get(repo, "unknown"), False


def parse_front_matter(path):
    text = open(path, encoding="utf-8", errors="replace").read()
    m = re.match(r"^---\r?\n(.*?)\r?\n---", text, re.S)
    if not m:
        return {}
    out, key, buf = {}, None, []
    for line in m.group(1).split("\n"):
        km = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if km and not line.startswith((" ", "\t")):
            if key:
                out[key] = " ".join(buf).strip()
            key = km.group(1)
            val = km.group(2).strip()
            buf = [] if val in (">", "|", ">-", "|-", "") else [val]
        elif key:
            buf.append(line.strip())
    if key:
        out[key] = " ".join(buf).strip()
    return out


def group_of(repo, relpath):
    parts = relpath.split("/")
    if repo == "openakita":
        if len(parts) > 2 and parts[1] == "skills" and parts[2] == "system":
            return "openakita/system"
        return "openakita/" + parts[1]
    if repo == "superset":
        return "superset/agents" if parts[1] == ".agents" else "superset/plugin"
    return repo


def classify_portability(group, name, short):
    if group == "openakita/system":
        return "host-builtin"
    if short in DUPLICATE:
        return "duplicate"
    if group == "superset/agents":
        return "repo-local"
    if NEEDS_HOST.search(short):
        return "needs-host"
    if group == "openakita/plugins":
        return "needs-host"
    return "portable"


def classify_model(name, short, desc, portability):
    for key in (name, short):
        if key in MODEL_OVERRIDE:
            return MODEL_OVERRIDE[key]
    if portability == "host-builtin":
        return "haiku"
    blob = f"{short} {desc}"
    if OPUS_KEYWORDS.search(blob):
        return "opus"
    if HAIKU_KEYWORDS.search(short):
        return "haiku"
    return "sonnet"


def scan(cache):
    rows = []
    for repo in sorted(os.listdir(cache)):
        rp = os.path.join(cache, repo)
        if not os.path.isdir(rp):
            continue
        for dirpath, dirnames, filenames in os.walk(rp):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            if "SKILL.md" not in filenames:
                continue
            path = os.path.join(dirpath, "SKILL.md")
            fm = parse_front_matter(path)
            rel = os.path.relpath(path, cache).replace("\\", "/")
            name = fm.get("name") or os.path.basename(dirpath)
            short = name.split("@")[-1]
            desc = re.sub(r"\s+", " ", fm.get("description", "")).strip()
            group = group_of(repo, rel)
            port = classify_portability(group, name, short)
            model = classify_model(name, short, desc, port)
            lic, own = detect_licence(dirpath, repo)
            rows.append({
                "id": short, "name": name, "repo": repo, "group": group,
                "path": rel, "dir": os.path.dirname(rel),
                "description": desc, "portability": port,
                "model": model, "effort": EFFORT[model],
                "licence": lic, "licence_class": LICENCE_CLASS.get(lic, "unknown"),
                "licence_own_file": own,
            })
    rows.sort(key=lambda r: (r["group"], r["id"]))
    return rows


def write_catalogue(rows, out_md):
    from collections import Counter
    pc, mc = Counter(r["portability"] for r in rows), Counter(r["model"] for r in rows)
    L = []
    L.append("# Catalogue — 7 Grace9393 repos\n")
    L.append("Generated by `scripts/build_catalogue.py`. **Do not hand-edit.**\n")
    L.append(f"**{len(rows)} skills** across {len(set(r['group'] for r in rows))} groups.\n")
    L.append("| Portability | Count | | Model tier | Count |")
    L.append("|---|---:|---|---|---:|")
    pk = ["portable", "needs-host", "duplicate", "host-builtin", "repo-local"]
    mk = ["haiku", "sonnet", "opus", "fable"]
    for i in range(max(len(pk), len(mk))):
        a = f"`{pk[i]}` | {pc.get(pk[i], 0)}" if i < len(pk) else " | "
        b = f"`{mk[i]}` | {mc.get(mk[i], 0)}" if i < len(mk) else " | "
        L.append(f"| {a} | | {b} |")
    L.append("")
    L.append("Install only `portable`. See `SKILL.md` for what the other four mean.\n")
    lc = Counter(r["licence_class"] for r in rows if r["portability"] == "portable")
    L.append("**Licence, across the portable set** — `portable` is a technical")
    L.append("judgement (will it run). It says nothing about whether you may use the")
    L.append("output. See `sources.md`.\n")
    L.append("| Licence class | Portable skills | Use in billed client work |")
    L.append("|---|---:|---|")
    for k, note in (("permissive", "Yes — attribution only"),
                    ("noncommercial", "**No** — personal/learning only"),
                    ("copyleft", "Legal review first"),
                    ("proprietary", "Read the restrictions"),
                    ("unlicensed", "**No** — no grant exists")):
        if lc.get(k):
            L.append(f"| `{k}` | {lc[k]} | {note} |")
    L.append("")
    cur = None
    for r in rows:
        if r["group"] != cur:
            cur = r["group"]
            n = sum(1 for x in rows if x["group"] == cur)
            L.append(f"\n## {cur} ({n})\n")
            L.append("| Skill | Model | Portability | Licence | What it does |")
            L.append("|---|---|---|---|---|")
        d = r["description"].replace("|", "/")
        if len(d) > 170:
            d = d[:167] + "..."
        eff = "" if r["effort"] == "-" else f" · {r['effort']}"
        lic = r["licence"] + ("*" if r["licence_own_file"] else "")
        L.append(f"| `{r['id']}` | {r['model']}{eff} | {r['portability']} | {lic} | {d} |")
    L.append("\n`*` = the skill ships its own LICENSE file, which overrides its repo's.")
    open(out_md, "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default=None)
    ap.add_argument("--out", default=PACK)
    a = ap.parse_args()
    if not a.cache:
        base = os.environ.get("LOCALAPPDATA") or os.path.join(
            os.path.expanduser("~"), ".cache")
        a.cache = os.path.join(base, "grace-skill-pack", "sources")
    if not os.path.isdir(a.cache):
        sys.exit(f"cache not found: {a.cache}\nrun scripts/sync_sources.py first")

    rows = scan(a.cache)
    idx = os.path.join(a.out, "index.json")
    json.dump({"cache": a.cache, "count": len(rows), "skills": rows},
              open(idx, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    md = os.path.join(a.out, "grace-skills", "references", "catalogue.md")
    write_catalogue(rows, md)
    print(f"{len(rows)} skills -> {idx}\n{' ' * len(str(len(rows)))}          -> {md}")


if __name__ == "__main__":
    main()
