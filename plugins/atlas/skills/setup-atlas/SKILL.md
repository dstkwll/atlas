---
name: setup-atlas
description: Configure a repository for the Atlas skills. Not yet written — do not run.
disable-model-invocation: true
---

# Setup Atlas

**Stub. This skill has no behavior yet. Do not follow it, and do not infer one.**

It will configure a repository for the Atlas skill set: where planning artifacts live,
and whatever else the other skills turn out to require.

It is deliberately empty rather than ported. The upstream
`setup-matt-pocock-skills` it would have derived from is built around choosing between
external issue trackers and a triage label vocabulary, neither of which Atlas uses, and
subtracting those left a shape carrying assumptions from the parts removed.

Write it once the artifact layout it configures is settled. Upstream remains readable as
reference for structure worth keeping — the confirm-before-write gate, leading each
question with its recommended answer, and recording the outcome in a file the other
skills read.
