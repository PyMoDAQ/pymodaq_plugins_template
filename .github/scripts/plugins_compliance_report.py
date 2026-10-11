"""Print which PyMoDAQ plugin repositories still do not follow the plugin template.

Maintainer tool, run by hand (never in CI)::

    python .github/scripts/plugins_compliance_report.py                 # every pymodaq_plugins_* repo of the org
    python .github/scripts/plugins_compliance_report.py basler thorlabs # only these (short names or full names)
    python .github/scripts/plugins_compliance_report.py --markdown      # paste in an issue / a message to maintainers
    python .github/scripts/plugins_compliance_report.py --json

Only reads GitHub (public API; set GH_TOKEN/GITHUB_TOKEN to raise the rate limit or see private repositories).
Standard library only. Archived repositories and forks are skipped.

Checks, each ``ok`` / ``MISSING`` / ``OLD`` (what the template ships today):
  agents    AGENTS.md and CLAUDE.md at the root
  tests     tests/test_plugin_package_structure.py imports ``pymodaq.utils.plugin_testing`` (PyMoDAQ >= 5.3.2)
  workflows tests.yml, compatibility.yml and python-publish.yml are the tiny callers of the template reusable
            workflows, and no legacy Test.yml / Testbase.yml / updater.yml is left
  floor     ``pymodaq>=X`` in pyproject.toml is at least the template's (5.3.2)
The ``PR`` column tells whether an open pull request already touches the plugin tests (the "use the plugin acceptance
checks" series), which then needs to be updated or replaced rather than duplicated.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.request

ORG = 'PyMoDAQ'
TEMPLATE = f'{ORG}/pymodaq_plugins_template'
CALLERS = {'tests.yml': 'reusable-tests.yml', 'compatibility.yml': 'reusable-compatibility.yml',
           'python-publish.yml': 'reusable-publish.yml'}
LEGACY = ('Test.yml', 'Testbase.yml', 'updater.yml')
FLOOR = (5, 3, 2)
API = 'https://api.github.com'


def request(url: str, raw: bool = False):
    if url.startswith(API) and shutil.which('gh'):  # gh knows the credentials (higher rate limit than anonymous)
        done = subprocess.run(['gh', 'api', url[len(API):]], capture_output=True, text=True)
        if done.returncode == 0:
            return json.loads(done.stdout)
    return _request(url, raw)


def _request(url: str, raw: bool = False):
    headers = {'Accept': 'application/vnd.github+json', 'User-Agent': 'plugins-compliance-report'}
    token = os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
    for use_token in ((True, False) if token else (False,)):
        if use_token:
            headers['Authorization'] = f'Bearer {token}'
        else:
            headers.pop('Authorization', None)  # an invalid token is refused, public data does not need one
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30) as response:
                body = response.read().decode()
            return body if raw else json.loads(body)
        except urllib.error.HTTPError as error:
            if error.code not in (401, 403) or not use_token:
                raise


def list_repos() -> list:
    repos, page = [], 1
    while True:
        batch = request(f'{API}/orgs/{ORG}/repos?per_page=100&type=public&page={page}')
        if not batch:
            break
        repos += batch
        page += 1
    return sorted(r['name'] for r in repos
                  if r['name'].startswith('pymodaq_plugins_') and not r['archived'] and not r['fork']
                  and r['full_name'] != TEMPLATE)


def fetch(full_name: str, branch: str, path: str) -> str:
    try:
        return request(f'https://raw.githubusercontent.com/{full_name}/{branch}/{path}', raw=True)
    except urllib.error.HTTPError:
        return ''


def parse_floor(pyproject: str):
    match = re.search(r'["\']pymodaq\s*>=\s*(\d+)\.(\d+)(?:\.(\d+))?', pyproject)
    return tuple(int(g or 0) for g in match.groups()) if match else None


def check(name: str) -> dict:
    full_name = f'{ORG}/{name}'
    info = request(f'{API}/repos/{full_name}')
    branch = info['default_branch']
    tree = {t['path'] for t in request(f'{API}/repos/{full_name}/git/trees/{branch}?recursive=1')['tree']}
    result = {'repo': name, 'branch': branch}

    missing = [f for f in ('AGENTS.md', 'CLAUDE.md') if f not in tree]
    result['agents'] = ('MISSING ' + ', '.join(missing)) if missing else 'ok'

    stub = 'tests/test_plugin_package_structure.py'
    if stub not in tree:
        result['tests'] = 'MISSING'
    elif 'pymodaq.utils.plugin_testing' in fetch(full_name, branch, stub):
        result['tests'] = 'ok'
    elif 'pymodaq_utils.plugin_testing' in fetch(full_name, branch, stub):
        result['tests'] = 'OLD (pymodaq_utils.plugin_testing)'
    else:
        result['tests'] = 'OLD (generic copy of the template tests)'

    problems = []
    for workflow, reusable in CALLERS.items():
        path = f'.github/workflows/{workflow}'
        if path not in tree:
            problems.append(f'no {workflow}')
        elif f'{TEMPLATE}/.github/workflows/{reusable}' not in fetch(full_name, branch, path):
            problems.append(f'{workflow} is not the template caller')
    problems += [f'legacy {f}' for f in LEGACY if f'.github/workflows/{f}' in tree]
    result['workflows'] = '; '.join(problems) or 'ok'

    floor = parse_floor(fetch(full_name, branch, 'pyproject.toml'))
    if floor is None:
        result['floor'] = 'MISSING pymodaq>=X'
    elif floor < FLOOR:
        result['floor'] = 'OLD pymodaq>=' + '.'.join(map(str, floor))
    else:
        result['floor'] = 'ok'

    pulls = request(f'{API}/repos/{full_name}/pulls?state=open&per_page=100')
    mine = [f"#{p['number']}" for p in pulls
            if re.search(r'plugin acceptance|plugin_testing|plugin acceptance checks', p['title'] + p['head']['ref'], re.I)]
    result['pr'] = ' '.join(mine) or '-'
    result['compliant'] = all(result[k] == 'ok' for k in ('agents', 'tests', 'workflows', 'floor'))
    return result


def render(rows: list, markdown: bool) -> str:
    columns = ['repo', 'agents', 'tests', 'workflows', 'floor', 'pr']
    lines = []
    if markdown:
        lines.append('| ' + ' | '.join(columns) + ' |')
        lines.append('|' + '---|' * len(columns))
        lines += ['| ' + ' | '.join(str(r.get(c, '')) for c in columns) + ' |' for r in rows]
    else:
        widths = {c: max(len(c), *(len(str(r.get(c, ''))) for r in rows)) for c in columns}
        lines.append('  '.join(c.ljust(widths[c]) for c in columns))
        lines += ['  '.join(str(r.get(c, '')).ljust(widths[c]) for c in columns) for r in rows]
    done = sum(1 for r in rows if r.get('compliant'))
    lines.append('')
    lines.append(f'{done}/{len(rows)} repositories follow the template')
    return '\n'.join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('repos', nargs='*', help='short names (basler) or full names; default: all of the organization')
    parser.add_argument('--markdown', action='store_true')
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()
    names = [r.split('/')[-1] if r.startswith(ORG) else (r if r.startswith('pymodaq_plugins_') else f'pymodaq_plugins_{r}')
             for r in args.repos] or list_repos()
    rows = []
    for name in names:
        try:
            rows.append(check(name))
        except urllib.error.HTTPError as error:
            rows.append({'repo': name, 'agents': f'error {error.code}', 'compliant': False})
    print(json.dumps(rows, indent=1) if args.json else render(rows, args.markdown))
    return 0 if all(r.get('compliant') for r in rows) else 1


if __name__ == '__main__':
    sys.exit(main())
