# Import service
The importer synchronizes remote records for a tenant. A successful completed job means that the source was read and the corresponding records were stored. Callers may retry a failed job ID. A retried completed job must not duplicate stored rows. Jobs and records are tenant-scoped. This snapshot is a review candidate; do not edit it.
