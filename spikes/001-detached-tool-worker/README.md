# 001: detached tool-enabled hermes worker

**Question (sol's T0 blind spot):** Can a *detached, tool-enabled* `hermes -z` worker
stand up unattended and actually GROUND work (web) + emit an ARTIFACT (file), surviving
the MCP cold-start that killed the earlier cron-agent approach?

**Given** a detached `hermes -z '<prompt>' -m opus --provider copilot -t web,file --yolo`
**When** it is asked to research a fact and write a file
**Then** it should cold-start clean, use web, write the artifact, exit 0.

## Runs

- **T1** (`-t web,file --cli`, relative path `artifact.md`): exit 0 in 13s, printed
  `WORKER_DONE`, but **NO web search and NO file**. Looked like a fabricated "done."
- **T2** (`-t file`, relative path `t2.md`): exit 0, printed DONE2 — **file WAS written,
  but to `~/t2.md` (Hermes's own cwd = home), not the subprocess `$PWD`.** This explained T1.
- **T3** (`-t web,file`, ABSOLUTE path): exit 0, **web search ran**, artifact written with
  the real elevation + source URL, printed DONE3. ✅

## Verdict: VALIDATED (with one hard constraint)

### What worked
- `-z` DOES run the full tool loop headless (not just a single completion).
- `-t web,file` scoping **avoids the MCP cold-start stall** — gmail/monarch MCP never load,
  so the detached worker starts clean. This is the neutralizer the topology depends on.
- Real web grounding + file artifact + clean exit 0, unattended, under the perl-alarm timeout.
- `--yolo` needed so the detached worker doesn't block on an approval prompt (no TTY).

### What didn't / the trap
- **The file tool resolves RELATIVE paths against Hermes's OWN cwd (home dir), NOT the
  spawning shell's `$PWD`.** A relative-path artifact silently lands in the wrong place and
  looks like the worker "faked done." → **The worker prompt MUST pass an ABSOLUTE artifact
  path** (the launcher computes it from the Card id and injects it). This is a plan-level
  contract, not a nicety.

### Surprises
- T1's "fabricated done" was NOT the model lying — it was the cwd trap. But it's a vivid live
  demonstration of exactly WHY the constitution says "never trust self-reported done": the
  gate must verify the artifact exists AT THE EXPECTED ABSOLUTE PATH, not read stdout.

### Recommendation for the real build
1. Port-2 personal adapter = detached `hermes -z ... -m opus --provider copilot -t web,file --yolo`.
2. Launcher injects an **absolute** artifact path derived from card_id; worker contract requires it.
3. The completion CHECK = "artifact file exists at the expected absolute path + non-empty +
   parses" — exit-0/stdout is NEVER the proof (T1 proves why).
4. Keep the worker toolset MINIMAL (`web,file`) — it's both the MCP-stall fix AND the
   surface-only/no-actions guardrail (no gmail/monarch/send tools in scope = can't act).
5. Timeout via `perl -e 'alarm shift; exec @ARGV' <secs>` (macOS has no `timeout`).
