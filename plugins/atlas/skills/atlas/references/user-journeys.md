# User journeys and accessible interaction

Use when an interactive change needs end-to-end, usability or accessibility evidence. Identify the users, platform, critical journey, accepted interaction and available test environment. Use existing approved browser/device/test capabilities; this runbook does not require a browser package or hosted artifact service.

Follow the user's goal through the real interaction and observable result. Include relevant loading, empty, success, error and retry states, repeated actions, navigation and persistence. Assert meaningful results rather than only that a button was clicked. Isolate test data and avoid real purchases, messages or account changes without applicable authority. Wait for the relevant condition rather than arbitrary delays; record a failure before attempting recovery.

Inspect semantic name/role/value, keyboard reachability, logical focus order, focus movement and restoration, status/error announcements, non-color cues and usable zoom/text scaling/reflow. Prefer native controls when they supply the right interaction. For a modal, check opening focus, contained navigation, dismissal and return to the invoker. A screenshot cannot prove keyboard or assistive-technology behavior; automated accessibility checks alone do not establish conformance. Verify any claimed standard/version and required criteria from authoritative project or standards sources.

Match responsive/device checks to the actual layout and supported platforms. Check that visual polish preserves content hierarchy, readability and functional states. Aesthetic scores cannot override broken tasks or required accessibility. Use [client state](client-state-checks.md) when lifecycle or stale responses explain the failure.

For public pages whose goal includes search discovery, inspect intended indexing, canonical/redirect behavior, crawl directives, meaningful links and structured-data consistency. Internal/private pages may correctly be non-indexable. Verify current search-engine rules before promising compliance or ranking outcomes; do not manufacture SEO requirements for an internal app.

Keep traces/screenshots/logs only where they help diagnose or prove the claim, inside the approved environment. Separate live interaction, screenshot inspection, static code analysis and automated tests in the report. A flaky test is unresolved evidence; quarantine or reduced coverage must stay visible and follow project policy. Stop when the important journey claims are proven or a concrete missing capability prevents verification.
