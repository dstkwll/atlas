# Internal owner loading

Atlas internal owners remain non-implicit. This file defines how one already-selected owner loads the next named owner without teaching the user an internal command or broadening skill discovery.

1. **The caller chooses only from its existing named handoff contract.** This procedure never derives a stage, invents `next_skill`, or chooses legality.
2. **Prefer the host's safe nested skill invocation mechanism.** Require the host to confirm that the exact named sibling loaded before following it.
3. **Use the calibrated procedure-load fallback only when host metadata blocks nested invocation.** Resolve `<atlas-plugin-root>/skills/<exact-owner>/SKILL.md` from the caller's installed root, require that exact path to be a real non-symlinked file beneath `skills/`, read it completely, and follow it as the current owner procedure in the same conversation. Loading a named procedure this way does not make the sibling implicit and does not authorize another owner.
4. **Fail closed.** A missing, unreadable, symlinked, or differently named procedure is an installed-host blocker. Do not search for a substitute, copy cached instructions, or ask the user to type the internal skill name.
5. **Preserve ownership.** The loaded owner retains the conversation through its questions and defined controller handoff. The caller resumes only when that procedure returns.

Installed-host calibration must report whether each handoff used confirmed nested invocation or this calibrated procedure-load fallback. A direct file read outside this exact named-owner path is diagnostic only and is not a handoff.
