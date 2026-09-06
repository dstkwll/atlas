# Data, concurrency and migrations

Use when changing persistence, queries, schemas, permissions, transactions or rolling deployment behavior. Identify the actual database/version, dataset shape, read/write callers and production change authority. Inspect schema, migrations, queries and existing operational evidence before recommending database-specific syntax.

Locate ownership of integrity: uniqueness, foreign keys, nullability, valid state and precision. Application checks may race; database constraints may protect only some write paths. Trace concurrent updates and transaction isolation rather than assuming a read-then-write sequence is atomic. Keep lock ordering consistent and inspect what happens on retry, deadlock, cancellation or uncertain commit.

Plan coexistence of old and new readers/writers during deployment. Check defaults, backfills, duplicate/null cleanup, renamed or removed fields and rollback compatibility. A migration passing on an empty database says little about locks, rewrite cost or legacy records. Destructive changes, fake migration history and resets are not routine build fixes. If a rollback cannot restore lost information, state the recovery method and required decision.

For query performance, use representative cardinality, selectivity and access patterns. Trace N+1 access and unbounded result growth; inspect query plans using approved facilities. An index has write/storage costs and a sequential scan can be appropriate. Do not demand an index on every column, universal key types or one vendor's row-security convention. Query-plan execution tools may actually execute mutations; inspect their effects before running them.

Examine tenant filters, row policies and privileged connections along the actual path. Check pool exhaustion, connection/session cleanup, transaction duration and external calls while locks are held. Batching, pagination and queue locking must preserve ordering, fairness and consistency obligations as well as throughput.

Use disposable representative data for migration/recovery and concurrency checks when authorized. Record engine/version, data assumptions, measured lock/query effects, integrity checks and whether rollback or forward recovery was actually exercised. If only static inspection is possible, bound the claim accordingly.

Return the correctness and rollout risks, smallest supported change, and evidence needed before any live execution. Use [failure handling](failure-handling.md) for effects spanning multiple resources and [performance](performance.md) for measurement design.
