import copy
import csv
import importlib
import io
import json
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch

from records import select_rows
from render import render_csv
import report

failures = []

def check(name, operation):
    try:
        operation()
    except Exception as error:
        failures.append(name)
        print(f'FAIL {name}: {type(error).__name__}: {error}')
    else:
        print(f'PASS {name}')

def equal(actual, expected):
    assert actual == expected, f'actual={actual!r}, expected={expected!r}'

def invalid(rows, team='red'):
    try:
        select_rows(rows, team)
    except ValueError:
        return
    raise AssertionError('ValueError not raised')

boundary_rows = [
    {'team': 'red', 'label': 'A', 'count': 1, 'ignored': {'nested': []}},
    {'team': 'red', 'label': 'A ', 'count': 2},
    {'team': 'Red', 'label': None, 'count': True},
    {'team': 'red ', 'label': None, 'count': -1},
    {'team': ' red', 'label': None, 'count': 'secret'},
    {'team': 'red-ish', 'label': 'secret', 'count': 99},
    {'team': None, 'label': 'secret', 'count': 99},
    {'label': 'secret', 'count': 99},
    {'team': 'blue', 'label': 'secret', 'count': 99},
    {'team': 'red', 'label': 'A', 'count': 10**80},
]
before = copy.deepcopy(boundary_rows)
check('exact-team exclusion, malformed unselected rows, literal-label grouping and large integer', lambda: equal(select_rows(boundary_rows, 'red'), [{'label': 'A', 'count': 10**80 + 1}, {'label': 'A ', 'count': 2}]))
check('input remains byte-equivalent as JSON after aggregation', lambda: equal(json.dumps(boundary_rows), json.dumps(before)))
check('requested team whitespace remains literal', lambda: equal(select_rows([{'team':'red','label':'excluded','count':1},{'team':' red ','label':'literal','count':2}], ' red '), [{'label':'literal','count':2}]))
check('non-dictionary row rejected even following valid selected row', lambda: invalid([{'team':'red','label':'A','count':1}, None]))
for row in [{'team':'red','count':1}, {'team':'red','label':'A'}, {'team':'red','label':'\t\n','count':1}, {'team':'red','label':'A','count':False}]:
    check(f'selected-row validation {row!r}', lambda row=row: invalid([{'team':'red','label':'A','count':1}, row]))

expected = {
    'a': {'red':[{'label':'基础','count':6}], 'blue':[{'label':'private','count':3}], 'green':[]},
    'b': {'red':[{'label':'comma,value','count':1},{'label':'quote"value','count':0}], 'blue':[{'label':'private','count':8}], 'green':[]},
    'c': {'red':[{'label':'零','count':0}], 'blue':[{'label':'蓝色','count':10}], 'green':[{'label':'第一行\n第二行','count':1}]},
    'd': {'red':[{'label':'emoji 🌱','count':5},{'label':'keep spaces ','count':7}], 'blue':[], 'green':[{'label':'G','count':12}]},
}
for name, teams in expected.items():
    current = json.loads(Path(f'catalog/{name}.json').read_text(encoding='utf-8'))
    original = json.loads(subprocess.check_output(['git','show',f'HEAD:catalog/{name}.json']))
    def catalog_check(current=current, original=original):
        equal(len(current), len(original))
        for old, new in zip(original, current):
            equal(new['team'], old['teamName'])
            equal(new['count'], old['qty'])
            equal({k:v for k,v in new.items() if k not in ('team','count')}, {k:v for k,v in old.items() if k not in ('teamName','qty','team')})
            assert 'teamName' not in new and 'qty' not in new
    check(f'catalog/{name}.json independent value/key/nested/order mapping', catalog_check)
    for team, selected in teams.items():
        def cli_check(name=name, team=team, selected=selected):
            result = subprocess.run([sys.executable,'-B','report.py',f'catalog/{name}.json','--team',team], capture_output=True, text=True)
            equal(result.returncode, 0)
            equal(result.stderr, '')
            equal(list(csv.DictReader(io.StringIO(result.stdout, newline=''))), [{'label':r['label'],'count':str(r['count'])} for r in selected])
        check(f'actual subprocess CLI catalog/{name}.json team={team}', cli_check)

for name, payload in [
    ('late malformed selected count', '[{"team":"red","label":"valid","count":1},{"team":"red","label":"bad","count":true}]'),
    ('late non-dictionary row', '[{"team":"red","label":"valid","count":1}, null]'),
    ('non-list JSON input', '{"team":"red"}'),
    ('malformed JSON suffix', '[{"team":"red","label":"valid","count":1}] trailing'),
]:
    def failure_check(payload=payload):
        stdout, stderr = io.StringIO(), io.StringIO()
        with patch.object(Path, 'read_text', return_value=payload), patch.object(sys, 'stdout', stdout), patch.object(sys, 'stderr', stderr):
            try:
                report.main(['catalog/a.json', '--team', 'red'])
            except SystemExit as error:
                equal(error.code, 2)
            else:
                raise AssertionError('CLI did not fail')
        equal(stdout.getvalue(), '')
        assert stderr.getvalue().strip(), 'stderr empty'
    check(f'mocked file contents: {name}, exit2/stderr/no partial stdout', failure_check)

for error in [PermissionError('permission denied'), UnicodeDecodeError('utf-8', b'\xff', 0, 1, 'invalid start byte')]:
    def io_failure_check(error=error):
        stdout, stderr = io.StringIO(), io.StringIO()
        with patch.object(Path, 'read_text', side_effect=error), patch.object(sys, 'stdout', stdout), patch.object(sys, 'stderr', stderr):
            try:
                report.main(['catalog/a.json', '--team', 'red'])
            except SystemExit as caught:
                equal(caught.code, 2)
            else:
                raise AssertionError('CLI did not fail')
        equal(stdout.getvalue(), '')
        assert stderr.getvalue().strip(), 'stderr empty'
    check(f'{type(error).__name__}: exit2/stderr/no stdout', io_failure_check)

def import_check():
    stdout, stderr = io.StringIO(), io.StringIO()
    with patch.object(sys,'argv',['report.py','missing.json','--team','red']), patch.object(Path,'read_text', side_effect=AssertionError('import read catalog')), patch.object(sys,'stdout',stdout), patch.object(sys,'stderr',stderr):
        importlib.reload(report)
    equal((stdout.getvalue(),stderr.getvalue()), ('',''))
check('reload/import with CLI-like argv does not read input or emit output', import_check)

check('render mixed UTF-8, quotes, comma and embedded LF exact bytes', lambda: equal(render_csv([{'label':'中文,"x"\ny','count':0}]), 'label,count\n"中文,""x""\ny",0\n'))
check('render carriage-return newline is quoted and roundtrips as one field', lambda: equal(render_csv([{'label':'first\rsecond','count':1}]), 'label,count\n"first\rsecond",1\n'))
print(f'Independent review: {len(failures)} failure(s): {failures!r}')
raise SystemExit(bool(failures))
