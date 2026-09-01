#!/usr/bin/env python3
"""Install selected skills from the source cache into Claude Code and/or IBM Bob.

Conversion work this performs (the reason a plain copy is not enough):

  1. **Name rewrite.** 85 skills in openakita carry namespaced frontmatter names
     like `openakita/skills@brainstorming` or `obra/superpowers@writing-plans`.
     Claude Code skill names must be lowercase, hyphen-separated, and must match
     the directory name -- a slash or `@` makes the skill silently unloadable.
     Everything after the last `@` (and the last `/`) becomes the installed name,
     and the frontmatter is rewritten to match.
  2. **Model annotation.** Each installed SKILL.md gets a `metadata.model` and
     `metadata.effort` key from the catalogue, plus a one-line routing banner in
     the body, so the tier travels with the skill instead of living only here.
  3. **Portability gate.** Non-`portable` skills are refused unless --force.
  4. **Agent install.** --agents installs the four model-pinned subagents that
     make the routing actually automatic (Claude Code only; Bob has no
     equivalent surface).

Usage:
    python install_skills.py --list
    python install_skills.py --profile core --dry-run
    python install_skills.py --profile core --target claude --agents
    python install_skills.py --skill leader hv-analysis --target both
    python install_skills.py --profile core --uninstall
    python install_skills.py --audit
"""
import argparse
import json
import os
import re
import shutil
import sys

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
SKILLDIR = os.path.dirname(HERE)          # grace-skills/
PACK = os.path.dirname(SKILLDIR)          # grace-skill-pack/
INDEX = os.path.join(PACK, "index.json")
PROFILES = os.path.join(PACK, "profiles.json")
NEW_SKILLS = os.path.join(PACK, "new-skills")
AGENTS_SRC = os.path.join(SKILLDIR, "agents")

MARKER = ".installed-by-grace-skill-pack"


def claude_home():
    return os.environ.get("CLAUDE_CONFIG_DIR") or os.path.join(
        os.path.expanduser("~"), ".claude")


def bob_home():
    return os.environ.get("BOB_HOME") or os.path.join(
        os.path.expanduser("~"), ".bob")


def targets_for(target):
    t = {}
    if target in ("claude", "both"):
        t["claude"] = os.path.join(claude_home(), "skills")
    if target in ("bob", "both"):
        t["bob"] = os.path.join(bob_home(), "skills")
    return t


def load():
    if not os.path.exists(INDEX):
        sys.exit(f"missing {INDEX}\nrun scripts/build_catalogue.py first")
    data = json.load(open(INDEX, encoding="utf-8"))
    profiles = json.load(open(PROFILES, encoding="utf-8")) if os.path.exists(
        PROFILES) else {}
    by_id = {}
    for r in data["skills"]:
        by_id.setdefault(r["id"], r)          # first wins; groups are sorted
    # skills authored in this pack (the two repos that shipped no SKILL.md)
    if os.path.isdir(NEW_SKILLS):
        for d in sorted(os.listdir(NEW_SKILLS)):
            p = os.path.join(NEW_SKILLS, d, "SKILL.md")
            if os.path.exists(p):
                by_id[d] = {"id": d, "name": d, "repo": d, "group": "authored",
                            "dir": os.path.join("..", "new-skills", d),
                            "abs": os.path.join(NEW_SKILLS, d),
                            "description": "(authored in this pack)",
                            "portability": "portable",
                            "model": "opus" if d == "crawl4ai" else "sonnet",
                            "effort": "high",
                            # The skill text is ours. The licence recorded is
                            # that of the upstream it documents: crawl4ai is
                            # Apache-2.0; finger-frame-effect-lucy ships no
                            # licence at all, so its upstream grants nothing.
                            "licence": "Apache-2.0" if d == "crawl4ai" else "none",
                            "licence_class": ("permissive" if d == "crawl4ai"
                                              else "unlicensed"),
                            "licence_own_file": False}
    return data, by_id, profiles


def rewrite_skill_md(text, new_name, model, effort):
    """Normalise the frontmatter name and stamp the model tier."""
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n?(.*)$", text, re.S)
    if not m:
        fm, body = f"name: {new_name}\n", text
    else:
        fm, body = m.group(1), m.group(2)
    if re.search(r"^name:", fm, re.M):
        fm = re.sub(r"^name:.*$", f"name: {new_name}", fm, count=1, flags=re.M)
    else:
        fm = f"name: {new_name}\n" + fm
    # Lift any existing metadata block out, keep every key we do not own, and
    # re-emit it with ours on top. Dropping the block wholesale would discard
    # provenance the skill author wrote (upstream, verified_against, related).
    OURS = ("model", "effort", "source")
    kept = []
    mb = re.search(r"^metadata:[ \t]*\n((?:[ \t]+\S.*\n?)*)", fm, re.M)
    if mb:
        for line in mb.group(1).splitlines():
            key = line.strip().split(":", 1)[0].strip()
            if key and key not in OURS:
                kept.append("  " + line.strip())
        fm = (fm[:mb.start()] + fm[mb.end():]).rstrip()
    eff = "" if effort == "-" else f"\n  effort: {effort}"
    fm += (f"\nmetadata:\n  model: {model}{eff}\n  source: grace-skill-pack"
           + ("\n" + "\n".join(kept) if kept else ""))
    # Skills authored inside this pack already carry their own banner.
    banner = ""
    if "grace-skill-pack:" not in body[:400]:
        banner = (f"<!-- grace-skill-pack: run this on **{model}**"
                  + (f" at effort `{effort}`" if effort != "-" else "")
                  + ". Route a subagent to it rather than switching the session. -->\n\n")
    return f"---\n{fm}\n---\n\n{banner}{body.lstrip()}"


def install_one(row, cache, dest_root, dry, force, commercial_only=False):
    if row["portability"] != "portable" and not force:
        return ("skip", f"{row['id']}: {row['portability']} (use --force)")
    if commercial_only and row.get("licence_class") != "permissive":
        return ("licence", f"{row['id']}: {row['licence']} "
                           f"({row['licence_class']}) — not billable")
    src = row.get("abs") or os.path.join(cache, row["dir"])
    if not os.path.isdir(src):
        return ("fail", f"{row['id']}: source missing {src}")
    dest = os.path.join(dest_root, row["id"])
    warn = "" if row.get("licence_class") == "permissive" else \
           f"  ⚠ {row.get('licence', '?')}"
    if dry:
        return ("dry", f"{row['id']} -> {dest}  [{row['model']}]{warn}")
    if os.path.isdir(dest) and not os.path.exists(os.path.join(dest, MARKER)):
        return ("skip", f"{row['id']}: {dest} exists and is not ours")
    if os.path.isdir(dest):
        shutil.rmtree(dest)
    shutil.copytree(src, dest, ignore=shutil.ignore_patterns(
        ".git", "node_modules", "__pycache__", "*.pyc"))
    sk = os.path.join(dest, "SKILL.md")
    text = open(sk, encoding="utf-8", errors="replace").read()
    open(sk, "w", encoding="utf-8", newline="\n").write(
        rewrite_skill_md(text, row["id"], row["model"], row["effort"]))
    open(os.path.join(dest, MARKER), "w", encoding="utf-8").write(
        json.dumps({"id": row["id"], "origin": row.get("path", row["dir"]),
                    "model": row["model"],
                    "licence": row.get("licence")}, ensure_ascii=False))
    return ("ok", f"{row['id']} -> {dest}  [{row['model']}]{warn}")


def uninstall_one(row, dest_root, dry):
    dest = os.path.join(dest_root, row["id"])
    if not os.path.isdir(dest):
        return ("skip", f"{row['id']}: not installed")
    if not os.path.exists(os.path.join(dest, MARKER)):
        return ("skip", f"{row['id']}: not installed by this pack -- left alone")
    if dry:
        return ("dry", f"remove {dest}")
    shutil.rmtree(dest)
    return ("ok", f"removed {dest}")


def install_agents(dry):
    dest_root = os.path.join(claude_home(), "agents")
    if not os.path.isdir(AGENTS_SRC):
        return
    os.makedirs(dest_root, exist_ok=True)
    for f in sorted(os.listdir(AGENTS_SRC)):
        if not f.endswith(".md"):
            continue
        d = os.path.join(dest_root, f)
        print(f"  agent  {f} -> {d}" + ("  (dry)" if dry else ""))
        if not dry:
            shutil.copy2(os.path.join(AGENTS_SRC, f), d)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile")
    ap.add_argument("--skill", nargs="*")
    ap.add_argument("--target", choices=["claude", "bob", "both"], default="claude")
    ap.add_argument("--agents", action="store_true",
                    help="also install the model-pinned subagents (Claude Code)")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--audit", action="store_true")
    ap.add_argument("--uninstall", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--commercial-only", action="store_true",
                    help="install only permissively-licensed skills (MIT / "
                         "Apache-2.0 / BSD) — skip anything not usable in "
                         "billed client work")
    ap.add_argument("--cache", default=None)
    a = ap.parse_args()

    data, by_id, profiles = load()
    cache = a.cache or data.get("cache")

    if a.list:
        print("profiles:")
        for k, v in profiles.items():
            print(f"  {k:<20} {len(v['skills'])} skills -- {v['description']}")
        print(f"\nportable skills ({sum(1 for r in by_id.values() if r['portability']=='portable')}):")
        for r in sorted(by_id.values(), key=lambda r: r["id"]):
            if r["portability"] == "portable":
                flag = " " if r.get("licence_class") == "permissive" else "!"
                print(f" {flag}{r['id']:<30} {r['model']:<7} "
                      f"{r.get('licence','?'):<13} {r['group']}")
        print("\n  ! = not permissively licensed; see references/sources.md "
              "before using it in billed work. Filter with --commercial-only.")
        return

    if a.audit:
        for label, root in targets_for("both").items():
            print(f"\n{label}: {root}")
            if not os.path.isdir(root):
                print("  (does not exist)")
                continue
            for d in sorted(os.listdir(root)):
                mk = os.path.join(root, d, MARKER)
                tag = "ours" if os.path.exists(mk) else "other"
                info = json.load(open(mk, encoding="utf-8")) if tag == "ours" else {}
                print(f"  [{tag:<5}] {d:<32} {info.get('model',''):<7} "
                      f"{info.get('licence','')}")
        return

    ids = list(a.skill or [])
    if a.profile:
        if a.profile == "all-portable":
            ids += [r["id"] for r in by_id.values() if r["portability"] == "portable"]
        elif a.profile in profiles:
            ids += profiles[a.profile]["skills"]
        else:
            sys.exit(f"unknown profile {a.profile}; try --list")
    if not ids and not a.agents:
        sys.exit("nothing to do -- pass --profile, --skill, or --agents")

    roots = targets_for(a.target)
    for label, root in roots.items():
        print(f"\n== {label}: {root}")
        os.makedirs(root, exist_ok=True)
        counts = {}
        for i in sorted(set(ids)):
            row = by_id.get(i)
            if not row:
                print(f"  ?      unknown skill: {i}")
                continue
            st, msg = (uninstall_one(row, root, a.dry_run) if a.uninstall
                       else install_one(row, cache, root, a.dry_run, a.force,
                                        a.commercial_only))
            counts[st] = counts.get(st, 0) + 1
            print(f"  {st:<6} {msg}")
        print(f"  -- {counts}")

    if a.agents:
        print(f"\n== agents: {os.path.join(claude_home(), 'agents')}")
        install_agents(a.dry_run)


if __name__ == "__main__":
    main()
