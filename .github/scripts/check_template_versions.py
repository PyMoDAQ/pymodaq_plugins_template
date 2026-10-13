"""Warn when the versions written in the template have drifted from PyMoDAQ's.

Run weekly by .github/workflows/check-versions.yml (only in the template repository, not in plugins).
Single source of truth: the ``pymodaq>=X.Y.Z`` floor of pyproject.toml. Everything else is compared to it and to what
PyPI says about the latest pymodaq. Standard library only. Exit code 1 if something needs a human.

When a new PyMoDAQ minor (say 5.4.0) is released
------------------------------------------------
1. Create the ``5.4.x`` branch from ``5.3.x`` and make it the default branch of the template repository.
2. On it, raise the floors in pyproject.toml (``pymodaq>=5.4.0``...), the "PyMoDAQ 5.3.x" wording in README.rst and
   AGENTS.md, requires-python and the matrix of reusable-compatibility.yml if they changed.
3. Point the three caller workflows (``@5.3.x`` in tests.yml, compatibility.yml, python-publish.yml) to ``@5.4.x``.
4. Run this script: it must print OK. Keep ``5.3.x`` for hotfixes.
"""
import json
import re
import sys
import tomllib
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PYPI = 'https://pypi.org/pypi/{}/json'


def pypi_info(name: str) -> dict:
    with urllib.request.urlopen(PYPI.format(name), timeout=30) as response:
        return json.load(response)


def minor(version: str) -> tuple:
    return tuple(int(p) for p in version.split('.')[:2])


def is_release(version: str) -> bool:
    return re.fullmatch(r'\d+\.\d+\.\d+', version) is not None


def python_minors(classifiers: list) -> list:
    found = [re.fullmatch(r'Programming Language :: Python :: 3\.(\d+)', c) for c in classifiers]
    return sorted(int(m.group(1)) for m in found if m)


def main() -> int:
    problems = []
    project = tomllib.loads((ROOT / 'pyproject.toml').read_text())['project']

    floors = {}
    for dep in project['dependencies']:
        match = re.match(r'(pymodaq(?:_utils|_gui|_data)?)>=(\d+\.\d+\.\d+)', dep)
        if match:
            floors[match.group(1)] = match.group(2)
    if 'pymodaq' not in floors:
        problems.append('pyproject.toml has no "pymodaq>=X.Y.Z" dependency: nothing to compare to')
        return report(problems)
    branch_minor = minor(floors['pymodaq'])
    branch = '{}.{}'.format(*branch_minor)

    # 1. the floors of the PyMoDAQ packages exist and belong to the branch's minor
    for name, floor in floors.items():
        releases = [v for v in pypi_info(name)['releases'] if is_release(v)]
        if floor not in releases:
            problems.append(f'{name}>={floor} was never released on PyPI')
        elif name == 'pymodaq' and minor(floor) != branch_minor:
            problems.append(f'{name} floor {floor} is not in {branch}')
        elif minor(floor) > branch_minor:
            problems.append(f'{name}>={floor} is newer than the branch ({branch}.x)')

    # 2. a new PyMoDAQ minor means a new template branch
    latest = pypi_info('pymodaq')
    versions = sorted((v for v in latest['releases'] if is_release(v)), key=lambda v: tuple(map(int, v.split('.'))))
    newest = versions[-1]
    if minor(newest) > branch_minor:
        problems.append(f'PyMoDAQ {newest} is out but this template targets {branch}.x: create the {"{}.{}".format(*minor(newest))}.x '
                        f'branch (checklist in the docstring of .github/scripts/check_template_versions.py)')

    # 3. supported Python versions: ours vs the latest pymodaq of the branch's minor
    same_minor = [v for v in versions if minor(v) == branch_minor][-1]
    with urllib.request.urlopen(f'https://pypi.org/pypi/pymodaq/{same_minor}/json', timeout=30) as response:
        data = json.load(response)['info']
    # the Python classifiers of a plugin are computed from requires-python when it is built (dynamic classifiers)
    ours = theirs = python_minors(data['classifiers'])
    requires = data.get('requires_python') or ''
    if requires and requires != project.get('requires-python'):
        problems.append(f'requires-python is {project.get("requires-python")!r}, pymodaq {same_minor} has {requires!r}')

    # 4. the compatibility matrix covers both Python extremes
    matrix = (ROOT / '.github/workflows/reusable-compatibility.yml').read_text()
    used = sorted({int(m) for m in re.findall(r"python-version: '3\.(\d+)'", matrix)})
    if ours and used and (used[0], used[-1]) != (ours[0], ours[-1]):
        problems.append(f'compatibility matrix spans Python 3.{used[0]}-3.{used[-1]}, supported is 3.{ours[0]}-3.{ours[-1]}')

    # 5. prose that names the branch
    for name in ('README.rst', 'AGENTS.md'):
        for number, line in enumerate((ROOT / name).read_text().splitlines(), 1):
            for found in re.findall(r'PyMoDAQ\s+(\d+\.\d+)\.x', line):
                if found != branch:
                    problems.append(f'{name}:{number} says PyMoDAQ {found}.x, the branch is {branch}.x')
    return report(problems, branch)


def report(problems: list, branch: str = '?') -> int:
    if not problems:
        print(f'OK: template versions are consistent with PyMoDAQ {branch}.x')
        return 0
    for problem in problems:
        print(f'::warning::{problem}')
    return 1


if __name__ == '__main__':
    sys.exit(main())
