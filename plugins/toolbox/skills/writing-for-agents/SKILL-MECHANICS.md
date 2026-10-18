# Skill mechanics

The skill-specific branch of [`writing-for-agents`](SKILL.md): what changes when the document is a skill (frontmatter, the invocation choice, and router skills). Everything else about writing it is the universal reference in `SKILL.md`.

## Invocation

Two intended discovery patterns can shift the two loads. Their actual behavior is a host capability to verify:

- A **model-invoked** skill can be selected automatically when its description matches the request. It may also be explicitly selectable by the user or reachable from other guidance. Write the description as the skill's top-level context pointer, carrying its purpose and trigger branches (the pointer-writing rules in `SKILL.md` apply in full). A model-invoked skill whose content is all reference can hold shared guidance if its callers can reliably reach it.
- A **user-invoked** skill reserves starting the method for the human's explicit choice where the host supports that policy. This spends cognitive load: the user must know it exists. It does not inherently remove its metadata from context, hide its files or enforce an authority boundary.

Keep normal automatic discovery unless the user requests explicit-only invocation; preserve an existing invocation policy unless asked to change it. Invocation policy and permission to perform an action are separate: discovering a skill does not authorize publication or another consequential mutation.

Verify the target host's supported metadata and loading mechanism before choosing invocation fields or tool names. Check what is visible before invocation, how explicit selection works, and how references are read. A host may use a skill tool or ordinary file access; no frontmatter flag, hidden description or zero-context claim is universal. Keep the description meaningful when the host exposes it.

Shared reference can live in a plain file that each caller links directly. When the skill being authored must install independently, bundle the files it needs. Shared references are also valid when callers ship together or declared dependencies are actually available; verify that availability instead of inferring it from the author's checkout. Reading a reference is not a separate worker or a fresh context.

## Frontmatter and paths

Use a concise name and a description stating both what the skill does and when to use it; check the target host's syntax and limits. Include exclusions only where they prevent a likely mismatch. Keep detailed procedure in the body. Resolve bundled reference links from the skill folder, and identify task-workspace paths explicitly so a reader does not write output into the installed skill.

## Splitting by invocation

The invocation cut of splitting (the sequence cut lives in `SKILL.md`): consider a separate skill when a distinct capability should be discoverable on its own, or another method needs that reusable behavior. A leading word you actually use in requests can help name it; demonstrate the independent use case. Additional discovery metadata and a new human choice have costs, so independent reach has to be worth them.

## Router skills

When users demonstrably struggle to find the right skill, a **router** or a simple catalog can name the available choices and when each applies. Add one only when it reduces that burden; a small collection may need neither. Whether a router can invoke a target depends on host capabilities and the target's invocation policy. Preserve the user's control and the original task's authority rather than treating routing as permission.
