#!/usr/bin/env python3
"""Check that a skill and its reference files agree.

Two directions, because each misses what the other catches:

  forward  every field a reference template defines is governed by a rule in SKILL.md
  reverse  every value the skill mandates has somewhere in a template to land

Both match on WORD BOUNDARIES, not substrings. A substring check reports a pass it
has not earned: `id` matches "idea", `date` matches "validate", `opened` matches
"reopened". All three were counted as governed before this was written.

Governance also requires more than a mention. A field is governed when the skill
names it AND the naming sentence says something about writing it — when it is set,
what it holds, or what it must be. A field appearing only inside a path or a prose
aside is reported as MENTIONED, not governed.

Run:  python3 tools/check_skill_seams.py [--self-test]
Exit: 0 clean, 1 findings, 2 self-test failed.
"""
from __future__ import annotations
import re, sys, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "plugins" / "atlas" / "skills"

# a naming sentence must carry one of these to count as a rule rather than a mention
RULE_WORDS = re.compile(
    r"\b(carr(?:y|ies|ying)|record(?:s|ed|ing)?|set(?:s|ting)?|writ(?:e|es|ten|ing)|"
    r"nam(?:e|es|ing)|state(?:s|d)?|declare(?:s|d)?|hold(?:s)?|flip(?:s)?|"
    r"assign(?:ed|s)?|required|must|never|append(?:s|ed)?|populate(?:s|d)?)\b", re.I)


def words(text: str) -> set[str]:
    return set(re.findall(r"[A-Za-z_][A-Za-z0-9_-]*", text))


def sentences_naming(text: str, token: str) -> list[str]:
    """Sentences where token appears as a whole word."""
    pat = re.compile(r"(?<![\w-])" + re.escape(token) + r"(?![\w-])")
    out = []
    for chunk in re.split(r"(?<=[.!?])\s+|\n\n", text):
        if pat.search(chunk):
            out.append(" ".join(chunk.split()))
    return out


def template_fields(ref: str) -> list[str]:
    """YAML keys the reference's template block defines."""
    block = re.search(r"```yaml\n(.*?)```", ref, re.S) or re.search(r"---\n(.*?)\n---", ref, re.S)
    if not block:
        return []
    return sorted({m for m in re.findall(r"^([a-z_][a-z0-9_]*):", block.group(1), re.M)})


def mandated_values(skill: str) -> list[str]:
    """Enum-ish values the skill mandates: backticked ALL-CAPS or hyphenated tokens.

    Derived from the text rather than hand-listed, so a value the author forgot to
    think about is still checked.
    """
    vals = set()
    for m in re.findall(r"`([A-Z][A-Z-]{2,})`", skill):          # VALIDATED, MIXED
        vals.add(m)
    for m in re.findall(r"`([a-z]+(?:-[a-z]+)+)`", skill):        # user-rejected, load-bearing
        vals.add(m)
    return sorted(vals)


def check(skill_dir: Path) -> list[tuple[str, str]]:
    findings: list[tuple[str, str]] = []
    skill = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    refs = sorted((skill_dir / "references").glob("*.md")) if (skill_dir / "references").is_dir() else []
    if not refs:
        findings.append(("skipped", f"{skill_dir.name}: no reference files — check does not apply"))
        return findings

    joined = "\n".join(r.read_text(encoding="utf-8") for r in refs)

    for ref in refs:
        text = ref.read_text(encoding="utf-8")
        for field in template_fields(text):
            naming = sentences_naming(skill, field)
            if not naming:
                findings.append(("forward", f"{skill_dir.name}/{ref.name}: `{field}` defined in template, ungoverned"))
            elif not any(RULE_WORDS.search(s) for s in naming):
                findings.append(("forward-weak", f"{skill_dir.name}/{ref.name}: `{field}` mentioned but no rule — {naming[0][:90]}"))

    for value in mandated_values(skill):
        if not sentences_naming(joined, value):
            findings.append(("reverse", f"{skill_dir.name}: skill mandates `{value}` with no home in any template"))

    return findings


def self_test() -> bool:
    """A checker that cannot fail is not a check. Prove each direction fires."""
    import tempfile
    ok = True
    with tempfile.TemporaryDirectory() as td:
        d = Path(td) / "fake"
        (d / "references").mkdir(parents=True)

        # forward: template defines a field the skill never names
        (d / "SKILL.md").write_text("# x\nNothing here names the field.\n", encoding="utf-8")
        (d / "references" / "t.md").write_text("```yaml\nwidget: 1\n```\n", encoding="utf-8")
        if not any(k == "forward" for k, _ in check(d)):
            print("SELF-TEST FAIL: forward did not fire on an ungoverned field"); ok = False

        # forward-weak: named, but with no rule behind the naming
        (d / "SKILL.md").write_text("# x\nThe widget is interesting to consider.\n", encoding="utf-8")
        if not any(k == "forward-weak" for k, _ in check(d)):
            print("SELF-TEST FAIL: forward-weak did not fire on a bare mention"); ok = False

        # substring must NOT count: 'id' inside 'idea'
        (d / "SKILL.md").write_text("# x\nThis idea is good.\n", encoding="utf-8")
        (d / "references" / "t.md").write_text("```yaml\nid: 1\n```\n", encoding="utf-8")
        if not any(k == "forward" for k, _ in check(d)):
            print("SELF-TEST FAIL: 'idea' was accepted as governing 'id'"); ok = False

        # reverse: skill mandates a value no template carries
        (d / "SKILL.md").write_text("# x\nThe verdict is `MIXED` when they disagree.\n", encoding="utf-8")
        (d / "references" / "t.md").write_text("```yaml\nid: 1\n```\nThe id is assigned once.\n", encoding="utf-8")
        if not any(k == "reverse" for k, _ in check(d)):
            print("SELF-TEST FAIL: reverse did not fire on a homeless value"); ok = False

    return ok


def main() -> int:
    if "--self-test" in sys.argv:
        ok = self_test()
        print("self-test:", "OK" if ok else "FAILED")
        return 0 if ok else 2

    if not self_test():
        print("refusing to report: the checker's own self-test failed")
        return 2

    all_findings = []
    for d in sorted(p for p in SKILLS.iterdir() if p.is_dir()):
        all_findings += check(d)

    hard = [f for f in all_findings if f[0] in ("forward", "reverse")]
    soft = [f for f in all_findings if f[0] == "forward-weak"]
    skip = [f for f in all_findings if f[0] == "skipped"]

    for kind, msg in hard + soft + skip:
        print(f"{kind:13} {msg}")
    print(f"\n{len(hard)} findings, {len(soft)} weak, {len(skip)} skipped")
    return 1 if hard else 0


if __name__ == "__main__":
    raise SystemExit(main())
