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
import ast, re, sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "plugins" / "atlas" / "skills"

# a naming sentence must carry one of these to count as a rule rather than a mention
RULE_WORDS = re.compile(
    r"\b(carr(?:y|ies|ying)|record(?:s|ed|ing)?|set(?:s|ting)?|writ(?:e|es|ten|ing)|"
    r"nam(?:e|es|ing)|state(?:s|d)?|declare(?:s|d)?|hold(?:s)?|flip(?:s)?|"
    r"assign(?:ed|s)?|assess(?:es|ed|ing)?|required|must|never|append(?:s|ed)?|populate(?:s|d)?)\b", re.I)


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


def template_blocks(ref: str) -> list[tuple[str, str]]:
    """Every explicit YAML fence and artifact-frontmatter block in a reference."""
    blocks = [("YAML template", block) for block in re.findall(r"```yaml\n(.*?)```", ref, re.S)]
    blocks += [
        ("frontmatter template", block)
        for block in re.findall(r"(?:^|\n)---\n(.*?)\n---(?:\n|$)", ref, re.S)
    ]
    return blocks


def template_fields(ref: str) -> list[str]:
    """Union of dotted YAML key paths defined by every template block."""
    fields: set[str] = set()
    for _, block in template_blocks(ref):
        stack: list[tuple[int, str]] = []
        lines = block.splitlines()
        for line_index, line in enumerate(lines):
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
            elif line_index + 1 < len(lines):
                following = lines[line_index + 1]
                if len(following) - len(following.lstrip()) > indent and re.match(r"^\s*-\s+[^:]+$", following):
                    fields.add(path)
            if not value or value.startswith("<complete recommended gate map"):
                stack.append((indent, key))
    return sorted(fields)


def template_yaml_errors(ref: str) -> list[str]:
    """Return parse errors for every YAML or artifact-frontmatter template block."""
    errors = []
    for index, (kind, block) in enumerate(template_blocks(ref), 1):
        try:
            yaml.safe_load(block)
        except yaml.YAMLError as exc:
            first = str(exc).splitlines()[0]
            errors.append(f"{kind} block {index} is invalid: {first}")
    return errors


def frontmatter_maps(ref: str) -> list[dict]:
    """Parse every artifact-frontmatter example into a mapping."""
    maps = []
    for block in re.findall(r"(?:^|\n)---\n(.*?)\n---(?:\n|$)", ref, re.S):
        value = yaml.safe_load(block)
        if isinstance(value, dict):
            maps.append(value)
    return maps


def assigned_literal(source: str, name: str):
    """Read a literal controller schema without importing executable code."""
    tree = ast.parse(source)
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == name for target in node.targets
        ):
            return ast.literal_eval(node.value)
    raise ValueError(f"missing literal assignment: {name}")


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
        for error in template_yaml_errors(text):
            findings.append(("template-yaml", f"{skill_dir.name}/{ref.name}: {error}"))
        for field in template_fields(text):
            token = field.rsplit(".", 1)[-1]
            if field.startswith("gates.") and field.count(".") == 1:
                token = "gates"
            naming = sentences_naming(skill, token)
            if not naming:
                findings.append(("forward", f"{skill_dir.name}/{ref.name}: `{field}` defined in template, ungoverned"))
            elif not any(RULE_WORDS.search(s) for s in naming):
                findings.append(("forward-weak", f"{skill_dir.name}/{ref.name}: `{field}` mentioned but no rule — {naming[0][:90]}"))

    for value in mandated_values(skill):
        if not sentences_naming(joined, value):
            findings.append(("reverse", f"{skill_dir.name}: skill mandates `{value}` with no home in any template"))

    return findings


def cross_skill_contracts(skills: Path) -> list[tuple[str, str]]:
    """Guard the Stage 0 → Stage 2 seams that previously drifted in real files."""
    findings: list[tuple[str, str]] = []

    required_files = {
        "start-run": skills / "start-run" / "SKILL.md",
        "run-file": skills / "start-run" / "references" / "run-file.md",
        "state-file": skills / "start-run" / "references" / "state-file.md",
        "amendment": skills / "start-run" / "references" / "run-amendment.md",
        "control-run": skills / "control-run" / "SKILL.md",
        "atlas-control": skills.parent / "tools" / "atlas_control.py",
        "discovery": skills / "discovery" / "SKILL.md",
        "run-layout": skills / "discovery" / "references" / "run-layout.md",
        "setup-atlas": skills / "setup-atlas" / "SKILL.md",
        "spike": skills / "spike" / "SKILL.md",
        "to-spec": skills / "to-spec" / "SKILL.md",
        "spec-file": skills / "to-spec" / "references" / "spec-file.md",
    }
    texts: dict[str, str] = {}
    for name, path in required_files.items():
        if not path.exists():
            findings.append(("cross", f"missing first-party seam file: {path.relative_to(skills)}"))
            continue
        texts[name] = path.read_text(encoding="utf-8")

    required_text = {
        "start-run": ["Stage 0", "run.yaml", "00-state.md", "resolved gate map",
                      "conditions", "material_dimensions", "otherwise", "when", "then",
                      "NOT_REQUIRED", "run-config-NNN.yaml", "effective_config_revision",
                      "atlas:control-run", "initialize --run", "never edits `00-state.md` directly"],
        "run-file": ["tracer", "CONDITIONAL", "conditions", "otherwise", "overrides"],
        "state-file": ["tracer: NOT_REQUIRED", "effective_config_revision", "effective_config_hash",
                       "approved_artifacts", "accepted_amendments", "blocked_reason"],
        "amendment": ["prior_effective_hash", "top-level replacement semantics", "run.yaml"],
        "control-run": ["tools/atlas_control.py", "only writer", "atlas:control-run",
                        "AGENT_REVIEW", "HUMAN_IF_CHANGED", "implementation gap",
                        "One transition per invocation", "initialize --run", "mark-stale", "apply-amendment", "reopen", "reject"],
        "atlas-control": ["def initialize", "def advance", "def mark_stale", "def apply_amendment", "def reopen", "def reject", "load_effective_run",
                          "prior_effective_hash", "effective_config_hash", "approved_artifacts",
                          "accepted_amendments",
                          "state does not match", "write_files_atomic", "recover_transaction"],
        "discovery": ["run.yaml", "00-state.md", "configured discovery gate", "atlas:control-run",
                      "leave immutable intake unchanged", "return to Stage 0"],
        "run-layout": ["<planning-root>/<feature-slug>/", "run.yaml", "00-state.md"],
        "setup-atlas": ["<planning-root>/<feature-slug>/", "atlas:start-run"],
        "spike": ["workflow authority", "side-effect consent", "explicit confirmation",
                  "immediately before it runs"],
        "to-spec": ["effective `gates.spec`", "atlas:control-run", "status: draft", "gate_ready: true"],
    }
    for name, needles in required_text.items():
        text = texts.get(name, "")
        for needle in needles:
            if needle not in text:
                findings.append(("cross", f"{name}: missing seam contract `{needle}`"))

    # Check structural operands in the actual templates, not only prose mentions.
    structural_fields = {
        "run-file": {
            "planning_root.source", "planning_root.mode", "planning_root.path",
            "recommendation.execution_policy", "recommendation.environment_policy",
            "recommendation.roster", "recommendation.gates",
            "recommendation.reasons.dimension", "recommendation.reasons.evidence",
            "gates.tracer.activation.when", "gates.tracer.authority", "gates.tracer.conditions.when",
            "gates.tracer.conditions.then", "gates.tracer.otherwise",
            "gates.program_design.material_dimensions",
            "repos.repository", "repos.baseline", "overrides.path",
            "overrides.from", "overrides.to", "overrides.reason",
        },
        "state-file": {
            "effective_config_revision", "effective_config_hash", "base_run_sha256",
            "approved_artifacts", "accepted_amendments",
            "gates.tracer", "blocked_reason", "pending_amendment",
        },
        "amendment": {
            "applies_to", "prior_effective_hash", "changes.repos.repository",
            "changes.repos.baseline", "effective_config_revision",
        },
    }
    for name, required in structural_fields.items():
        present = set(template_fields(texts.get(name, "")))
        for field in sorted(required - present):
            findings.append(("cross", f"{name}: template missing structural field `{field}`"))

    # Candidate templates are executable interfaces. Bind each exact documented
    # shape to the controller's literal schemas, including the distinct reopen shape.
    try:
        controller_schemas = assigned_literal(texts.get("atlas-control", ""), "CANDIDATE_FIELDS")
        reopened_schema = set(assigned_literal(
            texts.get("atlas-control", ""), "REOPENED_DISCOVERY_FIELDS"
        ))
        discovery_schema = set(controller_schemas["discovery"])
        spec_schema = set(controller_schemas["spec"])
    except (KeyError, SyntaxError, ValueError) as exc:
        findings.append(("cross", f"controller candidate schemas are unreadable: {exc}"))
    else:
        discovery_maps = [
            set(item) for item in frontmatter_maps(texts.get("run-layout", ""))
            if {"run", "version", "status", "gate_ready"}.issubset(item)
        ]
        spec_maps = [
            set(item) for item in frontmatter_maps(texts.get("spec-file", ""))
            if {"run", "version", "status", "gate_ready"}.issubset(item)
        ]
        if discovery_schema not in discovery_maps:
            findings.append(("cross", "discovery candidate schema does not match controller CANDIDATE_FIELDS"))
        if reopened_schema not in discovery_maps:
            findings.append(("cross", "reopened discovery candidate schema does not match controller REOPENED_DISCOVERY_FIELDS"))
        if spec_schema not in spec_maps:
            findings.append(("cross", "spec candidate schema does not match controller CANDIDATE_FIELDS"))

    banned = {
        "The plan is the gate": "spike may not invent a human workflow gate",
        "Approval is the user's": "spec authority comes from run policy",
        "A run closes on the user's word": "discovery authority comes from run policy",
        "ask whether to run all of them": "spike plan is readiness evidence, not a gate",
        "<planning-root>/<project>/runs": "external roots use the canonical feature-slug layout",
        "per-run judgement": "run placement is fixed beneath the configured root",
        "changeable provenance": "run.yaml must remain immutable provenance",
    }
    joined = "\n".join(texts.values())
    for phrase, reason in banned.items():
        if phrase.lower() in joined.lower():
            findings.append(("cross", f"legacy contract `{phrase}` remains — {reason}"))

    # Stage skills may read run.yaml but never mutate the immutable Stage 0 snapshot.
    for name in ("discovery", "setup-atlas", "spike", "to-spec"):
        for sentence in re.split(r"(?<=[.!?])\s+|\n+", texts.get(name, "")):
            lower = sentence.lower()
            if "run.yaml" not in lower:
                continue
            mutates = re.search(
                r"\b(?:update|edit|modify|rewrite|append(?:\s+to)?|write|replace|change|"
                r"overwrite|delete|remove|revise|amend|mutate)\b",
                lower,
            )
            negated = any(phrase in lower for phrase in ("do not ", "never ", "none edits", "leave ", "unchanged"))
            if mutates and not negated:
                findings.append(("cross", f"{name}: stage skill may not mutate immutable run.yaml — {sentence.strip()}"))

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

        # nested template fields are visible and reported with their complete path
        (d / "SKILL.md").write_text("# x\nThe planning root is required.\n", encoding="utf-8")
        (d / "references" / "t.md").write_text("```yaml\nplanning_root:\n  mode: external\n```\n", encoding="utf-8")
        nested = check(d)
        if not any("planning_root.mode" in msg for _, msg in nested):
            print("SELF-TEST FAIL: nested YAML field was invisible"); ok = False

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

        # Every YAML block must parse, not only the first block in a reference.
        (d / "references" / "t.md").write_text(
            "```yaml\nid: 1\n```\n\n```yaml\nbroken: [\n```\n", encoding="utf-8")
        if not any(k == "template-yaml" for k, _ in check(d)):
            print("SELF-TEST FAIL: malformed later YAML template was invisible"); ok = False

        # Fields from every YAML block participate in governance, not only the first.
        two_blocks = "```yaml\nfirst: 1\n```\n\n```yaml\nsecond: 2\n```\n"
        if set(template_fields(two_blocks)) != {"first", "second"}:
            print("SELF-TEST FAIL: later YAML template fields were invisible"); ok = False

        # Markdown-fenced artifact frontmatter is YAML and must be syntax-checked.
        markdown_frontmatter = "```markdown\n---\nvalid: [\n---\n# Body\n```\n"
        if not template_yaml_errors(markdown_frontmatter):
            print("SELF-TEST FAIL: malformed Markdown-fenced frontmatter was invisible"); ok = False

        # cross-skill: accept the minimum coherent seam, then reject actual pre-fix defects
        seam = Path(td) / "seam-skills"
        minimal = {
            "start-run/SKILL.md": "Stage 0 run.yaml 00-state.md resolved gate map conditions material_dimensions otherwise when then NOT_REQUIRED run-config-NNN.yaml effective_config_revision atlas:control-run initialize --run never edits `00-state.md` directly\n",
            "start-run/references/run-file.md": """tracer CONDITIONAL conditions otherwise overrides
```yaml
planning_root:
  source: x
  mode: external
  path: .
recommendation:
  execution_policy: x
  environment_policy: x
  roster: x
  gates: <complete recommended gate map>
  reasons:
    - dimension: x
      evidence: x
gates:
  tracer:
    activation:
      when: route-evidence
    authority: CONDITIONAL
    conditions:
      - when: x
        then: HUMAN
    otherwise: AGENT_REVIEW
repos:
  - repository: x
    baseline: x
overrides:
  - path: x
    from: x
    to: x
    reason: x
```
```yaml
gates:
  program_design:
    authority: HUMAN_IF_CHANGED
    material_dimensions:
      - behavior
    otherwise: AGENT_REVIEW
```
""",
            "start-run/references/state-file.md": """tracer: NOT_REQUIRED effective_config_revision effective_config_hash base_run_sha256 approved_artifacts accepted_amendments blocked_reason
---
effective_config_revision: 0
effective_config_hash: null
base_run_sha256: null
gates:
  tracer: NOT_REQUIRED
blocked_reason: null
pending_amendment: null
approved_artifacts: {}
accepted_amendments: {}
---
""",
            "start-run/references/run-amendment.md": """prior_effective_hash top-level replacement semantics run.yaml
```yaml
applies_to: run.yaml
prior_effective_hash: x
changes:
  repos:
    - repository: x
      baseline: x
effective_config_revision: 1
```
""",
            "control-run/SKILL.md": "tools/atlas_control.py only writer atlas:control-run AGENT_REVIEW HUMAN_IF_CHANGED implementation gap One transition per invocation initialize --run mark-stale apply-amendment reopen reject\n",
            "../tools/atlas_control.py": """CANDIDATE_FIELDS = {
    "discovery": {"run", "version", "status", "gate_ready"},
    "spec": {"run", "version", "status", "gate_ready", "supersedes"},
}
REOPENED_DISCOVERY_FIELDS = {"run", "version", "status", "gate_ready", "supersedes"}
def initialize(): pass
def advance(): pass
def mark_stale(): pass
def apply_amendment(): pass
def reopen(): pass
def reject(): pass
# load_effective_run prior_effective_hash effective_config_hash approved_artifacts accepted_amendments
# state does not match write_files_atomic recover_transaction
""",
            "discovery/SKILL.md": "run.yaml 00-state.md configured discovery gate atlas:control-run leave immutable intake unchanged return to Stage 0\n",
            "discovery/references/run-layout.md": """<planning-root>/<feature-slug>/ run.yaml 00-state.md
---
run: x
version: 1
status: draft
gate_ready: false
---
reopened
---
run: x
version: 2
status: draft
gate_ready: false
supersedes: approved/discovery-r2.md
---
""",
            "setup-atlas/SKILL.md": "<planning-root>/<feature-slug>/ atlas:start-run\n",
            "spike/SKILL.md": "workflow authority side-effect consent explicit confirmation immediately before it runs\n",
            "to-spec/SKILL.md": "effective `gates.spec` atlas:control-run status: draft gate_ready: true\n",
            "to-spec/references/spec-file.md": """---
run: x
version: 1
status: draft
gate_ready: false
supersedes: null
---
""",
        }
        for rel, content in minimal.items():
            path = seam / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        if cross_skill_contracts(seam):
            print("SELF-TEST FAIL: cross-skill check rejected the minimum coherent seam"); ok = False

        # Candidate schemas are executable interfaces: each documented initial/reopen
        # shape must stay byte-independent and exact against controller constants.
        layout = seam / "discovery" / "references" / "run-layout.md"
        layout.write_text(
            minimal["discovery/references/run-layout.md"].replace("version: 1\n", "", 1),
            encoding="utf-8",
        )
        if not any("discovery candidate schema" in msg for _, msg in cross_skill_contracts(seam)):
            print("SELF-TEST FAIL: discovery candidate field deletion was invisible"); ok = False
        layout.write_text(minimal["discovery/references/run-layout.md"], encoding="utf-8")

        reopened = "---\nrun: x\nversion: 2\nstatus: draft\ngate_ready: false\nsupersedes: approved/discovery-r2.md\n---\n"
        layout.write_text(
            minimal["discovery/references/run-layout.md"].replace(reopened, ""),
            encoding="utf-8",
        )
        if not any("reopened discovery candidate schema" in msg for _, msg in cross_skill_contracts(seam)):
            print("SELF-TEST FAIL: reopened discovery schema absence was invisible"); ok = False
        layout.write_text(minimal["discovery/references/run-layout.md"], encoding="utf-8")

        spec_ref = seam / "to-spec" / "references" / "spec-file.md"
        spec_ref.write_text(
            minimal["to-spec/references/spec-file.md"].replace("supersedes: null\n", ""),
            encoding="utf-8",
        )
        if not any("spec candidate schema" in msg for _, msg in cross_skill_contracts(seam)):
            print("SELF-TEST FAIL: spec candidate field deletion was invisible"); ok = False
        spec_ref.write_text(minimal["to-spec/references/spec-file.md"], encoding="utf-8")

        # A prose mention cannot substitute for a missing conditional-policy operand in the template.
        run_ref = seam / "start-run" / "references" / "run-file.md"
        run_ref.write_text(minimal["start-run/references/run-file.md"].replace(
            "    otherwise: AGENT_REVIEW\n", ""), encoding="utf-8")
        if not any("gates.tracer.otherwise" in msg for _, msg in cross_skill_contracts(seam)):
            print("SELF-TEST FAIL: structural check accepted a tracer policy without fallback"); ok = False
        run_ref.write_text(minimal["start-run/references/run-file.md"], encoding="utf-8")

        # A required operand in a later template block must remain structurally enforced.
        run_ref.write_text(minimal["start-run/references/run-file.md"].replace(
            "    material_dimensions:\n      - behavior\n", ""), encoding="utf-8")
        if not any("gates.program_design.material_dimensions" in msg
                   for _, msg in cross_skill_contracts(seam)):
            print("SELF-TEST FAIL: later-block material_dimensions was not enforced"); ok = False
        run_ref.write_text(minimal["start-run/references/run-file.md"], encoding="utf-8")

        # This exact phrase was the real spec authority leak before the Stage 0 fix.
        (seam / "to-spec" / "SKILL.md").write_text(
            minimal["to-spec/SKILL.md"] + "Approval is the user's.\n", encoding="utf-8")
        if not any("Approval is the user's" in msg for _, msg in cross_skill_contracts(seam)):
            print("SELF-TEST FAIL: cross-skill check accepted the pre-fix spec authority leak"); ok = False

        # The previous external-root reference used this extra project/runs hierarchy.
        layout = seam / "discovery" / "references" / "run-layout.md"
        layout.write_text(minimal["discovery/references/run-layout.md"] +
                          "<planning-root>/<project>/runs/<slug>/\n", encoding="utf-8")
        if not any("<planning-root>/<project>/runs" in msg for _, msg in cross_skill_contracts(seam)):
            print("SELF-TEST FAIL: cross-skill check accepted the pre-fix external layout"); ok = False
        layout.write_text(minimal["discovery/references/run-layout.md"], encoding="utf-8")

        # Required phrases must not mask a contradictory instruction to mutate immutable intake.
        discovery = seam / "discovery" / "SKILL.md"
        discovery.write_text(minimal["discovery/SKILL.md"] + "Update run.yaml with the wider repository scope.\n",
                             encoding="utf-8")
        if not any("may not mutate immutable run.yaml" in msg for _, msg in cross_skill_contracts(seam)):
            print("SELF-TEST FAIL: cross-skill check accepted run.yaml mutation"); ok = False
        discovery.write_text(minimal["discovery/SKILL.md"], encoding="utf-8")

        # Synonyms must not evade immutable-intake enforcement, while explicit
        # prohibitions must not become false positives.
        for verb in ("Replace", "Change", "Overwrite", "Revise", "Amend", "Mutate"):
            discovery.write_text(
                minimal["discovery/SKILL.md"] + f"{verb} run.yaml with the widened repository scope.\n",
                encoding="utf-8",
            )
            if not any("may not mutate immutable run.yaml" in msg for _, msg in cross_skill_contracts(seam)):
                print(f"SELF-TEST FAIL: cross-skill check accepted `{verb} run.yaml`"); ok = False
            discovery.write_text(
                minimal["discovery/SKILL.md"] + f"Never {verb.lower()} run.yaml.\n",
                encoding="utf-8",
            )
            if any("may not mutate immutable run.yaml" in msg for _, msg in cross_skill_contracts(seam)):
                print(f"SELF-TEST FAIL: cross-skill check rejected negated `{verb} run.yaml`"); ok = False
        discovery.write_text(minimal["discovery/SKILL.md"], encoding="utf-8")

        # Restore the good spec, then prove absence of Stage 0 is rejected independently.
        (seam / "to-spec" / "SKILL.md").write_text(minimal["to-spec/SKILL.md"], encoding="utf-8")
        (seam / "start-run" / "SKILL.md").unlink()
        if not any("missing first-party seam file" in msg for _, msg in cross_skill_contracts(seam)):
            print("SELF-TEST FAIL: cross-skill check accepted a missing Stage 0"); ok = False

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
    all_findings += cross_skill_contracts(SKILLS)

    hard = [f for f in all_findings if f[0] in ("forward", "reverse", "cross", "template-yaml")]
    soft = [f for f in all_findings if f[0] == "forward-weak"]
    skip = [f for f in all_findings if f[0] == "skipped"]

    for kind, msg in hard + soft + skip:
        print(f"{kind:13} {msg}")
    print(f"\n{len(hard)} findings, {len(soft)} weak, {len(skip)} skipped")
    return 1 if hard else 0


if __name__ == "__main__":
    raise SystemExit(main())
