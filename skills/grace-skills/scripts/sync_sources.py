#!/usr/bin/env python3
"""Clone or update the seven Grace9393 source repos into a LOCAL cache.

The cache deliberately does NOT live on H:\\My Drive — that path is a Google
Drive File Stream mount at ~10 ms per file stat, and these repos total ~250k
files. Default cache is %LOCALAPPDATA%\\grace-skill-pack\\sources (Windows) or
~/.cache/grace-skill-pack/sources (POSIX).

Usage:
    python sync_sources.py                  # clone/pull everything
    python sync_sources.py --only dbskill khazix-skills
    python sync_sources.py --cache D:\\src   # override cache location
"""
import argparse
import os
import subprocess
import sys

OWNER = "Grace9393"

# name -> sparse-checkout paths. None = full shallow clone.
# superset and crawl4ai are large product repos; we only need their skill dirs
# (superset additionally fails a full checkout on Windows with
# "Filename too long", hence core.longpaths + sparse).
REPOS = {
    "dbskill": None,
    "openakita": ["skills", "plugins", "examples/plugins"],
    "khazix-skills": None,
    "notebooklm-skill": None,
    "superset": [".agents", "plugins/superset/skills"],
    "crawl4ai": ["docs", "prompts"],
    "finger-frame-effect-lucy": None,
}


def default_cache():
    base = os.environ.get("LOCALAPPDATA") or os.path.join(
        os.path.expanduser("~"), ".cache")
    return os.path.join(base, "grace-skill-pack", "sources")


def run(args, cwd=None):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True)


def sync(name, sparse, cache):
    dest = os.path.join(cache, name)
    url = f"https://github.com/{OWNER}/{name}.git"
    git = ["git", "-c", "core.longpaths=true"]
    if os.path.isdir(os.path.join(dest, ".git")):
        r = run(git + ["pull", "--depth", "1", "--ff-only"], cwd=dest)
        print(f"[{name}] pull: {(r.stdout or r.stderr).strip().splitlines()[-1:] or ['ok']}")
        return dest
    clone = git + ["clone", "--depth", "1", "--quiet"]
    if sparse:
        clone += ["--filter=blob:none", "--sparse"]
    r = run(clone + [url, dest])
    if r.returncode and not os.path.isdir(dest):
        print(f"[{name}] CLONE FAILED: {r.stderr.strip()}", file=sys.stderr)
        return None
    if sparse:
        run(git + ["sparse-checkout", "init", "--cone"], cwd=dest)
        run(git + ["sparse-checkout", "set"] + sparse, cwd=dest)
        run(git + ["checkout", "HEAD", "--"] + sparse, cwd=dest)
    print(f"[{name}] cloned -> {dest}")
    return dest


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default=default_cache())
    ap.add_argument("--only", nargs="*")
    a = ap.parse_args()
    os.makedirs(a.cache, exist_ok=True)
    names = a.only or list(REPOS)
    for n in names:
        if n not in REPOS:
            print(f"unknown repo: {n}", file=sys.stderr)
            continue
        sync(n, REPOS[n], a.cache)
    print(f"\ncache: {a.cache}")


if __name__ == "__main__":
    main()
