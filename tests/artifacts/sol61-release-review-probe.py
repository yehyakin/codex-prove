#!/usr/bin/env python3
"""Preserved Astra read-only probe; pass the isolated fixture directory as argv[1]."""

from copy import deepcopy
import sys

sys.path.insert(0, sys.argv[1])
import ranges
import tags


class IntSubclass(int):
    pass


checks = 0


def rejects(fn, value):
    global checks
    before = deepcopy(value)
    try:
        fn(value)
    except ValueError:
        pass
    else:
        raise AssertionError((fn.__name__, value, 'accepted invalid input'))
    assert value == before, (fn.__name__, 'mutated rejected input')
    checks += 1


for value in (None, (), {}, set(), 4, True, b'abc', 'abc', [b'a'], [[]], [{}], [1], [None], [False], ['ok', 3]):
    rejects(tags.normalize, value)
for value in (None, (), {}, set(), 4, True, '12', [[1, 2]], [None], ['12'], [(1,)], [(1, 2, 3)], [(2, 1)], [(True, 2)], [(1, False)], [(IntSubclass(1), 2)], [(1, IntSubclass(2))], [(1.0, 2)], [(1, 2.0)], [('1', 2)], [(1, '2')], [(1, 2), [3, 4]]):
    rejects(ranges.merge, value)
values = [' \u00c9 ', 'E\u0301', '\u00e9', 'e\u0301', '\uff21', 'A', '\u2003', ' Stra\u00dfe ', 'STRASSE', '\u0130', 'i\u0307']
before = values[:]
expected = ['\u00e9', 'e\u0301', '\uff41', 'a', 'strasse', 'i\u0307']
actual = tags.normalize(values)
assert actual == expected, (actual, expected)
assert values == before
checks += 1
print('Unicode output:', ascii(actual))
values = [(7, 9), (1, 4), (4, 6), (9, 10), (-3, -1), (-1, 0), (20, 20)]
before = values[:]
actual = ranges.merge(values)
assert actual == [(-3, 0), (1, 6), (7, 10), (20, 20)], actual
assert values == before
checks += 1
print('Range output:', actual)
print(f'PASS: {checks} supplemental cases; invalid types/shapes raise ValueError; inputs unchanged; no NFC/NFKC collapse')
