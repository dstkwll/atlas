"""Synthetic composition projects; evaluator expectations are kept separately."""

FIXTURES = {
    'composition-onboarding': {
        'README.md': '''# Equipment team onboarding
Coordinators onboard seasonal staff from a CSV supplied by their local manager.
They currently copy every row into a form and chase unclear matches by email.
The first release should reduce that repeated entry without replacing the company
directory, authentication service or existing manager approval service.
All names and addresses here are synthetic. No directory service is connected.

Accepted access rule: only a manager may approve an equipment-account grant.
An approval identifies the directory person and role, not merely a display name
or an email typed into this screen. Coordinators may prepare the request.
Unresolved rows must not acquire access. Each row may progress independently.
The manager approval service already supports approving selected valid requests.
Importing a file and sending an approval request do not mean access was granted.

The attached HTML is a static proposal, not an implemented or tested workflow.
The matching helper is an earlier prototype; it has not been accepted for release.
Design only. Notes may be saved under planning/onboarding/; no source changes,
real invitations, directory updates, account operations or deployment.
''',
        'import.csv': '''name,email,role
Alex Chen,alex.chen@seasonal.invalid,operator
Jamie Orr,jamie.orr@seasonal.invalid,operator
Morgan Vale,morgan.vale@seasonal.invalid,operator
''',
        'directory.json': '''[
  {"id": "person-17", "name": "Alex Chen", "email": "alex.north@directory.invalid", "team": "North"},
  {"id": "person-24", "name": "Alex Chen", "email": "alex.south@directory.invalid", "team": "South"},
  {"id": "person-31", "name": "Jamie Orr", "email": "jamie.orr@directory.invalid", "team": "North"}
]
''',
        'matching.py': '''def prepare_request(row, directory):
    matches = [person for person in directory
               if person['name'].casefold() == row['name'].casefold()]
    return {'name': row['name'], 'email': row['email'], 'role': row['role'],
            'person_id': matches[0]['id'] if matches else None,
            'status': 'ready'}
''',
        'proposal.html': '''<!doctype html>
<html lang="en"><meta charset="utf-8"><title>Import staff</title>
<main><h1>Welcome your team</h1><p>3 staff ready to start</p>
<table><tr><th>Name</th><th>Email</th><th>Role</th><th>Status</th></tr>
<tr><td>Alex Chen</td><td><input value="alex.chen@seasonal.invalid"></td><td>Operator</td><td>Ready</td></tr>
<tr><td>Jamie Orr</td><td><input value="jamie.orr@seasonal.invalid"></td><td>Operator</td><td>Ready</td></tr>
<tr><td>Morgan Vale</td><td><input value="morgan.vale@seasonal.invalid"></td><td>Operator</td><td>Ready</td></tr>
</table><button>Give all staff access</button>
<p>Editing an email updates the recipient for that row.</p></main></html>
''',
    },
    'composition-reveal': {
        'README.md': '''# Workshop job search
Dispatchers look up service jobs while talking to customers. The initial pilot
has one workshop. Every typed query currently waits for another server response;
returning to a recent query is especially annoying on a weak connection.
Keep the existing search endpoint, authentication and application. Search is
read-only and should continue showing the server's current visit status.
No browser measurements or representative network captures are available here.
This is design work; notes may be saved under planning/search/. Do not edit
application files, make service calls, change permissions or run a live server.
''',
        'api.md': '''# Existing endpoint
GET /jobs/search?q=... returns jobs allowed by the signed-in session.
The server checks permission on every request before returning rows.
Each row contains id, customer_name, address, access_note and visit_status.
The authenticated transport is supplied to the client; this fixture does not
contain credentials, server implementation or a runnable service.
''',
        'search.js': '''export async function searchJobs(query, fetchJobs, render) {
  render({ state: 'loading', rows: [] });
  try {
    const rows = await fetchJobs(query.trim());
    render({ state: 'ready', rows });
  } catch {
    render({ state: 'error', rows: [] });
  }
}
''',
        'proposal.md': '''# Team suggestion
Cache returned rows by normalized query in the browser. Show them immediately
when the same query is typed again, with no request while the entry is younger
than ten minutes. Persist the cache so refreshes can reuse it. The ten-minute
value is a suggestion; no freshness target or measurement supports it yet.
''',
    },
}
