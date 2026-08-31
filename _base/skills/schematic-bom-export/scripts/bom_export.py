# -*- coding: utf-8 -*-
"""Turn a DipTrace BoM.csv export into a review Markdown note and a print PDF.

Both outputs carry the same rows, counts and exclusions, so the note and the
printed sheet can never disagree. See ../SKILL.md for the editorial rules.

    python bom_export.py --csv "D:\\...\\BoM\\BoM.csv" \
        --out-dir "G:\\...\\assembly" --title R120DRV.BM3BF3X1 --date 2026-08-31
"""
import argparse
import csv
import os
import re
import sys

# Footprint-only entities: they are placed on the board but nothing is bought or
# mounted for them. Matched against the DipTrace component Name, case-insensitive.
NON_PURCHASABLE = (
    r'^Solder_JMP',      # solder jumpers
    r'^Lead_',           # bare wire-lead pads
    r'^TP[_-]',          # test points
    r'^TestPoint',
    r'^Mounting',        # mounting holes
    r'^Hole',
    r'^Fiducial',
    r'^Logo',
)

# Style lifted from the reference sheet R120LD.BM2BF2X1 BOM.pdf.
PAGE_W = 841.8898          # A4 landscape
FRAME_W = 762.5197
MARGIN = 40.01575
FOOT_X = 34.01575
FOOT_Y = 19.84252


def is_excluded(name, patterns):
    return any(re.search(p, name, re.I) for p in patterns)


def load(path, patterns):
    rows = list(csv.reader(open(path, encoding='utf-8-sig'), delimiter=';'))[1:]
    kept, dropped = [], []
    for num, ref, name, val, qty in rows:
        # DipTrace cannot store Ω in a single-byte export; it writes '?' instead.
        val = val.replace('?', 'Ohm')
        item = dict(no=num, ref=ref.strip(), name=name.strip(), val=val.strip(),
                    q=int(qty), dnp='NC!!!' in val)
        (dropped if is_excluded(item['name'], patterns) else kept).append(item)
    for i, item in enumerate(kept, 1):        # renumber after exclusions
        item['no'] = str(i)
    return kept, dropped


def totals(items):
    fitted = sum(i['q'] for i in items if not i['dnp'])
    dnp = sum(i['q'] for i in items if i['dnp'])
    return fitted + dnp, fitted, dnp


def intro_text(items, batches):
    tot, fitted, dnp = totals(items)
    words = {1: 'One board', 2: 'Two boards', 3: 'Three boards', 5: 'Five boards'}
    parts = ['%d design BOM lines.' % len(items)]
    for n in batches:
        parts.append('%s: %d placements (%d fitted, %d DNP).'
                     % (words.get(n, '%d boards' % n), tot * n, fitted * n, dnp * n))
    parts.append('Mechanical placements (solder jumpers, lead pads, test points) '
                 'are excluded — nothing is purchased for them.')
    parts.append('Stock availability not filled in.')
    return ' '.join(parts)


def write_md(items, batches, title, date, csv_path, out_path):
    tot = totals(items)[0]
    head = ('---\ncssclasses:\n  - bom-print\nsource_file: \'%s\'\nboards: %d\n'
            'updated: %s\n---\n\n# %s BOM\n\n%s\n\n' %
            (csv_path, max(batches), date, title, intro_text(items, batches)))
    cols = ['No.', 'RefDes', 'Part / value'] + ['Qty X%d' % n for n in batches] + \
           ['Available', '']
    align = ['--:', '------', '------------'] + ['-----:'] * len(batches) + \
            ['---------', '---']
    head += '| ' + ' | '.join(cols) + ' |\n| ' + ' | '.join(align) + ' |\n'

    lines = []
    for it in items:
        cell = '<span class="bom-part">%s</span>' % it['name'].replace('|', '\\|')
        if it['val'] and it['val'] != it['name']:
            cell += '<br><span class="bom-value">%s</span>' % it['val'].replace('|', '\\|')
        cells = [it['no'], it['ref'], cell] + [str(it['q'] * n) for n in batches] + \
                ['DNP' if it['dnp'] else '', '']
        lines.append('| ' + ' | '.join(cells) + ' |')
    open(out_path, 'w', encoding='utf-8').write(head + '\n'.join(lines) + '\n')
    return tot


def write_pdf(items, batches, title, date, out_path):
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib import colors
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Table,
                                    TableStyle, Paragraph, Spacer)

    pdfmetrics.registerFont(TTFont('Arial', r'C:\Windows\Fonts\arial.ttf'))
    pdfmetrics.registerFont(TTFont('Arial-Bold', r'C:\Windows\Fonts\arialbd.ttf'))

    grey = colors.Color(.4, .4, .4)
    hdr_bg = colors.Color(.945098, .952941, .960784)
    dnp_bg = colors.Color(.85098, .85098, .85098)
    hdr_tx = colors.Color(.133333, .133333, .133333)
    grid = colors.Color(.819608, .835294, .85098)
    rule = colors.Color(.666667, .690196, .713725)

    st_cell = ParagraphStyle('cell', fontName='Arial', fontSize=8.2, leading=9.8)
    st_num = ParagraphStyle('num', parent=st_cell, alignment=2)
    st_hdr = ParagraphStyle('hdr', fontName='Arial-Bold', fontSize=8.6, leading=10,
                            textColor=hdr_tx)
    st_ttl = ParagraphStyle('ttl', fontName='Arial-Bold', fontSize=19, leading=23)
    st_int = ParagraphStyle('intro', fontName='Arial', fontSize=10, leading=13)

    def esc(s):
        return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

    head = ['No.', 'RefDes', 'Part / value'] + ['Qty X%d' % n for n in batches] + \
           ['Available']
    data = [[Paragraph(h, st_hdr) for h in head]]
    dnp_rows = []
    for r, it in enumerate(items, 1):
        cell = '<font color="#000000">%s</font>' % esc(it['name'])
        if it['val'] and it['val'] != it['name']:
            cell += '<br/><font color="#666666">%s</font>' % esc(it['val'])
        row = [Paragraph(it['no'], st_num), Paragraph(esc(it['ref']), st_cell),
               Paragraph(cell, st_cell)]
        row += [Paragraph(str(it['q'] * n), st_num) for n in batches]
        row.append(Paragraph('DNP' if it['dnp'] else '', st_cell))
        data.append(row)
        if it['dnp']:
            dnp_rows.append(r)

    qw, avw, now, refw = 42.0, 78.0, 30.0, 226.0
    widths = [now, refw, FRAME_W - now - refw - qw * len(batches) - avw] + \
             [qw] * len(batches) + [avw]
    table = Table(data, colWidths=widths, repeatRows=1)
    style = [('VALIGN', (0, 0), (-1, -1), 'TOP'),
             ('LEFTPADDING', (0, 0), (-1, -1), 4),
             ('RIGHTPADDING', (0, 0), (-1, -1), 4),
             ('TOPPADDING', (0, 0), (-1, -1), 3.3),
             ('BOTTOMPADDING', (0, 0), (-1, -1), 3.3),
             ('BACKGROUND', (0, 0), (-1, 0), hdr_bg),
             ('GRID', (0, 0), (-1, -1), 0.35, grid),
             ('LINEBELOW', (0, 0), (-1, 0), 0.8, rule)]
    style += [('BACKGROUND', (0, r), (-1, r), dnp_bg) for r in dnp_rows]
    table.setStyle(TableStyle(style))

    doc = BaseDocTemplate(out_path, pagesize=landscape(A4),
                          leftMargin=MARGIN, rightMargin=MARGIN,
                          topMargin=40, bottomMargin=45, title='%s BOM' % title)

    def deco(canv, _doc):
        canv.saveState()
        canv.setFillColor(grey)
        canv.setFont('Arial', 7.5)
        canv.drawString(FOOT_X, FOOT_Y, '%s BOM - updated %s' % (title, date))
        canv.drawRightString(PAGE_W - FOOT_X, FOOT_Y, 'Page %d' % canv.getPageNumber())
        canv.restoreState()

    frame = Frame(doc.leftMargin, doc.bottomMargin, FRAME_W,
                  landscape(A4)[1] - doc.topMargin - doc.bottomMargin, id='body',
                  leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    doc.addPageTemplates([PageTemplate(id='page', frames=[frame], onPage=deco)])
    doc.build([Paragraph('%s BOM' % title, st_ttl), Spacer(1, 10),
               Paragraph(intro_text(items, batches), st_int), Spacer(1, 12), table])


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--csv', required=True, help='DipTrace BoM.csv export')
    ap.add_argument('--out-dir', required=True, help='assembly/ directory')
    ap.add_argument('--title', required=True, help='board name, e.g. R120DRV.BM3BF3X1')
    ap.add_argument('--date', required=True, help='YYYY-MM-DD stamped in the outputs')
    ap.add_argument('--batches', default='1,5', help='board counts, e.g. 1,2,5')
    ap.add_argument('--keep-mechanical', action='store_true',
                    help='do not drop jumpers, lead pads and test points')
    ap.add_argument('--format', choices=('both', 'md', 'pdf'), default='both')
    a = ap.parse_args(argv)

    batches = [int(x) for x in a.batches.split(',') if x.strip()]
    patterns = () if a.keep_mechanical else NON_PURCHASABLE
    items, dropped = load(a.csv, patterns)
    if not items:
        sys.exit('no purchasable lines found in %s' % a.csv)

    base = os.path.join(a.out_dir, '%s BOM' % a.title)
    if a.format in ('both', 'md'):
        write_md(items, batches, a.title, a.date, a.csv, base + '.md')
    if a.format in ('both', 'pdf'):
        write_pdf(items, batches, a.title, a.date, base + '.pdf')

    tot, fitted, dnp = totals(items)
    out = sys.stdout
    out.write('%d lines, %d placements (%d fitted, %d DNP)\n' % (len(items), tot, fitted, dnp))
    if dropped:
        out.write('excluded as mechanical: %s\n'
                  % '; '.join('%s (%s)' % (d['ref'], d['name']) for d in dropped))
    return 0


if __name__ == '__main__':
    sys.exit(main())
