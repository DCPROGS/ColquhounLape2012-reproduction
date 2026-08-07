"""Diff two check_retarget.py outputs and report the worst disagreement.

Usage:  python compare_retarget.py <out-a.txt> <out-b.txt> <label-a> <label-b>
"""
import re
import sys


def load(path):
    out = {}
    for line in open(path, encoding='utf-8', errors='replace'):
        m = re.match(r'^([A-Za-z][^ ].*?)\s{2,}(\S.*)$', line.rstrip())
        if m and not line.startswith(('scalcs from', 'cjumps API', 'mechanism')):
            out[m.group(1).strip()] = m.group(2).strip()
    return out


a, b = load(sys.argv[1]), load(sys.argv[2])
la, lb = sys.argv[3], sys.argv[4]

keys = [k for k in a if k in b]
only_a = [k for k in a if k not in b]
only_b = [k for k in b if k not in a]

print('%-30s %22s %22s  %s' % ('quantity', la, lb, 'agreement'))
print('-' * 88)
worst = 0.0
ndiff = 0
for k in keys:
    va, vb = a[k], b[k]
    try:
        fa, fb = float(va), float(vb)
        if fa == fb:
            note = 'identical'
        else:
            rel = abs(fa - fb) / max(abs(fa), abs(fb), 1e-300)
            worst = max(worst, rel)
            note = 'rel %.2e' % rel
            if rel > 1e-9:
                note += '  <-- DIFFERS'
                ndiff += 1
    except ValueError:
        note = 'identical' if va == vb else 'DIFFERS'
        if va != vb:
            ndiff += 1
    print('%-30s %22s %22s  %s' % (k, va, vb, note))

if only_a:
    print('\nonly in %s: %s' % (la, ', '.join(only_a)))
if only_b:
    print('only in %s: %s' % (lb, ', '.join(only_b)))

print('\nworst relative difference among numeric values: %.3e' % worst)
print('values differing by more than 1e-9 relative: %d' % ndiff)
