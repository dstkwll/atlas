# Security boundaries

Use for a requested security review or a change that materially affects authentication, authorization, untrusted input, sensitive data or externally reachable operations. Establish the assets, caller identities, trust boundaries, deployment assumptions and authorized inspection scope. Use approved local tools and current authoritative references where needed; no scanner installation is required by this runbook.

Trace an input to the sensitive operation. Identify validation and encoding at the relevant boundary, not merely the presence of a sanitizer somewhere. Parameterized database access, structured process arguments, path containment and context-appropriate output encoding address different problems. Framework defaults count only when the actual version and call path use them.

Separate authentication from authorization. Check object ownership, tenant isolation, privilege changes and background/admin paths. A route guard may identify a user without authorizing the selected record. Browser-origin policy is not access control. Test both allowed and denied cases, including access through alternate identifiers or stale credentials, in a permitted test environment.

For outbound requests and file handling, inspect redirects, resolved destinations, path normalization, archive extraction and resource limits where attacker control reaches them. For callbacks/webhooks, determine how authenticity, freshness and replay are enforced. For concurrent state changes, verify that checking permission or balance and applying the effect cannot race.

Follow secrets and private data through configuration, logs, errors, caches, exports and artifacts. Show redacted locations and exposure paths rather than reproducing sensitive values. An example credential may be harmless; an actual leaked credential is not fixed solely by moving it into an environment variable. Report the exposure and required owner action; rotation, deletion, incident notification or production changes need applicable authority.

Validate dependency findings against the resolved version, affected functionality and exposure. Do not treat every available update as required, or a clean scanner as proof of safety. When official advisories or deployment evidence cannot be reached, say which conclusion is limited.

Return concrete attack preconditions, reachable effect, missing/ineffective guard and evidence, plus bounded remediation and unverified paths. Accept zero findings when supported. Keep secure defaults and least privilege tied to actual boundaries instead of adding unrelated controls.
