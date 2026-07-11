#!/usr/bin/env python3
"""Generate the Homebrew Updates Tracker HTML from JSON data."""
import json
import sys
from datetime import datetime


def html_escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def generate_html(data_file: str, output_file: str) -> None:
    with open(data_file) as f:
        entries = json.load(f)

    # Sort by date descending, newest first
    entries.sort(key=lambda e: e.get("date", ""), reverse=True)

    # Number rows sequentially
    for i, entry in enumerate(entries, 1):
        entry["sn"] = i

    # Collect unique dates for the filter dropdown (sorted desc)
    dates = sorted({e["date"] for e in entries}, reverse=True)

    rows_html = ""
    for entry in entries:
        sn = entry["sn"]
        date = html_escape(entry.get("date", ""))
        name = html_escape(entry.get("name", ""))
        desc = html_escape(entry.get("desc", ""))
        use_case = html_escape(entry.get("use_case", ""))

        rows_html += f""" <!-- Row {sn} -->
 <tr data-date="{date}">
 <td class="col-sn">{sn}</td>
 <td class="col-date">{date}</td>
 <td class="col-name">{name}</td>
 <td class="col-desc">{desc}</td>
 <td class="col-use">
 <ul>
 <li>{use_case}</li>
 </ul>
 </td>
 </tr>
"""

    date_options = ""
    for d in dates:
        date_options += f' <option value="{d}">{d}</option>\n'

    if not date_options:
        date_options = ' <option value="none">No data yet</option>\n'

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
 <meta charset="UTF-8">
 <meta name="viewport" content="width=device-width, initial-scale=1.0">
 <title>Homebrew Updates Tracker</title>
 <style>
 :root {{
 --bg-color: #f9f9fb;
 --card-bg: #ffffff;
 --text-main: #1d1d1f;
 --text-muted: #6e6e73;
 --accent: #0071e3;
 --border: #d2d2d7;
 --input-bg: #f5f5f7;
 }}

 @media (prefers-color-scheme: dark) {{
 :root {{
 --bg-color: #000000;
 --card-bg: #1d1d1f;
 --text-main: #f5f5f7;
 --text-muted: #86868b;
 --accent: #2997ff;
 --border: #424245;
 --input-bg: #2d2d2f;
 }}
 }}

 body {{
 font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
 background-color: var(--bg-color);
 color: var(--text-main);
 margin: 0;
 padding: 40px 20px;
 display: flex;
 justify-content: center;
 }}

 .container {{
 width: 100%;
 max-width: 1200px;
 }}

 header {{
 margin-bottom: 24px;
 }}

 h1 {{
 font-size: 28px;
 font-weight: 700;
 margin: 0 0 8px 0;
 letter-spacing: -0.5px;
 }}

 .subtitle {{
 color: var(--text-muted);
 font-size: 16px;
 margin: 0;
 }}

 .status {{
 margin-top: 8px;
 font-size: 13px;
 color: var(--text-muted);
 }}

 /* Search and Filter Controls */
 .controls {{
 display: flex;
 gap: 12px;
 margin-bottom: 20px;
 flex-wrap: wrap;
 }}

 .search-input, .filter-select {{
 font-family: inherit;
 font-size: 14px;
 border: 1px solid var(--border);
 border-radius: 8px;
 padding: 10px 16px;
 background-color: var(--card-bg);
 color: var(--text-main);
 outline: none;
 transition: border-color 0.2s;
 }}

 .search-input {{
 flex: 1;
 min-width: 200px;
 }}

 .filter-select {{
 min-width: 160px;
 cursor: pointer;
 }}

 .search-input:focus, .filter-select:focus {{
 border-color: var(--accent);
 }}

 /* Table Design */
 .table-container {{
 background-color: var(--card-bg);
 border: 1px solid var(--border);
 border-radius: 12px;
 overflow: hidden;
 box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02);
 }}

 table {{
 width: 100%;
 border-collapse: collapse;
 text-align: left;
 font-size: 15px;
 }}

 th {{
 background-color: var(--card-bg);
 color: var(--text-muted);
 font-weight: 600;
 font-size: 13px;
 text-transform: uppercase;
 letter-spacing: 0.5px;
 padding: 16px 20px;
 border-bottom: 1px solid var(--border);
 }}

 td {{
 padding: 20px;
 border-bottom: 1px solid var(--border);
 vertical-align: top;
 line-height: 1.5;
 }}

 tr:last-child td {{
 border-bottom: none;
 }}

 tr.hidden {{
 display: none;
 }}

 /* Column Sizing */
 .col-sn {{ width: 50px; color: var(--text-muted); }}
 .col-date {{ width: 110px; color: var(--text-muted); white-space: nowrap; }}
 .col-name {{ width: 160px; font-weight: 600; color: var(--accent); }}
 .col-desc {{ width: 38%; }}
 .col-use {{ width: 38%; }}

 ul {{
 margin: 0;
 padding-left: 18px;
 }}

 li {{
 margin-bottom: 4px;
 }}

 li:last-child {{
 margin-bottom: 0;
 }}

 .empty-state {{
 padding: 60px 20px;
 text-align: center;
 color: var(--text-muted);
 }}
 .empty-state p {{
 font-size: 15px;
 margin: 8px 0;
 }}
 .empty-state .icon {{
 font-size: 40px;
 margin-bottom: 12px;
 }}
 </style>
</head>
<body>

<div class="container">
 <header>
 <h1>Homebrew New Software Updates</h1>
 <p class="subtitle">Daily log of new tools discovered via <code>brew update</code></p>
 <p class="status">Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} IST &bull; {len(entries)} entries tracked</p>
 </header>

 <!-- Interactive Filter Panel -->
 <div class="controls">
 <input type="text" id="searchInput" class="search-input" placeholder="Search software name, description, or use cases...">

 <select id="dateFilter" class="filter-select">
 <option value="all">All Dates</option>
{date_options} </select>
 </div>

 <!-- Data Table -->
 <div class="table-container">
{"" if entries else ' <div class="empty-state"><div class="icon">📦</div><p>No updates recorded yet.</p><p>The first <code>brew update</code> run will populate this table.</p></div>'}
{" <table>" if entries else ""}
{" <thead><tr><th class=\"col-sn\">S.No</th><th class=\"col-date\">Date</th><th class=\"col-name\">Software</th><th class=\"col-desc\">Description</th><th class=\"col-use\">Typical Use Cases</th></tr></thead>" if entries else ""}
{" <tbody id=\"tableBody\">" if entries else ""}
{rows_html if entries else ""}
{" </tbody></table>" if entries else ""}
 </div>
</div>

<script>
 const searchInput = document.getElementById('searchInput');
 const dateFilter = document.getElementById('dateFilter');
 const tableRows = document.querySelectorAll('#tableBody tr');

 function filterTable() {{
 const searchText = searchInput.value.toLowerCase();
 const selectedDate = dateFilter.value;

 tableRows.forEach(row => {{
 const rowText = row.textContent.toLowerCase();
 const rowDate = row.getAttribute('data-date');

 const matchesSearch = rowText.includes(searchText);
 const matchesDate = (selectedDate === 'all' || rowDate === selectedDate);

 if (matchesSearch && matchesDate) {{
 row.classList.remove('hidden');
 }} else {{
 row.classList.add('hidden');
 }}
 }});
 }}

 if (searchInput) searchInput.addEventListener('input', filterTable);
 if (dateFilter) dateFilter.addEventListener('change', filterTable);
</script>

</body>
</html>"""

    with open(output_file, "w") as f:
        f.write(html)

    print(f"HTML written: {output_file} ({len(entries)} entries)")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <data.json> <output.html>", file=sys.stderr)
        sys.exit(1)
    generate_html(sys.argv[1], sys.argv[2])
