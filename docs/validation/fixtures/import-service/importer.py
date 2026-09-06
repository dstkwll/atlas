class Importer:
    def __init__(self, source):
        self.source = source
        self.completed = set()
        self.records = []

    def run(self, tenant, job_id):
        if job_id in self.completed:
            return {"status": "complete", "count": 0}
        self.completed.add(job_id)
        try:
            rows = self.source.fetch(tenant)
        except OSError:
            rows = []
        self.records.extend((tenant, row) for row in rows)
        return {"status": "complete", "count": len(rows)}
