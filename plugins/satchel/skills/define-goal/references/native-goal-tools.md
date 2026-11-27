# Native goal tools

Modified for Satchel.

Use when the user asked to create or set a goal, use the goal tool, or otherwise explicitly requested goal-backed work, and native goal tools are available. Follow the host's goal-tool instructions and supported operations.

## Check active goal state before creating a goal

- Call `get_goal`.
- If there is no active goal and the objective meets the quality bar, call `create_goal`.
- If there is an active goal that still matches the user's intent, continue using it instead of creating a duplicate.
- If there is an active goal that differs from the new request (unrelated or conflicting), preserve it and ask how to proceed. Mark it complete only if it is done. Offer a separate goal-backed thread only if the host supports one; otherwise retain the new objective as text until the conflict is resolved.

## Apply the quality bar when creating a native goal

- Use a single concise objective string.
- Include the verification evidence in the objective itself.
- Include scope bounds when they constrain the work.
- Include a token budget only when the user explicitly requested one.
- Do not call `create_goal` for an ordinary multi-step task unless the user explicitly asked for goal-backed work.

Then return to the skill's final step and report the goal's actual status.
