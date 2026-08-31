# -*- coding: utf-8 -*-
"""Read-only sanity checks over a DipTrace BoM.csv export.

Implements ../references/bom-sanity-checks.md. Exits non-zero when a hard error
is found; observations and questions never fail the run.

    python check_bom_csv.py "D:\\...\\BoM\\BoM.csv"
"""
import collections
import csv
import re
import sys

FOOTPRINT_PREFIX = re.compile(r'^(?:RC|CC|RL|RK|GRM|CL)(\d{4})')
RES_CODE = re.compile(r'^R[CL]\d{4}[FJ][RK]-07(\S+?)L\b')
VALUE = re.compile(r'([\d.]+)\s*(k|M)?\s*Ohm', re.I)
MULT = {None: 1.0, 'k': 1e3, 'M': 1e6}


def order_code(value):
    value = value.replace('NC!!!___', '').strip()
    m = re.match(r'([A-Za-z0-9\-/.]+)', value)
    return m.group(1).upper() if m else ''


def decode_res(code):
    m = re.match(r'^(\d+)([RKM])(\d*)$', code)
    if not m:
        return None
    whole, unit, frac = m.groups()
    return float('%s.%s' % (whole, frac or '0')) * {'R': 1, 'K': 1e3, 'M': 1e6}[unit]


def check(path):
    rows = list(csv.reader(open(path, encoding='utf-8-sig'), delimiter=';'))[1:]
    errors, notes = [], []
    refs = []

    for no, ref, name, value, qty in rows:
        value = value.replace('?', 'Ohm')
        parts = [x.strip() for x in ref.split(',') if x.strip()]
        refs += parts
        if len(parts) != int(qty):
            errors.append('line %s: Quantity %s but %d designators' % (no, qty, len(parts)))

        code = value.replace('NC!!!___', '')
        fp, nm = FOOTPRINT_PREFIX.match(code), re.search(r'(\d{4})', name)
        if fp and nm and fp.group(1) != nm.group(1):
            errors.append('line %s (%s): footprint %s but order code is %s'
                          % (no, ref, name, fp.group(1)))

        m = RES_CODE.match(code)
        if m:
            stated = VALUE.search(code)
            want = float(stated.group(1)) * MULT[stated.group(2)] if stated else None
            got = decode_res(m.group(1))
            if want is None or got is None or abs(got - want) > 1e-9 * max(1.0, got):
                errors.append('line %s (%s): code %s decodes to %s, value says %s'
                              % (no, ref, m.group(1), got, want))

    dupes = [r for r, n in collections.Counter(refs).items() if n > 1]
    if dupes:
        errors.append('designators on more than one line: %s' % ', '.join(sorted(dupes)))

    by_code = collections.defaultdict(list)
    for no, ref, name, value, qty in rows:
        by_code[order_code(value) or name.upper()].append((no, ref, value))
    for code, group in by_code.items():
        if len(group) > 1:
            fitted = [g for g in group if 'NC!!!' not in g[2]]
            if len(fitted) > 1:            # a fitted/DNP pair is legitimate
                errors.append('part number %s on lines %s'
                              % (code, ', '.join(g[0] for g in fitted)))

    seq = collections.defaultdict(set)
    for r in refs:
        m = re.match(r'([A-Za-z]+)(\d+)$', r)
        if m:
            seq[m.group(1)].add(int(m.group(2)))
    for prefix, used in sorted(seq.items()):
        missing = sorted(set(range(1, max(used) + 1)) - used)
        if missing:
            notes.append('%s numbering gaps: %s'
                         % (prefix, ', '.join(str(n) for n in missing)))

    out = sys.stdout
    out.write('%d lines, %d placements\n' % (len(rows), len(refs)))
    for e in errors:
        out.write('ERROR  %s\n' % e)
    for n in notes:
        out.write('note   %s\n' % n)
    if not errors:
        out.write('no errors\n')
    return 1 if errors else 0


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    sys.exit(check(sys.argv[1]))
