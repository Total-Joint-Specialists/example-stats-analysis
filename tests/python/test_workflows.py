"""Every GitHub Action a workflow uses must resolve to a real tag or branch.
An unresolvable ref fails CI at "Set up job", silently disabling every check."""

import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
USES = re.compile(r"^\s*-?\s*uses:\s*([\w.-]+/[\w.-]+)(?:/[\w./-]+)?@([\w.-]+)", re.MULTILINE)


def action_refs():
    refs = set()
    for wf in sorted((ROOT / ".github" / "workflows").glob("*.yml")):
        refs.update(USES.findall(wf.read_text(encoding="utf-8")))
    return sorted(refs)


@pytest.mark.parametrize("repo,ref", action_refs(), ids=lambda x: str(x))
def test_action_ref_resolves(repo, ref):
    try:
        out = subprocess.run(
            ["git", "ls-remote", f"https://github.com/{repo}", f"refs/tags/{ref}", f"refs/heads/{ref}"],
            capture_output=True, text=True, timeout=30,
        )
    except subprocess.TimeoutExpired:
        pytest.skip("GitHub unreachable")
    if out.returncode != 0:
        pytest.skip(f"GitHub unreachable: {out.stderr.strip()[:80]}")
    assert out.stdout.strip(), f"{repo}@{ref} does not resolve to a tag or branch"
