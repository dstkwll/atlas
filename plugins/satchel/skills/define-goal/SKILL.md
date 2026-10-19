---
name: define-goal
description: Define or refine a measurable goal, its scope and success criteria. Use for goal drafting or requested goal-tool creation, not task execution or progress tracking.
---

# Define Goal

Modified for Satchel.

## Overview

Shape the user's intent into an objective an agent can pursue honestly. Prefer measurable outcomes, explicit evidence, and bounded scope over activity descriptions.

This skill covers goal definition and native goal creation when requested and available, with a text-only objective fallback when goal tools are unavailable. Do not create intermediate planning artifacts, durable snapshots, ledgers, decision logs, or resume files from this skill.

## Workflow

1. Confirm that goal definition is actually needed.
   - Use this skill when the user asks for `$define-goal`, asks to create or set a goal, asks for the goal tool, or wants help turning an intention into a clear objective.
   - If the user only asks for ordinary implementation work, do the work directly instead of forcing goal creation.

2. Restate the likely goal in concrete terms.
   A usable goal names:
   - the specific outcome that will be true
   - the main artifact, system, repo, environment, or user-facing behavior involved
   - how completion will be verified
   - what is in scope
   - what is out of scope when ambiguity would matter
   - the stop condition for asking the user instead of grinding

3. Make it quantitative when the domain supports it.
   Prefer numbers that represent real success, not decorative precision:
   - pass/fail validators: exact tests, checks, CI jobs, evals, commands, or acceptance criteria
   - quality thresholds: latency, error rate, cost, accuracy, recall, precision, coverage, flake rate, bundle size, memory, uptime, completion rate, or manual review criteria
   - artifact constraints: file paths, affected modules, allowed commands, output formats, target environments, deadlines, or maximum blast radius
   - evidence counts: number of reproduced failures, successful reruns, reviewed examples, migrated records, addressed comments, or verified cases

4. Repair weak goals before setting them.
   - Rewrite vague goals into measurable objectives when local context makes the rewrite safe.
   - Ask one concise clarification question when the missing detail changes the intended outcome or validation.
   - Reject pure activity goals such as "make progress," "keep investigating," "improve things," or "work on X" unless they are sharpened into a verifiable outcome.

5. When the user asks to create or set a goal, use the goal tool, or otherwise explicitly requests goal-backed work, and native goal tools are available, check active goal state before creating a goal.
   - A request only to define or refine the wording, including invoking this skill without asking to save or activate a goal, returns a draft objective instead.
   - Follow the host's goal-tool instructions and supported operations. Call `get_goal`.
   - If there is no active goal and the objective meets the quality bar, call `create_goal`.
   - If there is an active goal that still matches the user's intent, continue using it instead of creating a duplicate.
   - If there is an active goal that differs from the new request (unrelated or conflicting), preserve it and ask how to proceed. Mark it complete only if it is done. Offer a separate goal-backed thread only if the host supports one; otherwise retain the new objective as text until the conflict is resolved.

6. When creating a native goal, apply the quality bar.
   - Use a single concise objective string.
   - Include the verification evidence in the objective itself.
   - Include scope bounds when they constrain the work.
   - Include a token budget only when the user explicitly requested one.
   - Do not call `create_goal` for an ordinary multi-step task unless the user explicitly asked for goal-backed work.

7. Return the objective and its actual status.
   - For definition or refinement only, or when native goal tools are unavailable, return the final objective in a copyable text block without claiming a persistent goal was created.
   - If native creation was requested, report the actual outcome: a new goal was created, a matching goal was retained, or no goal was created because tools are unavailable or a conflict or clarification is pending. If an attempted creation failed or remains unconfirmed, say so; check current goal state before retrying. A missing acknowledgment is not proof that nothing was created.
   - Do not start executing the objective unless the user has also authorized that work; existing authorization needs no additional confirmation.

## Goal Quality Bar

Before creating a goal or returning the final objective, the objective should answer:

- What concrete thing will be true when this is done?
- What evidence will prove it?
- What quantitative or binary threshold defines success?
- What scope boundaries matter?
- What should cause the agent to stop and ask?

Good:

> Reduce checkout API p95 latency below 250 ms for the documented slow path by making the smallest safe server-side change, then verify with `npm run test:checkout` and the existing local latency benchmark showing p95 under 250 ms across 3 consecutive runs.

Good:

> Resolve the open review comments on PR 123 that request code changes, update only the affected auth files and tests, and verify with the targeted auth test command plus `gh pr view 123` showing no unresolved change-request threads.

Weak:

> Make checkout faster.

Weak:

> Keep investigating the PR comments.

## Quantification Heuristics

- For bugs, define success as reproduction first, fix second, and a failing-then-passing validator when possible.
- For tests, name the exact command and required pass condition.
- For performance, name the metric, target threshold, measurement method, and number of runs.
- For quality work, define an observable acceptance bar such as reviewed examples, lint/typecheck/test pass, or user-approved artifact.
- For research, define the decision the research must enable, the sources or systems in scope, and the evidence standard.
- For operations, define healthy state, monitoring window, failure threshold, and rollback or escalation trigger.

## Clarifying Questions

Ask only when a reasonable rewrite would risk pursuing the wrong outcome. Keep the question short and oriented around the missing validator or scope boundary.

Useful question shapes:

- "What metric should define success here: latency, cost, accuracy, or user-visible behavior?"
- "Which environment should I verify against: local, staging, or production?"
- "What is the minimum evidence you want before I mark this goal complete?"

If the user cannot provide a metric, propose the most honest binary validator available and ask for confirmation.
