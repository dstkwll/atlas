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
        "readme": skills.parent / "README.md",
        "plugin-manifest": skills.parent / "plugin.json",
        "codex-plugin-manifest": skills.parent / ".codex-plugin" / "plugin.json",
        "agents-marketplace": skills.parent.parent.parent / ".agents" / "plugins" / "marketplace.json",
        "github-marketplace": skills.parent.parent.parent / ".github" / "plugin" / "marketplace.json",
        "gazetteer": skills / "gazetteer" / "SKILL.md",
        "gazetteer-agent": skills / "gazetteer" / "agents" / "openai.yaml",
        "internal-owner-loading": skills.parent / "references" / "internal-owner-loading.md",
        "gazetteer-helper": skills.parent / "tools" / "atlas_gazetteer.py",
        "start": skills / "start-run" / "SKILL.md",
        "start-agent": skills / "start-run" / "agents" / "openai.yaml",
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
        "setup-agent": skills / "setup-atlas" / "agents" / "openai.yaml",
        "installed-host-calibration": skills / "setup-atlas" / "references" / "installed-host-calibration.md",
        "spike": skills / "spike" / "SKILL.md",
        "spike-findings": skills / "spike" / "references" / "findings-file.md",
        "controller": skills.parent / "tools" / "atlas_control.py",
        "planning": skills.parent / "tools" / "atlas_planning.py",
        "repository": skills.parent / "tools" / "atlas_repository.py",
        "system-design": skills / "system-design" / "SKILL.md",
        "system-design-template": skills / "system-design" / "references" / "system-design-file.md",
        "system-design-board": skills / "system-design" / "references" / "system-design-board.md",
        "system-design-agent": skills / "system-design" / "agents" / "openai.yaml",
        "program-design": skills / "program-design" / "SKILL.md",
        "program-design-template": skills / "program-design" / "references" / "program-design-file.md",
        "program-design-agent": skills / "program-design" / "agents" / "openai.yaml",
        "compile-tickets": skills / "compile-tickets" / "SKILL.md",
        "ticket-graph-template": skills / "compile-tickets" / "references" / "ticket-graph-file.md",
        "compile-tickets-agent": skills / "compile-tickets" / "agents" / "openai.yaml",
        "control-planning": skills / "control-planning" / "SKILL.md",
        "system-design-authority": skills / "control-planning" / "references" / "system-design-authority.md",
        "program-design-authority": skills / "control-planning" / "references" / "program-design-authority.md",
        "ticket-graph-authority": skills / "control-planning" / "references" / "ticket-graph-authority.md",
        "program-design-blocked": skills.parent / "references" / "program-design-blocked.md",
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

    required_plugin_description_clauses = (
        "Gazetteer", "Stage 0", "System", "Program Design", "Stage 5", "ticket graphs"
    )
    try:
        plugin_manifest = json.loads(texts.get("plugin-manifest", ""))
        codex_plugin_manifest = json.loads(texts.get("codex-plugin-manifest", ""))
        agents_marketplace = json.loads(texts.get("agents-marketplace", ""))
        github_marketplace = json.loads(texts.get("github-marketplace", ""))
        agents_atlas = next(
            item for item in agents_marketplace.get("plugins", []) if item.get("name") == "atlas"
        )
        github_atlas = next(
            item for item in github_marketplace.get("plugins", []) if item.get("name") == "atlas"
        )
    except (json.JSONDecodeError, StopIteration, AttributeError) as exc:
        findings.append(("cross", f"Atlas plugin manifests are unreadable: {exc}"))
    else:
        descriptions = (
            plugin_manifest.get("description"),
            codex_plugin_manifest.get("description"),
            agents_atlas.get("description"),
            github_atlas.get("description"),
        )
        if (
            not all(isinstance(item, str) for item in descriptions)
            or len(set(descriptions)) != 1
            or any(clause not in descriptions[0] for clause in required_plugin_description_clauses)
        ):
            findings.append(("cross", "Atlas plugin manifest descriptions do not expose the current Stage 0-5 surface"))

    required = {
        "readme": [
            "First-party Stage 0–5 skills",
            "## Start here",
            "Gazetteer is Atlas's canonical entry point",
            "## Internal/direct skills",
            "| `setup-atlas` | Configure the planning root and verify an installed host. |",
            "| `start-run` | Accept immutable Stage 0 `run.yaml`, initialize control, or resume from authoritative state. |",
            "| `program-design` | Produce the exact Stage 4 candidate, record readiness, and continue the internal control handoff. |",
            "| `compile-tickets` | Compile and hand off the exact Stage 5 ticket graph candidate. |",
            "stops at `READY_FOR_EXECUTION`",
        ],
        "gazetteer": [
            "name: gazetteer", "canonical user-facing entry point", "atlas_gazetteer.py",
            "NEW_GOAL", "CONTINUE", "INSPECT", "ACT_ON_NAMED_WORK", "PROVIDE_JUDGMENT",
            "Semantic similarity may rank or suggest candidates; it never silently binds",
            "Prefer the host's safe nested skill invocation mechanism",
            "load the exact installed sibling `SKILL.md` as the current owner procedure",
            "calibrated procedure-load fallback",
            "Every existing run enters `atlas:start-run` first",
            "Gazetteer never invokes Discovery or a downstream producer directly",
            "Never tell a normal user to invoke `setup-atlas` or `start-run`",
            "offer one natural-language continue affordance through Gazetteer",
            "Status and orientation are read-only", "INTERACTIVE", "AUTO_CONTINUE",
            "owner retains the conversation", "does not interject between co-design or Discovery questions",
            "Do not encode `next_skill`", "Continuation is never acceptance or approval",
            "READY_FOR_EXECUTION",
            "no first-party execution owner exists", "Never hard-code a provider or model name",
        ],
        "gazetteer-agent": [
            'display_name: "Atlas Gazetteer"',
            "authoritative Atlas state",
            "allow_implicit_invocation: true",
        ],
        "internal-owner-loading": [
            "Atlas internal owners remain non-implicit",
            "Prefer the host's safe nested skill invocation mechanism",
            "calibrated procedure-load fallback",
            "never derives a stage",
        ],
        "gazetteer-helper": [
            "def inventory", "def _summarize_run", "def _accepted_boundaries",
            "def _accepted_graph", 'sub.add_parser("inventory"',
            "verified_state", "verified_planning_state", "load_machine_config", "NOT_CONFIGURED",
            "PARTIAL", "repository_relevant_runs", "repository_blocked_runs",
            "ticket_ids", "candidate_sha256",
        ],
        "setup-agent": [
            'short_description: "Configure or verify Atlas on this machine"',
            "allow_implicit_invocation: false",
        ],
        "start": [
            "description: Create or resume an Atlas run", "run.yaml", "control.json",
            "initialize", "AGENT_REVIEW", "HUMAN", "AUTO",
            "disable-model-invocation: true",
            "Prefer the host's safe nested skill invocation mechanism",
            "load the exact installed sibling `SKILL.md` as the current owner procedure",
            "atlas_planning.py", "planning-control.json", ".atlas-planning.lock",
        ],
        "start-agent": [
            'short_description: "Create or resume an Atlas run from authoritative state"',
            "allow_implicit_invocation: false",
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
            "def load_planning_control", "def initialize_planning", "def ensure_planning", "def check_boundary",
            "def advance_boundary", 'SYSTEM_DESIGN_FILE = "30-system-design.md"',
            'TICKET_GRAPH_FILE = "50-ticket-graph.json"', "def ticket_graph_report",
            "def advance_ticket_graph_boundary", 'TICKET_GRAPH_REVIEW_REFERENCE = "reviews/ticket-graph-v1.json"',
            "verify_system_design_board", "30-system-design.html",
        ],
        "repository": [
            "def selected_config_path", "def load_machine_config", "def load_bindings",
            "def repository_identity_for_location", "def probe_source", "def bind_repository", "def verify_run",
            "def list_tree", "def search_tree", "def read_tree_path",
            'sub.add_parser(\n        "probe-source"', 'sub.add_parser("verify"', 'sub.add_parser("list"',
            'sub.add_parser("search"', 'sub.add_parser("read"',
        ],
        "system-design": [
            "disable-model-invocation: true", "third parent of this file", "agent_led",
            "Features pay for seams", "named accepted behavior, authority boundary, or independently changing responsibility",
            "Delete speculative seams",
            "co_design", "Slice 2", "references/system-design-file.md", "references/system-design-board.md",
            "gate_ready: true", "render_system_design.py", ".30-system-design.next.md",
            "mobile projection contract", "mechanically verified but unreadable board is not complete decision evidence",
            "exactly one selected option", "### Decision map", "recommended is not a terminal decision state",
            "Begin every material decision packet", "every preview of the exact decision or next question",
            "simplified technical English", "exact decision or next question", "why it matters now",
            "fixed constraints", "not yet decided", "same evaluation criteria and trade-off axes",
            "what each option optimizes", "genuine choices or rejected controls",
            "synthesize the resulting consequence", "do not manufacture a preference picker",
            "one combined context-plus-diagram phone-first packet", "separate context and topology visuals",
            "When agent-led analysis presents materially different alternatives",
            "persist equivalent decision evidence", "use the framing above for every retained option",
            "within the existing twelve required sections",
            "selected route in the Decision map", "alternatives and reasoning in the owning section",
            "does not require HTML solely for this evidence rule",
            "atlas:control-planning", "without asking the user to issue a second command",
        ],
        "system-design-template": [
            "run: <feature-slug>", "version: 1", "status: draft", "gate_ready: false",
            "participation: agent_led", "source_binding:", "kind: product_closure",
            "kind: stage0", "effective_config_hash", "effective_config_revision",
            "### Decision map", "| Decision | Selected route | Adoption or disposition | Implementation consequence |",
            "(selected)", "Agent-led material alternative evidence", "same criteria and trade-off axes",
            "what each option optimizes", "genuine choice or rejected control", "owning existing section",
            "No additional top-level section", "HTML is not implied solely by this evidence rule",
        ],
        "system-design-agent": ["allow_implicit_invocation: false"],
        "program-design": [
            "name: program-design", "disable-model-invocation: true",
            "Bounded proof", "accepted behavior classes, invariants, authority boundaries, and canonical transitions",
            "Do not multiply tests across prose variants",
            "Every test seam must map to an accepted requirement, a necessary invariant or authority boundary implied by accepted design, or a reachable failure class",
            "references/program-design-file.md", "cite every upstream commitment",
        ],
        "program-design-template": [
            "run: <feature-slug>", "version: 1", "status: draft", "gate_ready: true",
            "kind: system_design", "artifact: 30-system-design.md", "kind: product_closure",
            "artifact: 20-prd.md", "kind: stage0", "artifact: run.yaml",
            "effective_config_hash", "effective_config_revision",
            "Implementation constraints and sequencing",
        ],
        "program-design-agent": [
            'display_name: "Atlas Program Design"',
            'short_description: "Produce Stage 4 and hand it to planning control"',
            "Use $program-design to produce the exact Atlas Program Design candidate and continue its internal control handoff.",
            "allow_implicit_invocation: false",
        ],
        "compile-tickets": [
            "name: compile-tickets", "disable-model-invocation: true",
            "references/ticket-graph-file.md", "D-084", "D-085",
            "tickets/*.md", "50-ticket-graph.json", "atlas:control-planning",
            "READY_FOR_EXECUTION",
        ],
        "ticket-graph-template": [
            '"version": 2', '"preferred_order"', '"tracer_ticket"', '"source_bindings"', "exactly one",
            "blocked_by:", "context:", "sources:", "purpose:", "external_prerequisites:", "validators:", "outcomes:",
            "What becomes true", "Acceptance", "Execution context",
            "Version 1 is retained as raw historical evidence only and is not loadable or factory-executable",
        ],
        "compile-tickets-agent": [
            'display_name: "Atlas Ticket Graph Compiler"',
            'short_description: "Compile Stage 5 and hand it to planning control"',
            "Use $compile-tickets to compile the exact Atlas Stage 5 ticket graph and continue its internal control handoff.",
            "allow_implicit_invocation: false",
        ],
        "system-design-board": [
            "30-system-design.md", "30-system-design.html", "Inapplicable:",
            "non-authoritative", "no independent acceptance hash",
            "## Mobile projection contract", "white-space: pre",
            "Mermaid is not a runtime dependency or implied capability",
            "document.documentElement.scrollWidth <= innerWidth",
            "390×844", "at least `44px` high", "both light and dark schemes",
            "## Decision packet framing contract", "simplified technical English",
            "one combined context-plus-diagram phone-first packet", "do not manufacture a preference picker",
            "## Decision visibility contract", "places **Decisions at a glance** above the detailed views",
            "labels the selected option **Selected** and every other option **Not selected**",
            "Selection is scoped by decision identity and option number, never by repeated option text",
            "A gate-ready board fails rendering when a settled alternative set has zero or multiple selected markers",
            "Later Option-number elaborations inside the same decision inherit that decision's selected route",
            "Status text is real HTML content, not CSS-generated content",
            "Option-looking text inside fenced code never participates in decision extraction",
            "A gate-ready candidate using canonical `(selected)` markers must have the Decision map as the first `Proposed system` subsection",
        ],
        "control-planning": [
            "disable-model-invocation: true", "third parent of this file", "never routes",
            "never synthesizes", "never edits", "never grades prose", "explicit human approval",
            "agent_led", "co_design", "30-system-design.html", "non-authoritative",
            "atlas_planning.py", "advance --run", "--approval human", "--date",
            "re-read `planning-control.json`", "AGENT_REVIEW", "HUMAN_IF_CHANGED", "Slice 2",
            "fresh read-only classifier", "distinct fresh semantic reviewer", "invoker assembles",
            "reviews/system-design-v1.json", "supports exactly the explicit stages `system_design`, `program_design`, and `tickets`",
            "never discovers, infers, or reroutes a stage", "references/program-design-authority.md",
            "configured `AGENT_REVIEW` or `HUMAN` authority", "fresh exact PASS review",
            "reviews/program-design-v1.json", "references/ticket-graph-authority.md",
            "reviews/ticket-graph-v1.json", "## Ticket graph branch",
        ],
        "system-design-authority": [
            "reviews/system-design-v1.json", "candidate_version", "candidate_sha256",
            "repository_baselines", "materiality", "semantic_review", "unavailable_reason",
            "MATERIAL", "NOT_MATERIAL", "UNAVAILABLE", "PASS", "BLOCKED",
        ],
        "program-design-authority": [
            "reviews/program-design-v1.json", "AGENT_REVIEW", "HUMAN", "PASS",
            "BLOCKED", "DESIGN_BLOCKED", "upstream_issue", "resume_boundary",
        ],
        "ticket-graph-authority": [
            "reviews/ticket-graph-v1.json", "AGENT_REVIEW", "HUMAN",
            "PASS", "BLOCKED", "DESIGN_BLOCKED", "deterministic_behavior_proof",
            "READY_FOR_EXECUTION",
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

    ticket_v2_context_contract = {
        "compile-tickets": (
            "Ticket-graph manifest version is exact integer `2`",
            "compile-tickets owns semantic context selection",
            "Execution context` body mirrors the ordered declarations exactly",
            "No automatic projection or supervisor gap filling is allowed",
        ),
        "ticket-graph-template": (
            "context:",
            "purpose:",
            "Execution context",
            "exactly one ordered canonical line per `context.sources` entry",
            "Version 1 is retained as raw historical evidence only and is not loadable or factory-executable",
        ),
        "control-planning": (
            "validates and materializes only the accepted context declarations plus current execution facts",
            "must not select sources, add sections, write purposes, or fill context gaps",
            "Missing declared material is a packaging/preflight blocker; missing accepted judgment is `DESIGN_BLOCKED`",
        ),
        "ticket-graph-authority": (
            '"candidate_version": 2',
            "`reviews/ticket-graph-v1.json` remains the evidence-envelope filename",
        ),
        "planning": (
            '"context", "external_prerequisites"',
            'TICKET_CONTEXT_FIELDS = {"sources"}',
            'TICKET_CONTEXT_SOURCE_FIELDS = {"kind", "sections", "purpose"}',
            'CURRENT_TICKET_GRAPH_VERSION = 2',
            'record["candidate_version"] != CURRENT_TICKET_GRAPH_VERSION',
            'candidate_version != CURRENT_TICKET_GRAPH_VERSION',
        ),
    }
    if any(
        clause not in texts.get(name, "")
        for name, clauses in ticket_v2_context_contract.items()
        for clause in clauses
    ):
        findings.append(("cross", "ticket v2 context authority contract is incomplete"))
    if (
        re.search(r"(?im)^\s*references:\s*$", texts.get("ticket-graph-template", ""))
        or "Every ticket references every applicable accepted source" in texts.get("compile-tickets", "")
    ):
        findings.append(("cross", "live Stage 5 contract still uses legacy ticket references"))

    repository_surface = required["repository"]
    if any(marker not in texts.get("repository", "") for marker in repository_surface):
        findings.append(("cross", "repository adapter public surface is incomplete"))

    setup = texts.get("setup", "")
    setup_binding_contract = (
        "Preserve every existing configuration key and value not explicitly changed",
        "one stable repository identity to one canonical absolute path to an existing local Git repository or object source",
        "Show the exact configuration diff, the exact configuration path, and the exact identity/source pair",
        "Wait for explicit confirmation before creating or changing a binding",
        "Normal runs reuse a confirmed binding without asking again",
        "A remote URL may help propose a stable identity, and the current checkout may help propose its canonical source path",
        "A proposal grants no authority and never silently creates or changes a binding",
        "never sync, clone, fetch, authenticate, checkout, create a worktree, or mutate a repository",
        'python3 "<atlas-plugin-root>/tools/atlas_repository.py" probe-source --source "<canonical-absolute-local-git-source>"',
        "Before a run exists, stop after source probing and confirmed configuration; do not invoke run-specific `verify --run`",
        'python3 "<atlas-plugin-root>/tools/atlas_repository.py" verify --run "<run-directory>"',
        "Only after an initialized run exists, use `verify --run`",
        "Report every gap and resume action from the complete verification report",
        "only V1 artifact-location setting, not the only machine configuration",
    )
    if (
        any(clause not in setup for clause in setup_binding_contract)
        or "must never infer a binding from a remote or the current checkout" in setup
    ):
        findings.append(("cross", "setup: incomplete D-081 binding commissioning contract"))

    calibration_six_clis = (
        "Invoke exactly all six packaged CLIs with `--help` using that same recorded interpreter: "
        "`tools/atlas_control.py`, `tools/atlas_planning.py`, `tools/atlas_repository.py`, "
        "`tools/atlas_gazetteer.py`, `tools/render_prd.py`, and `tools/render_system_design.py`."
    )
    if calibration_six_clis not in texts.get("installed-host-calibration", ""):
        findings.append(("cross", "installed-host-calibration: missing six packaged CLIs with the recorded interpreter"))

    readme_program_contract = (
        "First-party Stage 0–5 skills",
        "| `program-design` | Produce the exact Stage 4 candidate, record readiness, and continue the internal control handoff. |",
        "| `compile-tickets` | Compile and hand off the exact Stage 5 ticket graph candidate. |",
        "stops at `READY_FOR_EXECUTION`",
    )
    if any(clause not in texts.get("readme", "") for clause in readme_program_contract):
        findings.append(("cross", "README Stage 0-5 inventory is incomplete"))

    readme_repository_classification = (
        "missing binding, source, exact commit/tree/blob, submodule content, or Git LFS content returns `BLOCKED`; "
        "only an exact-code contradiction requiring accepted upstream truth to change returns `DESIGN_BLOCKED`"
    )
    if (
        readme_repository_classification not in texts.get("readme", "")
        or "unresolved repository access returns DESIGN_BLOCKED" in texts.get("readme", "")
    ):
        findings.append(("cross", "README repository BLOCKED classification contradicts D-081"))

    full_oid_start_contract = (
        "Resolve every admitted baseline to the repository's full canonical commit object ID before previewing `run.yaml`",
        "New intake never stores a branch, tag, `HEAD`, or abbreviated object ID as `baseline`",
        "If the exact commit is not locally readable, stop before writing intake",
    )
    full_oid_run_file_contract = (
        "baseline: <full canonical commit object ID>",
        "`baseline` is the full canonical lowercase hexadecimal object ID of a commit",
        "never a branch, tag, `HEAD`, or abbreviated object ID",
    )
    if (
        any(clause not in texts.get("start", "") for clause in full_oid_start_contract)
        or any(clause not in texts.get("run-file", "") for clause in full_oid_run_file_contract)
        or "baseline: <commit SHA>" in texts.get("run-file", "")
    ):
        findings.append(("cross", "start-run: missing full canonical repository baseline intake"))

    start_binding_commissioning_contract = (
        "Read the existing confirmed machine binding for every proposed stable repository identity before accepting intake",
        "If one is missing or an explicitly requested replacement is needed, invoke `atlas:setup-atlas` internally for that one identity/source pair",
        "Do not ask the user to leave `start-run`, invoke setup manually, or restart intake",
        "After setup returns, reload machine bindings and require the exact confirmed identity/source pair before resolving the full canonical commit object ID",
        "A declined or failed binding confirmation stops the same intake without writing `run.yaml`",
    )
    if any(clause not in texts.get("start", "") for clause in start_binding_commissioning_contract):
        findings.append(("cross", "start-run: missing internal binding commissioning"))

    program = texts.get("program-design", "")
    grounding = "Before drafting anything, require a readable repository for every stable identity and prove the exact frozen baseline commit/tree is available"
    drafting_heading = "## 3. Produce the Stage 4 candidate"
    if grounding not in program or drafting_heading not in program or program.index(grounding) > program.index(drafting_heading):
        findings.append(("cross", "program-design: missing repository grounding before drafting"))

    baseline_access_contract = (
        "current HEAD and working-tree state only as drift/context",
        "neither may silently replace the frozen baseline as design truth",
        "Treat current `HEAD`, index, and working-tree bytes only as drift",
        "never substitute them for the exact baseline",
        "../../references/program-design-blocked.md",
    )
    if any(clause not in program for clause in baseline_access_contract):
        findings.append(("cross", "program-design: missing fail-closed exact frozen-baseline access preflight"))

    portable_evidence_contract = {
        "program-design": (
            "Machine-local `config_path`, bound `source`, Git-directory, and absolute diagnostic paths are ephemeral operational evidence",
            "Never copy them into `40-program-design.md`",
            "Repository grounding in the candidate names only stable repository identity, full baseline OID, baseline-relative repository paths, and relevant code evidence",
        ),
        "program-design-template": (
            "<stable repository identities, full baseline OIDs, baseline-relative repository paths, conventions, and feasibility evidence; never machine-local config/source paths>",
        ),
        "control-planning": (
            "Adapter `config_path`, bound `source`, Git-directory, and absolute diagnostic paths are ephemeral operational evidence",
            "Never copy them into `reviews/program-design-v1.json`",
            "Reviewer evidence names only stable repository identity, full baseline OID, baseline-relative repository paths, and relevant code evidence",
        ),
    }
    if any(
        clause not in texts.get(name, "")
        for name, clauses in portable_evidence_contract.items()
        for clause in clauses
    ):
        findings.append(("cross", "Program Design machine-local path leakage boundary is incomplete"))

    repository_verify = 'python3 "<atlas-plugin-root>/tools/atlas_repository.py" verify --run "<run-directory>"'
    repository_list = 'python3 "<atlas-plugin-root>/tools/atlas_repository.py" list --run "<run-directory>" --repository "<stable-repository-id>"'
    repository_search = 'python3 "<atlas-plugin-root>/tools/atlas_repository.py" search --run "<run-directory>" --repository "<stable-repository-id>" --needle "<literal>"'
    repository_read = 'python3 "<atlas-plugin-root>/tools/atlas_repository.py" read --run "<run-directory>" --repository "<stable-repository-id>" --path "<baseline-path>"'
    repository_commands = (repository_verify, repository_list, repository_search, repository_read)
    if (
        drafting_heading not in program
        or any(command not in program for command in repository_commands)
        or any(program.index(command) > program.index(drafting_heading) for command in repository_commands if command in program)
        or (
            repository_verify in program
            and repository_list in program
            and program.index(repository_verify) > program.index(repository_list)
        )
        or "Use only these adapter `list`, `search`, and `read` commands for baseline inspection" not in program
    ):
        findings.append(("cross", "program-design: missing exact adapter verification and inspection before drafting"))

    program_blocked_contract = (
        "Missing binding, source, full canonical object ID, commit/tree/blob object, required submodule content, or required Git LFS content is ordinary non-mutating `BLOCKED`",
        "`DESIGN_BLOCKED` is reserved for an exact-code contradiction that requires accepted upstream truth to change",
    )
    blocked_runbook_contract = (
        "ordinary repository dependency `BLOCKED`",
        "true upstream `DESIGN_BLOCKED`",
        "Resume a missing local dependency through `setup-atlas` or an offline repository repair, then rerun",
        "requires no authority decision or reopen",
        "If Discovery no longer owns the cursor, an abbreviated baseline requires a corrected new run",
        "`PENDING` means no acceptance was written",
    )
    if (
        any(clause not in program for clause in program_blocked_contract)
        or any(clause not in texts.get("program-design-blocked", "") for clause in blocked_runbook_contract)
    ):
        findings.append(("cross", "Program Design D-081 BLOCKED classification is incomplete"))

    resolved_only_contract = (
        "settled Stage 4 decisions with bounded residual uncertainty",
        "Stage 5 receives no design question it must answer",
    )
    if (
        any(clause not in program for clause in resolved_only_contract)
        or any(clause not in texts.get("program-design-template", "") for clause in resolved_only_contract[1:])
        or "unresolved local code-shape choice is `BLOCKED`" not in texts.get("program-design-authority", "")
    ):
        findings.append(("cross", "Program Design least-confidence seam does not contain resolved-only Stage 4 decisions"))

    frozen_program_contract = (
        "Read immutable `run.yaml`, authoritative Stage 0 `control.json`, and `planning-control.json`",
        "Require current phase `program_design`, gate `PENDING`, and exact configured authority `AGENT_REVIEW` or `HUMAN`",
        "Program Design never asks a participation question",
    )
    if any(clause not in program for clause in frozen_program_contract):
        findings.append(("cross", "program-design: missing exact frozen boundary without participation"))

    source_contract = (
        "Derive the applicable branch only from effective selected stages, never from candidate prose or artifact presence",
        "Read exactly one applicable upstream source and do not read either omitted source",
        "System Design selected: read exact accepted `30-system-design.md`",
        "System Design omitted and Product Definition Approval selected: read exact accepted `20-prd.md`",
        "both upstream semantic boundaries omitted: read frozen effective Stage 0 `run.yaml` and its recorded effective configuration binding",
    )
    if any(clause not in program for clause in source_contract):
        findings.append(("cross", "program-design: missing exact three-source selection or one-source-only rule"))

    program_root = "it is the third parent of this file (`SKILL.md` → `program-design/` → `skills/` → plugin root)"
    if program_root not in program or "never rely on the caller's working directory" not in program:
        findings.append(("cross", "program-design: missing caller-CWD-independent Program Design skill root"))

    ownership_contract = (
        "On the normal path, write only canonical `40-program-design.md` candidate/readiness bytes",
        "never create or modify `reviews/program-design-v1.json`",
        "never write `planning-control.json`",
        "never rewrite an upstream artifact",
    )
    if any(clause not in program for clause in ownership_contract):
        findings.append(("cross", "program-design: missing normal-path candidate-only ownership"))

    producer_blocked_contract = (
        "Before writing candidate or readiness bytes, return structured read-only `DESIGN_BLOCKED` and stop",
        "nonempty `upstream_issue`",
        "both equal the actual selected source-binding kind",
        "smallest upstream decision or change required",
        "creates no review file",
        "does not rewrite any upstream artifact",
        "does not mutate planning state",
        "Reviewer-discovered `DESIGN_BLOCKED` belongs only in a fresh `reviews/program-design-v1.json`",
    )
    if any(clause not in program for clause in producer_blocked_contract):
        findings.append(("cross", "program-design: missing structured read-only pre-readiness DESIGN_BLOCKED stop"))

    handoff = "After mechanical `PASS`, perform the exact named internal handoff to `atlas:control-planning`"
    if (
        program.count("atlas:control-planning") != 1
        or handoff not in program
        or "without asking the user to issue a second routing command" not in program
        or "unchanged `<run-directory>` and explicit stage `program_design`" not in program
    ):
        findings.append(("cross", "program-design: missing exact internal control-planning handoff"))

    compile_tickets = texts.get("compile-tickets", "")
    compile_contract = (
        "Resolve `<atlas-plugin-root>` from this installed skill",
        "Require current status `PLANNING`, phase `tickets`, gate `PENDING`, and no ticket-graph acceptance",
        "Derive every applicable source only from effective selected stages and exact current acceptances",
        "write only canonical `tickets/*.md` and `50-ticket-graph.json` candidate/readiness bytes",
        "never create or modify `reviews/ticket-graph-v1.json`",
        "never write `planning-control.json`",
        'check --run "<run-directory>" --stage tickets',
        "unchanged `<run-directory>` and explicit stage `tickets`",
    )
    compile_handoff = "After mechanical `PASS`, perform the exact named internal handoff to `atlas:control-planning`"
    if any(clause not in compile_tickets for clause in compile_contract):
        findings.append(("cross", "compile-tickets: incomplete Stage 5 producer ownership or source contract"))
    if compile_tickets.count("atlas:control-planning") != 1 or compile_handoff not in compile_tickets:
        findings.append(("cross", "compile-tickets internal control-planning handoff is incomplete"))

    control_planning = texts.get("control-planning", "")
    stage_check_selector = (
        "Run exactly one mechanical check selected by the explicit stage; never run more than one command"
    )
    system_check = (
        'python3 "<atlas-plugin-root>/tools/atlas_planning.py" check '
        '--run "<run-directory>" --stage system_design'
    )
    program_check = (
        'python3 "<atlas-plugin-root>/tools/atlas_planning.py" check '
        '--run "<run-directory>" --stage program_design'
    )
    ticket_check = (
        'python3 "<atlas-plugin-root>/tools/atlas_planning.py" check '
        '--run "<run-directory>" --stage tickets'
    )
    if (
        stage_check_selector not in control_planning
        or "For explicit stage `system_design`, run only:" not in control_planning
        or "For explicit stage `program_design`, run only:" not in control_planning
        or "For explicit stage `tickets`, run only:" not in control_planning
        or control_planning.count(system_check) != 1
        or control_planning.count(program_check) != 1
        or control_planning.count(ticket_check) != 1
    ):
        findings.append(("cross", "control-planning: missing explicit-stage-only check selection"))

    reviewer_marker = "Invoke one distinct fresh read-only semantic reviewer"
    control_repository_contract = (
        "return its complete mechanical repository `BLOCKED` report before invoking a reviewer or writing evidence",
        "The fresh reviewer reads the exact baseline only through the adapter commands above",
        "Current `HEAD`, index, and working-tree bytes are never substitute review inputs",
    )
    if (
        reviewer_marker not in control_planning
        or any(command not in control_planning for command in repository_commands)
        or any(
            control_planning.index(command) > control_planning.index(reviewer_marker)
            for command in repository_commands
            if command in control_planning and reviewer_marker in control_planning
        )
        or (
            repository_verify in control_planning
            and repository_list in control_planning
            and control_planning.index(repository_verify) > control_planning.index(repository_list)
        )
        or any(clause not in control_planning for clause in control_repository_contract)
    ):
        findings.append(("cross", "control-planning: missing repository preflight before Program Design review"))

    try:
        system_agent = yaml.safe_load(texts.get("system-design-agent", ""))
        program_agent = yaml.safe_load(texts.get("program-design-agent", ""))
        compile_agent = yaml.safe_load(texts.get("compile-tickets-agent", ""))
        control_agent = yaml.safe_load(texts.get("control-planning-agent", ""))
        system_prompt = system_agent["interface"]["default_prompt"]
        program_interface = program_agent["interface"]
        compile_interface = compile_agent["interface"]
        control_interface = control_agent["interface"]
        system_implicit = system_agent["policy"]["allow_implicit_invocation"]
        program_implicit = program_agent["policy"]["allow_implicit_invocation"]
        compile_implicit = compile_agent["policy"]["allow_implicit_invocation"]
        control_implicit = control_agent["policy"]["allow_implicit_invocation"]
    except (TypeError, KeyError, yaml.YAMLError) as exc:
        findings.append(("cross", f"System, Program, ticket, or control model metadata is unreadable: {exc}"))
    else:
        expected_program_interface = {
            "display_name": "Atlas Program Design",
            "short_description": "Produce Stage 4 and hand it to planning control",
            "default_prompt": (
                "Use $program-design to produce the exact Atlas Program Design candidate "
                "and continue its internal control handoff."
            ),
        }
        expected_compile_interface = {
            "display_name": "Atlas Ticket Graph Compiler",
            "short_description": "Compile Stage 5 and hand it to planning control",
            "default_prompt": (
                "Use $compile-tickets to compile the exact Atlas Stage 5 ticket graph "
                "and continue its internal control handoff."
            ),
        }
        expected_control_interface = {
            "display_name": "Atlas Control Planning",
            "short_description": "Apply configured System, Program, or ticket authority once",
            "default_prompt": (
                "Use $control-planning to apply one explicit configured System Design, Program Design, "
                "or ticket-graph boundary and record at most one transition."
            ),
        }
        if program_interface != expected_program_interface:
            findings.append(("cross", "Program Design model metadata must expose the exact producer interface"))
        if compile_interface != expected_compile_interface:
            findings.append(("cross", "Ticket compiler model metadata must expose the exact producer interface"))
        if control_interface != expected_control_interface:
            findings.append(("cross", "control-planning model metadata must expose all three explicit boundaries"))
        if (
            "current agent-led" in system_prompt.lower()
            or "frozen agent_led or co_design participation" not in system_prompt
            or "candidate" not in system_prompt
            or "internal control handoff" not in system_prompt
        ):
            findings.append(("cross", "system-design-agent: stale Slice 1 agent-led priming remains in model metadata"))
        if (
            system_implicit is not False
            or program_implicit is not False
            or compile_implicit is not False
            or control_implicit is not False
        ):
            findings.append(("cross", "Stage 3-5 model metadata must keep implicit invocation false"))

    planning_command = 'python3 "<atlas-plugin-root>/tools/atlas_planning.py" ensure --run "<run-directory>"'
    for name in ("start", "control"):
        if planning_command not in texts.get(name, ""):
            findings.append(("cross", f"{name}: missing shared planning ensure command with installed-root/CWD contract"))
    start_text = texts.get("start", "")
    start_collision = start_text.split("## 1. Resolve and accept intake", 1)[0]
    start_handoff = start_text.split("## 3. Hand off", 1)[1] if "## 3. Hand off" in start_text else ""
    if planning_command not in start_collision:
        findings.append(("cross", "start: missing interrupted downstream resume recovery through shared ensure"))
    if (
        "A `PLANNING` run resumes at current `control.json.phase`" in start_text
        or "If authoritative `control.json.phase` is `discovery`" not in start_collision
        or "validated `planning-control.json.phase` is the actual current planning phase" not in start_collision
        or "validated `planning-control.json.phase` is the actual current planning phase" not in start_handoff
    ):
        findings.append(("cross", "start: stale live downstream resume cursor; planning-control must own downstream position"))
    start_route_contract = (
        "If validated planning phase is `system_design`, invoke `atlas:system-design` internally",
        "If validated planning phase is `program_design`, invoke `atlas:program-design` internally",
        "If validated planning phase is `tickets`, invoke `atlas:compile-tickets` internally",
        "If validated planning status is `READY_FOR_EXECUTION`, stop at the execution boundary",
        "Preserve the existing Product Definition Approval, System Design, and Program Design paths",
    )
    if any(clause not in start_text for clause in start_route_contract):
        findings.append(("cross", "start: missing complete Stage 3-5 producer route and execution-boundary stop"))

    start_continuation_contract = (
        "For `AUTO_CONTINUE`, use the existing bounded continuation loop, not one-shot dispatch",
        "After an invoked producer and its internal control handoff return, run `ensure` again and re-read validated `planning-control.json`",
        "The only legal downstream continuation after `system_design` is `program_design` or `tickets`; after `program_design` it is `tickets`; after pending `tickets` it is `READY_FOR_EXECUTION`",
        "Invoke at most three downstream producers during one `start-run` invocation",
        "If the phase is unchanged while status remains `PLANNING`, the invoked stage's gate remains `PENDING`, the transition is unexpected, or an invoked owner stops `BLOCKED` or `DESIGN_BLOCKED`, stop without retrying that producer",
        "Never derive a producer dynamically from the stage list",
    )
    if any(clause not in start_text for clause in start_continuation_contract):
        findings.append(("cross", "start: missing bounded downstream continuation"))

    check_command = 'python3 "<atlas-plugin-root>/tools/atlas_planning.py" check --run "<run-directory>" --stage system_design'
    program_check_command = 'python3 "<atlas-plugin-root>/tools/atlas_planning.py" check --run "<run-directory>" --stage program_design'
    ticket_check_command = 'python3 "<atlas-plugin-root>/tools/atlas_planning.py" check --run "<run-directory>" --stage tickets'
    advance_command = 'python3 "<atlas-plugin-root>/tools/atlas_planning.py" advance --run "<run-directory>" --stage system_design --approval human --date "<YYYY-MM-DD>"'
    for name in ("system-design", "control-planning"):
        if check_command not in texts.get(name, ""):
            findings.append(("cross", f"{name}: missing caller-CWD-independent System Design check command"))
    for name in ("program-design", "control-planning"):
        if program_check_command not in texts.get(name, ""):
            findings.append(("cross", f"{name}: missing caller-CWD-independent Program Design check command"))
    for name in ("compile-tickets", "control-planning"):
        if ticket_check_command not in texts.get(name, ""):
            findings.append(("cross", f"{name}: missing caller-CWD-independent tickets check command"))
    if advance_command not in texts.get("control-planning", ""):
        findings.append(("cross", "control-planning: missing exact HUMAN System Design advance command"))
    for command in (
        'advance --run "<run-directory>" --stage system_design --review reviews/system-design-v1.json --date "<YYYY-MM-DD>"',
        'advance --run "<run-directory>" --stage system_design --review reviews/system-design-v1.json --approval human --date "<YYYY-MM-DD>"',
    ):
        if command not in texts.get("control-planning", ""):
            findings.append(("cross", f"control-planning: missing System Design authority-matrix command `{command}`"))
    for command in (
        'advance --run "<run-directory>" --stage program_design --review reviews/program-design-v1.json --date "<YYYY-MM-DD>"',
        'advance --run "<run-directory>" --stage program_design --review reviews/program-design-v1.json --approval human --date "<YYYY-MM-DD>"',
    ):
        if command not in texts.get("control-planning", ""):
            findings.append(("cross", f"control-planning: missing Program Design authority-matrix command `{command}`"))
    for command in (
        'advance --run "<run-directory>" --stage tickets --review reviews/ticket-graph-v1.json --date "<YYYY-MM-DD>"',
        'advance --run "<run-directory>" --stage tickets --review reviews/ticket-graph-v1.json --approval human --date "<YYYY-MM-DD>"',
    ):
        if command not in texts.get("control-planning", ""):
            findings.append(("cross", f"control-planning: missing ticket-graph authority-matrix command `{command}`"))
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
        system_design_dimensions = tuple(assigned_literal(texts.get("planning", ""), "SYSTEM_DESIGN_DIMENSIONS"))
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
        run_dimensions = (
            run_maps[0].get("gates", {}).get("system_design", {}).get("material_dimensions")
            if len(run_maps) == 1 else None
        )
        if not isinstance(run_dimensions, list) or tuple(run_dimensions) != system_design_dimensions:
            findings.append(("cross", "canonical run-file HUMAN_IF_CHANGED dimensions do not match planning SYSTEM_DESIGN_DIMENSIONS"))

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
        program_fields = set(assigned_literal(texts.get("planning", ""), "PROGRAM_DESIGN_FIELDS"))
        product_source_fields = set(assigned_literal(texts.get("planning", ""), "PRODUCT_SOURCE_FIELDS"))
        stage0_source_fields = set(assigned_literal(texts.get("planning", ""), "STAGE0_SOURCE_FIELDS"))
        program_sections = tuple(assigned_literal(texts.get("planning", ""), "PROGRAM_DESIGN_SECTIONS"))
        program_maps = [
            item for item in frontmatter_maps(texts.get("program-design-template", ""))
            if {"run", "version", "status", "gate_ready"}.issubset(item)
        ]
        program_sources = [
            item.get("source_binding") for item in program_maps
            if isinstance(item.get("source_binding"), dict)
        ]
        program_sources += [
            item.get("source_binding") for _, block in template_blocks(texts.get("program-design-template", ""))
            if isinstance((item := yaml.safe_load(block)), dict)
            and set(item) == {"source_binding"}
            and isinstance(item.get("source_binding"), dict)
        ]
    except (SyntaxError, ValueError, yaml.YAMLError) as exc:
        findings.append(("cross", f"Program Design candidate schema seam is unreadable: {exc}"))
    else:
        present = set(program_maps[0]) if program_maps else set()
        if len(program_maps) != 1 or present != program_fields:
            findings.append(("cross", "Program Design candidate schema does not match planning PROGRAM_DESIGN_FIELDS"))
        expected_source_fields = {
            "system_design": product_source_fields,
            "product_closure": product_source_fields,
            "stage0": stage0_source_fields,
        }
        actual_sources = {
            source.get("kind"): set(source)
            for source in program_sources
            if isinstance(source, dict) and isinstance(source.get("kind"), str)
        }
        if len(program_sources) != 3 or actual_sources != expected_source_fields:
            findings.append(("cross", "Program Design source_binding templates do not match the exact three planning schemas"))
        headings = tuple(re.findall(r"(?m)^## ([^\n]+?)\s*$", texts.get("program-design-template", "")))
        if headings != program_sections:
            findings.append(("cross", "Program Design template sections do not match planning PROGRAM_DESIGN_SECTIONS"))
        combined_program = texts.get("program-design", "") + texts.get("program-design-template", "")
        if "participation:" in combined_program.lower() or "40-program-design.html" in combined_program.lower():
            findings.append(("cross", "Program Design must have no participation field or HTML artifact"))

    try:
        graph_fields = set(assigned_literal(texts.get("planning", ""), "TICKET_GRAPH_FIELDS"))
        ticket_fields = set(assigned_literal(texts.get("planning", ""), "TICKET_FIELDS"))
        context_fields = set(assigned_literal(texts.get("planning", ""), "TICKET_CONTEXT_FIELDS"))
        context_source_fields = set(assigned_literal(texts.get("planning", ""), "TICKET_CONTEXT_SOURCE_FIELDS"))
        current_graph_version = assigned_literal(texts.get("planning", ""), "CURRENT_TICKET_GRAPH_VERSION")
        graph_dimensions = tuple(assigned_literal(texts.get("planning", ""), "TICKET_GRAPH_DIMENSIONS"))
        graph_review_fields = set(assigned_literal(texts.get("planning", ""), "TICKET_GRAPH_REVIEW_FIELDS"))
        graph_review_reference = assigned_literal(texts.get("planning", ""), "TICKET_GRAPH_REVIEW_REFERENCE")
        graph_maps = json_maps(texts.get("ticket-graph-template", ""))
        ticket_maps = frontmatter_maps(texts.get("ticket-graph-template", ""))
        authority_maps = json_maps(texts.get("ticket-graph-authority", ""))
    except (SyntaxError, ValueError, json.JSONDecodeError, yaml.YAMLError) as exc:
        findings.append(("cross", f"Ticket graph schema seam is unreadable: {exc}"))
    else:
        manifest = graph_maps[0] if len(graph_maps) == 1 else {}
        ticket = ticket_maps[0] if len(ticket_maps) == 1 else {}
        envelope = authority_maps[0] if authority_maps else {}
        semantic = envelope.get("semantic_review") if isinstance(envelope, dict) else None
        context = ticket.get("context") if isinstance(ticket, dict) else None
        context_sources = context.get("sources") if isinstance(context, dict) else None
        rows = semantic.get("dimensions") if isinstance(semantic, dict) else None
        row_dimensions = tuple(
            item.get("dimension") for item in rows if isinstance(item, dict)
        ) if isinstance(rows, list) else ()
        if set(manifest) != graph_fields:
            findings.append(("cross", "ticket graph manifest schema does not match planning TICKET_GRAPH_FIELDS"))
        if set(ticket) != ticket_fields:
            findings.append(("cross", "ticket frontmatter schema does not match planning TICKET_FIELDS"))
        if not isinstance(context, dict) or set(context) != context_fields:
            findings.append(("cross", "ticket context schema does not match planning TICKET_CONTEXT_FIELDS"))
        if (
            not isinstance(context_sources, list)
            or not context_sources
            or any(
                not isinstance(source, dict) or set(source) != context_source_fields
                for source in context_sources
            )
        ):
            findings.append(("cross", "ticket context source schema does not match planning TICKET_CONTEXT_SOURCE_FIELDS"))
        if current_graph_version != 2 or manifest.get("version") != current_graph_version:
            findings.append(("cross", "ticket graph template candidate version does not match planning current version"))
        if set(envelope) != graph_review_fields:
            findings.append(("cross", "Ticket graph authority envelope does not match planning schema"))
        if envelope.get("version") != 1 or envelope.get("candidate_version") != current_graph_version:
            findings.append(("cross", "Ticket graph authority envelope version/candidate binding is inconsistent"))
        if row_dimensions != graph_dimensions:
            findings.append(("cross", "Ticket graph semantic review dimensions do not match planning TICKET_GRAPH_DIMENSIONS"))
        exact_filename = "`reviews/ticket-graph-v1.json` is the one exact run-relative envelope."
        if (
            graph_review_reference != "reviews/ticket-graph-v1.json"
            or exact_filename not in texts.get("ticket-graph-authority", "")
        ):
            findings.append(("cross", "Ticket graph authority filename is not exact across controller and reference"))

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

    try:
        program_review_reference = assigned_literal(
            texts.get("planning", ""), "PROGRAM_DESIGN_REVIEW_REFERENCE"
        )
        program_review_fields = set(
            assigned_literal(texts.get("planning", ""), "PROGRAM_DESIGN_REVIEW_FIELDS")
        )
        program_dimensions = tuple(
            assigned_literal(texts.get("planning", ""), "PROGRAM_DESIGN_DIMENSIONS")
        )
        semantic_fields = set(
            assigned_literal(texts.get("planning", ""), "SEMANTIC_REVIEW_FIELDS")
        )
        dimension_fields = set(
            assigned_literal(texts.get("planning", ""), "DIMENSION_REVIEW_FIELDS")
        )
        semantic_gap_fields = set(
            assigned_literal(texts.get("planning", ""), "SEMANTIC_GAP_FIELDS")
        )
        design_blocked_gap_fields = set(
            assigned_literal(texts.get("planning", ""), "DESIGN_BLOCKED_GAP_FIELDS")
        )
        program_authority_text = texts.get("program-design-authority", "")
        filename_definition = re.match(
            r"\A# Program Design authority evidence\n\n`([^`]+)` is the one exact run-relative envelope\.",
            program_authority_text,
        )
        defined_program_review_reference = (
            filename_definition.group(1) if filename_definition else None
        )
        program_authority_maps = json_maps(program_authority_text)
    except (SyntaxError, ValueError, TypeError, json.JSONDecodeError) as exc:
        findings.append(("cross", f"Program Design authority schema seam is unreadable: {exc}"))
    else:
        program_envelopes = [
            item
            for item in program_authority_maps
            if {"candidate_version", "repository_baselines", "semantic_review"}.issubset(item)
        ]
        program_envelope = program_envelopes[0] if len(program_envelopes) == 1 else {}
        program_semantic = (
            program_envelope.get("semantic_review")
            if isinstance(program_envelope, dict)
            else None
        )
        program_rows = (
            program_semantic.get("dimensions")
            if isinstance(program_semantic, dict)
            else None
        )
        program_baselines = (
            program_envelope.get("repository_baselines")
            if isinstance(program_envelope, dict)
            else None
        )
        blocked_gap_maps = [
            item for item in program_authority_maps if set(item) == semantic_gap_fields
        ]
        design_blocked_gap_maps = [
            item for item in program_authority_maps if set(item) == design_blocked_gap_fields
        ]
        if (
            program_review_reference != "reviews/program-design-v1.json"
            or defined_program_review_reference != program_review_reference
        ):
            findings.append(
                ("cross", "Program Design authority filename is not exact across controller and reference")
            )
        if set(program_envelope) != program_review_fields:
            findings.append(("cross", "Program Design authority envelope does not match planning schema"))
        if not isinstance(program_semantic, dict) or set(program_semantic) != semantic_fields:
            findings.append(
                ("cross", "Program Design semantic review reference does not match planning schema")
            )
        if (
            not isinstance(program_rows, list)
            or len(program_rows) != len(program_dimensions)
            or any(
                not isinstance(row, dict) or set(row) != dimension_fields
                for row in program_rows
            )
            or {row.get("dimension") for row in program_rows} != set(program_dimensions)
        ):
            findings.append(
                ("cross", "Program Design semantic review dimensions do not match the exact Stage 4 identifiers")
            )
        if len(blocked_gap_maps) != 1:
            findings.append(
                ("cross", "Program Design BLOCKED gap reference does not match planning schema")
            )
        if len(design_blocked_gap_maps) != 1:
            findings.append(
                ("cross", "Program Design DESIGN_BLOCKED gap reference does not match planning schema")
            )
        portable_authority_contract = (
            "Baselines are exact portable effective repository/full-canonical-OID pairs",
            "Acceptance records those exact portable pairs",
            "never a machine-local source path",
            "Missing local bindings, objects, submodule content, or Git LFS content are mechanical `BLOCKED`, not `DESIGN_BLOCKED`",
        )
        if (
            not isinstance(program_baselines, list)
            or not program_baselines
            or any(
                not isinstance(item, dict)
                or set(item) != {"repository", "baseline"}
                or not isinstance(item.get("repository"), str)
                or not isinstance(item.get("baseline"), str)
                or re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", item["baseline"]) is None
                for item in program_baselines
            )
            or any(clause not in program_authority_text for clause in portable_authority_contract)
        ):
            findings.append(("cross", "Program Design portable repository baseline authority is incomplete"))

    skill_line_bounds = {
        "system-design": (70, 110),
        "control-planning": (70, 135),
        "compile-tickets": (60, 130),
    }
    for name, (minimum, maximum) in skill_line_bounds.items():
        count = len(texts.get(name, "").splitlines())
        if not minimum <= count <= maximum:
            findings.append(("cross", f"{name}: SKILL.md line count {count} is outside {minimum}-{maximum}"))
    if re.search(r"\b(?:must|never|required)\b", texts.get("system-design-template", ""), re.I):
        findings.append(("cross", "System Design reference is not shape-only"))

    operating_required = {
        "discovery": [
            "Work in rounds", "**The problem test.**", "**The announcement test.**",
            "Propose candidate shapes", "never manufacture a recommendation",
            "cite the evidence that resolved it", "Give the fresh reader only `10-decisions.md`",
            "Nothing important exists only in the conversation", "third parent of this file",
            "return to the invoking continuation owner",
        ],
        "decision-record": ["justified recommendation or explicitly says that none is supportable"],
        "start": [
            "Never overwrite an existing `run.yaml`", "Stage 0 is recommend-only",
            "every other repository already known to be affected", "short, descriptive, stable",
            "does not imply an exact stage sequence or gate map", "ask rather than invent policy",
            "validated `planning-control.json.phase` is the actual current planning phase", "`STALE`", "`REJECTED`",
            "no first-party Atlas owner", "never substitute an incubator skill",
            "third parent of this file", "resolve-run-path", "before writing `run.yaml`",
            "pass the unchanged device/inode values", "--prepared-device", "--prepared-inode",
        ],
        "control": [
            "report the exact error and stop", "Never emulate transition logic",
            "structured `BLOCKED`", "expected check outcome",
            "run.yaml.gates.discovery.authority",
            "reject --run", "--reason", "third parent of this file",
            "already names `system_design`, `program_design`, or `tickets`",
            "do not rerun Product Definition Approval", "After a successful Product Definition Approval transition",
            "Return the freshly validated phase/status to the invoking continuation owner",
            "Do not invoke a downstream producer from `control-run`",
            "re-read `planning-control.json`", "discovery never starts execution",
        ],
        "setup": [
            "atomic contract-plus-code commits", "third parent of this file",
            "<atlas-plugin-root>/requirements.txt", "tools/atlas_gazetteer.py",
            "references/installed-host-calibration.md",
        ],
        "installed-host-calibration": [
            "installation bytes", "deterministic runtime readiness", "host recognition",
            "skill discovery", "procedure completion",
            "cross-skill handoff", "dated calibration", "PASS/FAIL/UNVERIFIED",
            "Gazetteer alone", "allow_implicit_invocation: true",
            "every internal/direct sibling", "retain `false`",
            "session.skills_loaded", "tools/atlas_planning.py",
            "tools/atlas_repository.py", "tools/atlas_gazetteer.py",
            "using that same launcher",
            "Without this run plus oracle, procedure completion is `UNVERIFIED`",
            "without changing a byte-equality PASS",
        ],
        "program-design-blocked": [
            "producer pre-readiness", "reviewer evidence", "`planning-control.json` remains `PENDING`",
            "no supported reopen or replacement-acceptance path",
            "frozen repository baseline cannot be located and read",
            "does not decide where a future repository binding lives",
            "Do not prescribe a `run.yaml` field, Stage 0 amendment/effective-configuration field",
        ],
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
        "repository_baselines: []": "stale pre-D-081 repository contract",
        "unratified repository-binding/baseline-reader mechanism": "stale pre-D-081 repository contract",
    }
    for phrase, reason in banned.items():
        if phrase.lower() in joined.lower():
            findings.append(("cross", f"legacy contract `{phrase}` remains — {reason}"))

    if (skills / "to-spec").exists():
        findings.append(("cross", "to-spec remains in the Atlas plugin after Product Definition Approval migration"))

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
