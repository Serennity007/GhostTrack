"""Human-readable exports, safe for spreadsheets and offline browsers."""
import csv
import html
import json
from pathlib import Path

from version import VERSION


def spreadsheet_cell(value):
    value = str(value)
    return "'" + value if value.lstrip().startswith(('=', '+', '-', '@')) else value


def write_report(path, data, headings=('Field', 'Value')):
    path = Path(path)
    if path.suffix.lower() == '.csv':
        with path.open('w', encoding='utf-8-sig', newline='') as stream:
            writer = csv.writer(stream)
            writer.writerow(headings)
            writer.writerows((spreadsheet_cell(k), spreadsheet_cell(v)) for k, v in data.items())
    elif path.suffix.lower() == '.html':
        rows = ''.join('<tr><th>' + html.escape(str(k)) + '</th><td>' + html.escape(str(v)) + '</td></tr>'
                       for k, v in data.items())
        document = '''<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>GhostTrack report</title><style>
body{background:#0b1020;color:#edf3ff;font:16px system-ui,sans-serif;margin:40px auto;padding:0 24px;max-width:1000px}
h1{color:#5ee0bc}small{color:#a6b5d2}table{border-collapse:collapse;width:100%;margin:32px 0}
th,td{text-align:left;vertical-align:top;border-bottom:1px solid #28354e;padding:16px;overflow-wrap:anywhere}
th{width:24%;color:#a6b5d2}tr:nth-child(odd){background:#11192d}
@media print{body{background:white;color:black}h1,th{color:black}}
</style></head><body><h1>GHOST / TRACK</h1><small>Desktop report · VERSION</small><table>ROWS</table></body></html>'''
        path.write_text(document.replace('VERSION', VERSION).replace('ROWS', rows), encoding='utf-8')
    else:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
