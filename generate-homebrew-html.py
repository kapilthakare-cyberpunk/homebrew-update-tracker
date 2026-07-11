#!/usr/bin/env python3
"""Generate the Homebrew Updates Tracker HTML from JSON data."""
import json
import sys
from datetime import datetime


def html_escape(text: str) -> str:
    return (str(text).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def generate_html(data_file: str, output_file: str) -> None:
    with open(data_file, encoding="utf-8") as f:
        entries = json.load(f)
    entries.sort(key=lambda e: e.get("date", ""), reverse=True)
    for i, entry in enumerate(entries, 1):
        entry["sn"] = i
    dates = sorted({e.get("date", "") for e in entries}, reverse=True)
    rows_html = ""
    for entry in entries:
        values = {key: html_escape(entry.get(key, "")) for key in ("date", "name", "desc", "use_case")}
        rows_html += f''' <tr data-date="{values["date"]}">
  <td class="col-sn">{entry["sn"]}</td>
  <td class="col-date">{values["date"]}</td>
  <td class="col-name">{values["name"]}</td>
  <td class="col-desc">{values["desc"]}</td>
  <td class="col-use">{values["use_case"]}</td>
 </tr>\n'''
    date_options = "".join(f' <option value="{html_escape(d)}">{html_escape(d)}</option>\n' for d in dates)
    content = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Homebrew Updates Tracker</title>
<style>
:root {{ color-scheme: light dark; --bg:#f9f9fb; --card:#fff; --text:#1d1d1f; --muted:#6e6e73; --accent:#0071e3; --border:#d2d2d7; }}
@media (prefers-color-scheme:dark) {{ :root {{ --bg:#000; --card:#1d1d1f; --text:#f5f5f7; --muted:#86868b; --accent:#2997ff; --border:#424245; }} }}
body {{ font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; background:var(--bg); color:var(--text); margin:0; padding:40px 20px; }}
.container {{ max-width:1200px; margin:auto; }}
h1 {{ margin:0 0 8px; }} .subtitle,.status {{ color:var(--muted); }}
.controls {{ display:flex; gap:12px; margin:24px 0 20px; flex-wrap:wrap; }}
input,select {{ font:inherit; padding:10px 14px; border:1px solid var(--border); border-radius:8px; background:var(--card); color:var(--text); }}
input {{ flex:1; min-width:220px; }} .table-container {{ overflow:auto; background:var(--card); border:1px solid var(--border); border-radius:12px; }}
table {{ width:100%; border-collapse:collapse; text-align:left; }} th,td {{ padding:16px 20px; border-bottom:1px solid var(--border); vertical-align:top; }} th {{ color:var(--muted); font-size:13px; text-transform:uppercase; }} tr.hidden {{ display:none; }} .col-sn {{ width:50px;color:var(--muted); }} .col-date {{ white-space:nowrap;color:var(--muted); }} .col-name {{ font-weight:600;color:var(--accent); }}
.empty-state {{ padding:60px 20px; text-align:center; color:var(--muted); }}
</style>
</head>
<body><main class="container">
<h1>Homebrew New Software Updates</h1>
<p class="subtitle">A daily history of new tools and apps discovered through <code>brew update</code>.</p>
<p class="status">Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} local time; {len(entries)} entries tracked.</p>
<div class="controls"><input id="searchInput" type="search" placeholder="Search software, descriptions, or use cases"><select id="dateFilter"><option value="all">All dates</option>{date_options}</select></div>
<div class="table-container">{("<table><thead><tr><th>No.</th><th>Date</th><th>Software</th><th>Description</th><th>Typical use case</th></tr></thead><tbody id=\"tableBody\">" + rows_html + "</tbody></table>") if entries else '<div class="empty-state"><p>No updates recorded yet.</p><p>The first Homebrew update will populate this table.</p></div>'}</div>
</main><script>
const search=document.getElementById('searchInput'), date=document.getElementById('dateFilter');
function filter() {{ const q=search.value.toLowerCase(), d=date.value; document.querySelectorAll('#tableBody tr').forEach(row => row.classList.toggle('hidden', !row.textContent.toLowerCase().includes(q) || (d !== 'all' && row.dataset.date !== d))); }}
search.addEventListener('input', filter); date.addEventListener('change', filter);
</script></body></html>'''
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"HTML written: {output_file} ({len(entries)} entries)")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <data.json> <output.html>", file=sys.stderr)
        sys.exit(1)
    generate_html(sys.argv[1], sys.argv[2])
