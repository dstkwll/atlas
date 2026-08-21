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
        "run-file": skills / "start-run" / "references" / "run-file.md",
        "state": skills / "start-run" / "references" / "state-file.md",
        "amendment": skills / "start-run" / "references" / "run-amendment.md",
        "discovery": skills / "discovery" / "SKILL.md",
        "decision-record": skills / "discovery" / "references" / "decision-record.md",
        "discovery-template": skills / "discovery" / "references" / "run-layout.md",
        "prd-template": skills / "discovery" / "references" / "prd-file.md",
        "control": skills / "control-run" / "SKILL.md",
        "review": skills / "control-run" / "references" / "boundary-review.md",
        "intake-correction": skills.parent / "references" / "intake-correction.md",
        "setup": skills / "setup-atlas" / "SKILL.md",
        "spike": skills / "spike" / "SKILL.md",
        "spike-findings": skills / "spike" / "references" / "findings-file.md",
        "controller": skills.parent / "tools" / "atlas_control.py",
        "planning": skills.parent / "tools" / "atlas_planning.py",
        "system-design": skills / "system-design" / "SKILL.md",
        "system-design-template": skills / "system-design" / "references" / "system-design-file.md",
        "system-design-board": skills / "system-design" / "references" / "system-design-board.md",
        "system-design-agent": skills / "system-design" / "agents" / "openai.yaml",
        "control-planning": skills / "control-planning" / "SKILL.md",
        "system-design-authority": skills / "control-planning" / "references" / "system-design-authority.md",
        "control-planning-agent": skills / "control-planning" / "agents" / "openai.yaml",
        "renderer": skills.parent / "tools" / "render_prd.py",
        "system-renderer": skills.parent / "tools" / "render_system_design.py",
    }
    texts: dict[str, str] = {}
    for name, path in paths.items():
        if not path.is_file():
            findings.append(("cross", f"missing first-party seam file: {path}"))
        else:
            texts[name] = path.read_text(encoding="utf-8")

    required = {
        "start": [
            "run.yaml", "control.json", "initialize", "AGENT_REVIEW", "HUMAN", "AUTO",
            "atlas_planning.py", "planning-control.json", ".atlas-planning.lock",
        ],
        "run-file": [
            "[a-z0-9]+(?:-[a-z0-9]+)*", "rejects path separators",
            "version: 2", "system_design_participation: agent_led",
        ],
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
        "planning": [
            'PLANNING_FILE = "planning-control.json"',
            'PLANNING_LOCK_FILE = ".atlas-planning.lock"',
            "def load_planning_control", "def initialize_planning", "def check_boundary",
            "def advance_boundary", 'SYSTEM_DESIGN_FILE = "30-system-design.md"',
            "verify_system_design_board", "30-system-design.html",
        ],
        "system-design": [
            "disable-model-invocation: true", "third parent of this file", "agent_led",
            "co_design", "Slice 2", "references/system-design-file.md", "references/system-design-board.md",
            "gate_ready: true", "render_system_design.py", ".30-system-design.next.md",
            "atlas:control-planning", "without asking the user to issue a second command",
        ],
        "system-design-template": [
            "run: <feature-slug>", "version: 1", "status: draft", "gate_ready: false",
            "participation: agent_led", "source_binding:", "kind: product_closure",
            "kind: stage0", "effective_config_hash", "effective_config_revision",
        ],
        "system-design-agent": ["allow_implicit_invocation: false"],
        "system-design-board": [
            "30-system-design.md", "30-system-design.html", "Inapplicable:",
            "non-authoritative", "no independent acceptance hash",
        ],
        "control-planning": [
            "disable-model-invocation: true", "third parent of this file", "never routes",
            "never synthesizes", "never edits", "never grades prose", "explicit human approval",
            "agent_led", "co_design", "30-system-design.html", "non-authoritative",
            "atlas_planning.py", "advance --run", "--approval human", "--date",
            "re-read `planning-control.json`", "AGENT_REVIEW", "HUMAN_IF_CHANGED", "Slice 2",
            "fresh read-only classifier", "distinct fresh semantic reviewer", "invoker assembles",
            "reviews/system-design-v1.json",
        ],
        "system-design-authority": [
            "reviews/system-design-v1.json", "candidate_version", "candidate_sha256",
            "repository_baselines", "materiality", "semantic_review", "unavailable_reason",
            "MATERIAL", "NOT_MATERIAL", "UNAVAILABLE", "PASS", "BLOCKED",
        ],
        "control-planning-agent": ["allow_implicit_invocation: false"],
        "renderer": ["def write_canonical", "def render", "def verify", "RENDERER_VERSION"],
        "system-renderer": [
            "def write_canonical", "def render", "def verify", "RENDERER_VERSION",
            'SOURCE_FILE = "30-system-design.md"', 'OUTPUT_FILE = "30-system-design.html"',
            "REQUIRED_VIEWS", "atlas-source", "atlas-source-sha256", "atlas-renderer-version",
        ],
    }
    for name, needles in required.items():
        text = texts.get(name, "")
        for needle in needles:
            if needle.lower() not in text.lower():
                findings.append(("cross", f"{name}: missing seam contract `{needle}`"))

    planning_command = 'python3 "<atlas-plugin-root>/tools/atlas_planning.py" initialize --run "<path>"'
    if planning_command not in texts.get("start", ""):
        findings.append(("cross", "start: missing planning initialize command with installed-root/CWD contract"))
    check_command = 'python3 "<atlas-plugin-root>/tools/atlas_planning.py" check --run "<run-directory>" --stage system_design'
    advance_command = 'python3 "<atlas-plugin-root>/tools/atlas_planning.py" advance --run "<run-directory>" --stage system_design --approval human --date "<YYYY-MM-DD>"'
    for name in ("system-design", "control-planning"):
        if check_command not in texts.get(name, ""):
            findings.append(("cross", f"{name}: missing caller-CWD-independent System Design check command"))
    if advance_command not in texts.get("control-planning", ""):
        findings.append(("cross", "control-planning: missing exact HUMAN System Design advance command"))
    for command in (
        'advance --run "<run-directory>" --stage system_design --review reviews/system-design-v1.json --date "<YYYY-MM-DD>"',
        'advance --run "<run-directory>" --stage system_design --review reviews/system-design-v1.json --approval human --date "<YYYY-MM-DD>"',
    ):
        if command not in texts.get("control-planning", ""):
            findings.append(("cross", f"control-planning: missing System Design authority-matrix command `{command}`"))
    renderer_commands = (
        'python3 "<atlas-plugin-root>/tools/render_system_design.py" write --run "<run-directory>" --draft .30-system-design.next.md',
        'python3 "<atlas-plugin-root>/tools/render_system_design.py" render --run "<run-directory>"',
        'python3 "<atlas-plugin-root>/tools/render_system_design.py" verify --run "<run-directory>"',
    )
    for command in renderer_commands:
        if command not in texts.get("system-design", ""):
            findings.append(("cross", f"system-design: missing caller-CWD-independent renderer command `{command}`"))
    producer = texts.get("system-design", "")
    if producer.count("atlas:control-planning") != 1 or "without asking the user to issue a second command" not in producer:
        findings.append(("cross", "system-design: missing exact internal control-planning handoff without a second user command"))
    try:
        run_v2_fields = set(assigned_literal(texts.get("controller", ""), "RUN_V2_FIELDS"))
        run_maps = [
            value for _, block in template_blocks(texts.get("run-file", ""))
            if isinstance((value := yaml.safe_load(block)), dict) and value.get("version") == 2
        ]
    except (SyntaxError, ValueError, yaml.YAMLError) as exc:
        findings.append(("cross", f"run.yaml v2 schema seam is unreadable: {exc}"))
    else:
        present = set(run_maps[0]) if run_maps else set()
        if len(run_maps) != 1 or present != run_v2_fields:
            findings.append(("cross", f"run.yaml v2 template does not match controller RUN_V2_FIELDS; missing={sorted(run_v2_fields - present)}"))

    try:
        system_fields = set(assigned_literal(texts.get("planning", ""), "SYSTEM_DESIGN_FIELDS"))
        product_source_fields = set(assigned_literal(texts.get("planning", ""), "PRODUCT_SOURCE_FIELDS"))
        stage0_source_fields = set(assigned_literal(texts.get("planning", ""), "STAGE0_SOURCE_FIELDS"))
        system_sections = tuple(assigned_literal(texts.get("planning", ""), "SYSTEM_DESIGN_SECTIONS"))
        candidate_maps = [
            item for item in frontmatter_maps(texts.get("system-design-template", ""))
            if {"run", "version", "status", "gate_ready"}.issubset(item)
        ]
        source_maps = [
            item.get("source_binding") for item in candidate_maps
            if isinstance(item.get("source_binding"), dict)
        ]
        source_maps += [
            item.get("source_binding") for _, block in template_blocks(texts.get("system-design-template", ""))
            if isinstance((item := yaml.safe_load(block)), dict)
            and isinstance(item.get("source_binding"), dict)
        ]
    except (SyntaxError, ValueError, yaml.YAMLError) as exc:
        findings.append(("cross", f"System Design candidate schema seam is unreadable: {exc}"))
    else:
        present = set(candidate_maps[0]) if candidate_maps else set()
        if len(candidate_maps) != 1 or present != system_fields:
            findings.append(("cross", f"System Design candidate schema does not match planning SYSTEM_DESIGN_FIELDS; missing={sorted(system_fields - present)}"))
        source_shapes = {frozenset(item) for item in source_maps if isinstance(item, dict)}
        expected_shapes = {frozenset(product_source_fields), frozenset(stage0_source_fields)}
        if source_shapes != expected_shapes:
            findings.append(("cross", "System Design source_binding templates do not match both discriminated planning schemas"))
        headings = tuple(re.findall(r"(?m)^## ([^\n]+?)\s*$", texts.get("system-design-template", "")))
        if headings != system_sections:
            findings.append(("cross", "System Design template sections do not match planning SYSTEM_DESIGN_SECTIONS"))
        governed = texts.get("system-design", "")
        for field in sorted(system_fields | product_source_fields | stage0_source_fields):
            if not sentences_naming(governed, field):
                findings.append(("cross", f"system-design: template field `{field}` is ungoverned"))

    try:
        board_views = tuple(assigned_literal(texts.get("system-renderer", ""), "REQUIRED_VIEWS"))
        board_labels = tuple(item[0] for item in board_views)
        board_sections = {section for _, _, sections in board_views for section in sections}
        system_sections = set(assigned_literal(texts.get("planning", ""), "SYSTEM_DESIGN_SECTIONS"))
    except (SyntaxError, ValueError, TypeError, IndexError) as exc:
        findings.append(("cross", f"System Design board views are unreadable: {exc}"))
    else:
        board_text = texts.get("system-design-board", "")
        skill_text = texts.get("system-design", "")
        if (
            len(board_labels) != len(set(board_labels))
            or any(label not in board_text for label in board_labels)
            or any(label not in skill_text and "stable label" not in skill_text for label in board_labels)
        ):
            findings.append(("cross", "System Design board views do not match renderer, reference, and skill contracts"))
        if not board_sections.issubset(system_sections):
            findings.append(("cross", "System Design board source sections are outside planning SYSTEM_DESIGN_SECTIONS"))

    try:
        review_reference = assigned_literal(texts.get("planning", ""), "SYSTEM_DESIGN_REVIEW_REFERENCE")
        review_fields = set(assigned_literal(texts.get("planning", ""), "SYSTEM_DESIGN_REVIEW_FIELDS"))
        dimensions = tuple(assigned_literal(texts.get("planning", ""), "SYSTEM_DESIGN_DIMENSIONS"))
        materiality_fields = set(assigned_literal(texts.get("planning", ""), "MATERIALITY_FIELDS"))
        semantic_fields = set(assigned_literal(texts.get("planning", ""), "SEMANTIC_REVIEW_FIELDS"))
        dimension_fields = set(assigned_literal(texts.get("planning", ""), "DIMENSION_REVIEW_FIELDS"))
        semantic_gap_fields = set(assigned_literal(texts.get("planning", ""), "SEMANTIC_GAP_FIELDS"))
        authority_maps = json_maps(texts.get("system-design-authority", ""))
    except (SyntaxError, ValueError, json.JSONDecodeError) as exc:
        findings.append(("cross", f"System Design authority schema seam is unreadable: {exc}"))
    else:
        envelopes = [item for item in authority_maps if {"candidate_version", "materiality", "semantic_review"}.issubset(item)]
        envelope = envelopes[0] if len(envelopes) == 1 else {}
        materiality = envelope.get("materiality") if isinstance(envelope, dict) else None
        semantic = envelope.get("semantic_review") if isinstance(envelope, dict) else None
        material_rows = materiality.get("dimensions") if isinstance(materiality, dict) else None
        semantic_rows = semantic.get("dimensions") if isinstance(semantic, dict) else None
        gap_maps = [item for item in authority_maps if set(item) == semantic_gap_fields]
        if review_reference != "reviews/system-design-v1.json" or review_reference not in texts.get("system-design-authority", ""):
            findings.append(("cross", "System Design authority filename is not exact across controller and reference"))
        if set(envelope) != review_fields:
            findings.append(("cross", "System Design authority envelope does not match planning schema"))
        if not isinstance(materiality, dict) or set(materiality) != materiality_fields:
            findings.append(("cross", "System Design materiality reference does not match planning schema"))
        for label, rows in (("materiality", material_rows), ("semantic review", semantic_rows)):
            if (
                not isinstance(rows, list)
                or len(rows) != len(dimensions)
                or any(not isinstance(row, dict) or set(row) != dimension_fields for row in rows)
                or {row.get("dimension") for row in rows} != set(dimensions)
            ):
                findings.append(("cross", f"System Design {label} dimensions do not match the exact D-073 identifiers"))
        if not isinstance(semantic, dict) or set(semantic) != semantic_fields:
            findings.append(("cross", "System Design semantic review reference does not match planning schema"))
        if len(gap_maps) != 1:
            findings.append(("cross", "System Design semantic gap reference does not match planning schema"))

    for name in ("system-design", "control-planning"):
        count = len(texts.get(name, "").splitlines())
        if not 70 <= count <= 110:
            findings.append(("cross", f"{name}: SKILL.md line count {count} is outside 70-110"))
    if re.search(r"\b(?:must|never|required)\b", texts.get("system-design-template", ""), re.I):
        findings.append(("cross", "System Design reference is not shape-only"))

    operating_required = {
        "discovery": [
            "Work in rounds", "**The problem test.**", "**The announcement test.**",
            "Propose candidate shapes", "never manufacture a recommendation",
            "cite the evidence that resolved it", "Give the fresh reader only `10-decisions.md`",
            "Nothing important exists only in the conversation", "third parent of this file",
        ],
        "decision-record": ["justified recommendation or explicitly says that none is supportable"],
        "start": [
            "Never overwrite an existing `run.yaml`", "Stage 0 is recommend-only",
            "every other repository already known to be affected", "short, descriptive, stable",
            "does not imply an exact stage sequence or gate map", "ask rather than invent policy",
            "current `control.json.phase`", "`STALE`", "`REJECTED`",
            "no first-party Atlas owner", "never substitute an incubator skill",
            "third parent of this file", "resolve-run-path", "before writing `run.yaml`",
            "pass the unchanged device/inode values", "--prepared-device", "--prepared-inode",
        ],
        "control": [
            "report the exact error and stop", "Never emulate transition logic",
            "structured `BLOCKED`", "expected check outcome",
            "run.yaml.gates.discovery.authority",
            "reject --run", "--reason", "third parent of this file",
        ],
        "setup": ["atomic contract-plus-code commits", "third parent of this file", "<atlas-plugin-root>/requirements.txt"],
        "spike": ["no executable spike runner", "agent-enforced procedure", "state confidence"],
        "spike-findings": ["**Confidence:**"],
    }
    for name, needles in operating_required.items():
        text = texts.get(name, "")
        for needle in needles:
            if needle.lower() not in text.lower():
                findings.append(("cross", f"{name}: missing operating contract `{needle}`"))

    relative_packaged_resources = ("python3 tools/", "py -3 tools/", "plugins/atlas/requirements.txt")
    for path in skills.parent.rglob("*.md"):
        source = path.read_text(encoding="utf-8")
        if any(needle in source for needle in relative_packaged_resources):
            findings.append(("cross", f"{path}: caller-CWD-dependent packaged resource; resolve it from <atlas-plugin-root>"))

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
