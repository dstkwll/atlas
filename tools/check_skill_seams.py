#!/usr/bin/env python3
"""Check first-party Atlas skill/reference contracts for executable drift.

The generic check keeps reference templates governed by their skill. The
cross-skill check binds Stage 0–2 candidate, control, and review shapes to the
controller's literal schemas.
"""
from __future__ import annotations

import ast
import json
import re
import sys
import tempfile
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "plugins" / "atlas" / "skills"
RULE_WORDS = re.compile(
    r"\b(carr(?:y|ies|ying)|record(?:s|ed|ing)?|set(?:s|ting)?|writ(?:e|es|ten|ing)|"
    r"nam(?:e|es|ing)|state(?:s|d)?|declare(?:s|d)?|hold(?:s)?|required|must|never|"
    r"append(?:s|ed)?|populate(?:s|d)?|match(?:es|ed|ing)?)\b",
    re.I,
)


def sentences_naming(text: str, token: str) -> list[str]:
    pattern = re.compile(r"(?<![\w-])" + re.escape(token) + r"(?![\w-])")
    return [
        " ".join(chunk.split())
        for chunk in re.split(r"(?<=[.!?])\s+|\n\n", text)
        if pattern.search(chunk)
    ]


def template_blocks(reference: str) -> list[tuple[str, str]]:
    blocks = [("YAML template", block) for block in re.findall(r"```yaml\n(.*?)```", reference, re.S)]
    blocks += [
        ("frontmatter template", block)
        for block in re.findall(r"(?:^|\n)---\n(.*?)\n---(?:\n|$)", reference, re.S)
    ]
    return blocks


def template_fields(reference: str) -> list[str]:
    fields: set[str] = set()
    for _, block in template_blocks(reference):
        stack: list[tuple[int, str]] = []
        lines = block.splitlines()
        for index, line in enumerate(lines):
            match = re.match(r"^(\s*)(?:-\s+)?([a-z_][a-z0-9_-]*):", line)
            if not match:
                continue
            indent = len(match.group(1))
            key = match.group(2)
            while stack and stack[-1][0] >= indent:
                stack.pop()
            value = line[match.end():].strip()
            path = ".".join([item[1] for item in stack] + [key])
            if value:
                fields.add(path)
            elif index + 1 < len(lines):
                following = lines[index + 1]
                if len(following) - len(following.lstrip()) > indent and re.match(r"^\s*-\s+[^:]+$", following):
                    fields.add(path)
            if not value or value.startswith("<complete recommended gate map"):
                stack.append((indent, key))
    return sorted(fields)


def template_yaml_errors(reference: str) -> list[str]:
    errors = []
    for index, (kind, block) in enumerate(template_blocks(reference), 1):
        try:
            yaml.safe_load(block)
        except yaml.YAMLError as exc:
            errors.append(f"{kind} block {index} is invalid: {str(exc).splitlines()[0]}")
    return errors


def frontmatter_maps(reference: str) -> list[dict[str, Any]]:
    maps = []
    for block in re.findall(r"(?:^|\n)---\n(.*?)\n---(?:\n|$)", reference, re.S):
        value = yaml.safe_load(block)
        if isinstance(value, dict):
            maps.append(value)
    return maps


def json_maps(reference: str) -> list[dict[str, Any]]:
    maps = []
    for block in re.findall(r"```json\n(.*?)```", reference, re.S):
        value = json.loads(block)
        if isinstance(value, dict):
            maps.append(value)
    return maps


def assigned_literal(source: str, name: str):
    tree = ast.parse(source)
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == name for target in node.targets
        ):
            return ast.literal_eval(node.value)
    raise ValueError(f"missing literal assignment: {name}")


def mandated_values(skill: str) -> list[str]:
    values = set(re.findall(r"`([A-Z][A-Z-]{2,})`", skill))
    values.update(re.findall(r"`([a-z]+(?:-[a-z]+)+)`", skill))
    return sorted(values)


def check(skill_dir: Path) -> list[tuple[str, str]]:
    findings: list[tuple[str, str]] = []
    skill = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    refs = sorted((skill_dir / "references").glob("*.md")) if (skill_dir / "references").is_dir() else []
    if not refs:
        return [("skipped", f"{skill_dir.name}: no reference files — check does not apply")]
    joined = "\n".join(path.read_text(encoding="utf-8") for path in refs)
    for ref in refs:
        text = ref.read_text(encoding="utf-8")
        for error in template_yaml_errors(text):
            findings.append(("template-yaml", f"{skill_dir.name}/{ref.name}: {error}"))
        try:
            json_maps(text)
        except json.JSONDecodeError as exc:
            findings.append(("template-json", f"{skill_dir.name}/{ref.name}: invalid JSON template: {exc.msg}"))
        for field in template_fields(text):
            token = field.rsplit(".", 1)[-1]
            naming = sentences_naming(skill, token)
            if not naming:
                findings.append(("forward", f"{skill_dir.name}/{ref.name}: `{field}` defined in template, ungoverned"))
            elif not any(RULE_WORDS.search(sentence) for sentence in naming):
                findings.append(("forward-weak", f"{skill_dir.name}/{ref.name}: `{field}` mentioned but no rule"))
    for value in mandated_values(skill):
        if not sentences_naming(joined, value):
            findings.append(("reverse", f"{skill_dir.name}: skill mandates `{value}` with no home in any template"))
    return findings


def cross_skill_contracts(skills: Path) -> list[tuple[str, str]]:
    findings: list[tuple[str, str]] = []
    paths = {
        "start": skills / "start-run" / "SKILL.md",
        "state": skills / "start-run" / "references" / "state-file.md",
        "amendment": skills / "start-run" / "references" / "run-amendment.md",
        "discovery": skills / "discovery" / "SKILL.md",
        "discovery-template": skills / "discovery" / "references" / "run-layout.md",
        "prd-template": skills / "discovery" / "references" / "prd-file.md",
        "control": skills / "control-run" / "SKILL.md",
        "review": skills / "control-run" / "references" / "boundary-review.md",
        "intake-correction": skills.parent / "references" / "intake-correction.md",
        "spike": skills / "spike" / "SKILL.md",
        "controller": skills.parent / "tools" / "atlas_control.py",
        "renderer": skills.parent / "tools" / "render_prd.py",
    }
    texts: dict[str, str] = {}
    for name, path in paths.items():
        if not path.is_file():
            findings.append(("cross", f"missing first-party seam file: {path}"))
        else:
            texts[name] = path.read_text(encoding="utf-8")

    required = {
        "start": ["run.yaml", "control.json", "initialize", "AGENT_REVIEW", "HUMAN", "AUTO"],
        "state": ["control.json", "base_run_sha256", "accepted_amendment_count", "acceptances"],
        "amendment": ["amendments/NNN-", "accepted amendment count", "No `previous`"],
        "discovery": ["producer", "read-only", "gate_ready", "status: draft", "control.json", "20-prd.md", "render_prd.py"],
        "discovery-template": ["Cold-read evidence"],
        "prd-template": ["derived_from", "Goals and outcomes", "Acceptance outcomes"],
        "control": ["read-only", "AGENT_REVIEW", "HUMAN", "One invocation", "atomic", "no transaction journal"],
        "review": ["candidate_version", "candidate_sha256", "PASS", "BLOCKED", "resume_stage", "resume_action"],
        "intake-correction": [".20-prd.next.md", "mark-stale", "apply-amendment", "run.yaml remains byte-for-byte unchanged"],
        "spike": ["authoritative `control.json`", "accepted_amendment_count", "ignore `00-state.md`"],
        "controller": ["def initialize", "def check", "def advance", "def reject", "def mark_stale", "def apply_amendment"],
        "renderer": ["def write_canonical", "def render", "def verify", "RENDERER_VERSION"],
    }
    for name, needles in required.items():
        text = texts.get(name, "")
        for needle in needles:
            if needle.lower() not in text.lower():
                findings.append(("cross", f"{name}: missing seam contract `{needle}`"))

    try:
        controller_candidates = assigned_literal(texts.get("controller", ""), "CANDIDATE_FIELDS")
        control_fields = set(assigned_literal(texts.get("controller", ""), "CONTROL_FIELDS"))
        acceptance_fields = set(assigned_literal(texts.get("controller", ""), "ACCEPTANCE_FIELDS"))
        review_fields = set(assigned_literal(texts.get("controller", ""), "REVIEW_FIELDS"))
        gap_fields = set(assigned_literal(texts.get("controller", ""), "GAP_FIELDS"))
        controller_renderer_version = assigned_literal(texts.get("controller", ""), "RENDERER_VERSION")
        renderer_version = assigned_literal(texts.get("renderer", ""), "RENDERER_VERSION")
    except (SyntaxError, ValueError) as exc:
        findings.append(("cross", f"controller schemas are unreadable: {exc}"))
    else:
        if controller_renderer_version != renderer_version:
            findings.append(("cross", "controller and renderer version contracts differ"))
        discovery_maps = [
            set(item) for item in frontmatter_maps(texts.get("discovery-template", ""))
            if {"run", "version"}.issubset(item)
        ]
        prd_maps = [
            set(item) for item in frontmatter_maps(texts.get("prd-template", ""))
            if {"run", "version", "status", "gate_ready"}.issubset(item)
        ]
        if set({"run", "version"}) not in discovery_maps:
            findings.append(("cross", "discovery decision-log schema is missing required run/version frontmatter"))
        if set(controller_candidates["discovery"]) not in prd_maps:
            findings.append(("cross", "discovery candidate schema does not match controller CANDIDATE_FIELDS"))

        try:
            state_maps = json_maps(texts.get("state", ""))
            review_maps = json_maps(texts.get("review", ""))
        except json.JSONDecodeError as exc:
            findings.append(("cross", f"JSON seam template is invalid: {exc.msg}"))
        else:
            if not state_maps or set(state_maps[0]) != control_fields:
                present = set(state_maps[0]) if state_maps else set()
                findings.append(("cross", f"control.json template does not match controller CONTROL_FIELDS; missing={sorted(control_fields - present)}"))
            if state_maps and (
                not isinstance(state_maps[0].get("acceptances"), dict)
                or set(state_maps[0]["acceptances"]) != set(controller_candidates)
            ):
                findings.append(("cross", "control.json acceptances do not define the current stage bindings"))
            acceptance_maps = [item for item in state_maps if acceptance_fields.issubset(item)]
            if len(acceptance_maps) != 1 or set(acceptance_maps[0]) != acceptance_fields:
                present = set(acceptance_maps[0]) if acceptance_maps else set()
                findings.append(("cross", f"acceptance template does not match controller ACCEPTANCE_FIELDS; missing={sorted(acceptance_fields - present)}"))
            for item in review_maps:
                if set(item) != review_fields:
                    findings.append(("cross", "boundary review schema does not match controller REVIEW_FIELDS"))
                gaps = item.get("gaps", [])
                if gaps and any(not isinstance(gap_item, dict) or set(gap_item) != gap_fields for gap_item in gaps):
                    findings.append(("cross", "boundary review gap schema does not match controller GAP_FIELDS"))

    joined = "\n".join(texts.values())
    banned = {
        "approved_copy": "approved-copy machinery is not part of Stage 0–2",
        "recover_transaction": "transaction replay machinery is not part of Stage 0–2",
        "write_files_atomic": "multi-file transaction machinery is not part of Stage 0–2",
        "<planning-root>/<project>/runs": "feature layout is fixed beneath planning root",
    }
    for phrase, reason in banned.items():
        if phrase.lower() in joined.lower():
            findings.append(("cross", f"legacy contract `{phrase}` remains — {reason}"))

    if (skills / "to-spec").exists():
        findings.append(("cross", "to-spec remains in the Atlas plugin after product-closure migration"))

    for name in ("discovery",):
        for sentence in re.split(r"(?<=[.!?])\s+|\n+", texts.get(name, "")):
            lower = sentence.lower()
            if "run.yaml" not in lower:
                continue
            mutates = re.search(r"\b(?:update|edit|modify|rewrite|append|write|replace|change|overwrite|revise|amend|mutate)\b", lower)
            negated = any(word in lower for word in ("do not", "never", "unchanged", "immutable"))
            if mutates and not negated:
                findings.append(("cross", f"{name}: stage skill may not mutate immutable run.yaml — {sentence.strip()}"))
    return findings


def self_test() -> bool:
    ok = True
    with tempfile.TemporaryDirectory() as td:
        skill = Path(td) / "fake"
        (skill / "references").mkdir(parents=True)
        (skill / "SKILL.md").write_text("The widget is required.\n", encoding="utf-8")
        (skill / "references" / "shape.md").write_text("```yaml\nwidget: one\nmissing: two\n```\n", encoding="utf-8")
        if not any(kind == "forward" for kind, _ in check(skill)):
            print("SELF-TEST FAIL: ungoverned template field was invisible")
            ok = False
        (skill / "references" / "shape.md").write_text("```yaml\nwidget: [\n```\n", encoding="utf-8")
        if not any(kind == "template-yaml" for kind, _ in check(skill)):
            print("SELF-TEST FAIL: malformed YAML was invisible")
            ok = False
        if set(template_fields("```yaml\nroot:\n  child: x\n```\n")) != {"root.child"}:
            print("SELF-TEST FAIL: nested field extraction failed")
            ok = False
    return ok


def main() -> int:
    if "--self-test" in sys.argv:
        ok = self_test()
        print("self-test:", "OK" if ok else "FAILED")
        return 0 if ok else 2
    if not self_test():
        print("refusing to report: the checker's own self-test failed")
        return 2
    findings = cross_skill_contracts(SKILLS)
    hard_kinds = {"forward", "reverse", "cross", "template-yaml", "template-json"}
    hard = [item for item in findings if item[0] in hard_kinds]
    soft = [item for item in findings if item[0] == "forward-weak"]
    skipped = [item for item in findings if item[0] == "skipped"]
    for kind, message in hard + soft + skipped:
        print(f"{kind:13} {message}")
    print(f"\n{len(hard)} findings, {len(soft)} weak, {len(skipped)} skipped")
    return 1 if hard else 0


if __name__ == "__main__":
    raise SystemExit(main())
