"""PDF builder module: renders branded HTML template to PDF via Playwright.

Transforms the same sections dict used by docx_builder into an HTML document
via Jinja2 template, then renders to PDF using Playwright's headless Chromium.

Uses sync_playwright (not async) since the pipeline is synchronous.
Logo paths are converted to file:/// URIs for Chromium to load (Pitfall 1).
print_background=True is mandatory for color rendering (Pitfall 2).
"""

import os
import re
import sys
from pathlib import Path
from datetime import date

from jinja2 import Environment, FileSystemLoader

# Relative import for skill scripts
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from scripts.docx_builder import format_date, get_section_label, COVER_BOILERPLATE


# Section order and labels (must match docx_builder.SECTION_ORDER)
SECTION_ORDER = ['overview', 'sources', 'dataflows', 'mquery', 'datamodel', 'maintenance']


def slugify(text: str) -> str:
    """Convert section name to URL-safe ID for HTML anchors (D-05)."""
    slug = text.lower().strip()
    slug = slug.replace(' ', '-')
    slug = re.sub(r'[^a-z0-9-]', '', slug)
    slug = re.sub(r'-+', '-', slug)
    return slug.strip('-')


def _to_file_uri(path: str) -> str:
    """Convert local file path to file:/// URI for HTML img src (Pitfall 1)."""
    return Path(path).resolve().as_uri()


def _prose_to_html(prose_text: str, accent_color: str) -> str:
    """Convert generated prose (with TABLE:/CODE_BLOCK: markers) to HTML.

    Mirrors the parsing logic in docx_builder._parse_and_add_prose()
    but outputs HTML elements instead of python-docx objects.

    Handles:
    - TABLE: ... END_TABLE markers -> <table> with <th>/<td>
    - CODE_BLOCK: ... END_CODE_BLOCK markers -> <pre><code>
    - Triple-backtick fenced code blocks -> <pre><code>
    - Pipe-delimited tables (without TABLE: marker) -> <table>
    - ## and ### sub-headings -> <h2>/<h3>
    - Regular text -> <p>
    """
    import html as html_module
    lines = prose_text.split('\n')
    output = []
    i = 0

    while i < len(lines):
        line = lines[i]

        if not line.strip():
            i += 1
            continue

        # TABLE: marker
        if line.strip().startswith('TABLE:'):
            table_lines = []
            i += 1
            while i < len(lines):
                tl = lines[i]
                if tl.strip().startswith('END_TABLE') or (not tl.strip() and table_lines):
                    if not tl.strip() and i + 1 < len(lines) and '|' in lines[i + 1]:
                        i += 1
                        continue
                    i += 1
                    break
                if '|' in tl:
                    table_lines.append(tl)
                i += 1
            output.append(_table_lines_to_html(table_lines))
            continue

        # Pipe-delimited table without marker
        if '|' in line and re.match(r'^\s*\|', line):
            table_lines = []
            while i < len(lines) and '|' in lines[i] and lines[i].strip():
                table_lines.append(lines[i])
                i += 1
            if len(table_lines) >= 2:
                output.append(_table_lines_to_html(table_lines))
            else:
                for tl in table_lines:
                    output.append(f'<p>{html_module.escape(tl.strip())}</p>')
            continue

        # CODE_BLOCK: marker
        if line.strip().startswith('CODE_BLOCK:'):
            code_lines = []
            i += 1
            while i < len(lines):
                cl = lines[i]
                if cl.strip().startswith('END_CODE_BLOCK') or not cl.strip():
                    i += 1
                    break
                code_lines.append(html_module.escape(cl))
                i += 1
            output.append(f'<pre><code>{chr(10).join(code_lines)}</code></pre>')
            continue

        # Triple-backtick fenced code
        if line.strip().startswith('```'):
            code_lines = []
            i += 1
            while i < len(lines):
                cl = lines[i]
                if cl.strip().startswith('```'):
                    i += 1
                    break
                code_lines.append(html_module.escape(cl))
                i += 1
            output.append(f'<pre><code>{chr(10).join(code_lines)}</code></pre>')
            continue

        # Sub-headings
        heading_match = re.match(r'^(#{2,3})\s+(.+)$', line.strip())
        if heading_match:
            level = len(heading_match.group(1))
            text = html_module.escape(heading_match.group(2).strip())
            output.append(f'<h{level}>{text}</h{level}>')
            i += 1
            continue

        # Regular paragraph
        output.append(f'<p>{html_module.escape(line.strip())}</p>')
        i += 1

    return '\n'.join(output)


def _table_lines_to_html(table_lines: list[str]) -> str:
    """Convert pipe-delimited table lines to an HTML table."""
    import html as html_module
    if not table_lines:
        return ''

    rows = []
    for line in table_lines:
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        rows.append(cells)

    # Skip separator rows (all dashes/colons)
    data_rows = [r for r in rows if not all(re.match(r'^[-:]+$', c) for c in r)]

    if not data_rows:
        return ''

    html_parts = ['<table>']
    # First row is header
    html_parts.append('<thead><tr>')
    for cell in data_rows[0]:
        html_parts.append(f'<th>{html_module.escape(cell)}</th>')
    html_parts.append('</tr></thead>')

    # Remaining rows are body
    if len(data_rows) > 1:
        html_parts.append('<tbody>')
        for row in data_rows[1:]:
            html_parts.append('<tr>')
            for cell in row:
                html_parts.append(f'<td>{html_module.escape(cell)}</td>')
            html_parts.append('</tr>')
        html_parts.append('</tbody>')

    html_parts.append('</table>')
    return '\n'.join(html_parts)


def _render_html(sections: dict, config: dict) -> str:
    """Render the Jinja2 HTML template with section content.

    Returns the full HTML string ready for Playwright.
    """
    # Resolve template directory
    skill_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template_dir = os.path.join(skill_root, 'templates')

    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=False  # HTML content is pre-escaped in _prose_to_html
    )
    template = env.get_template('document.html.j2')

    accent_color = config.get('accent_color', '#4A90D9')

    # Language-aware section labels and date (D-05, Pitfall 3)
    language = config.get('language', 'EN')

    # Build sections list in display order with HTML content
    sections_list = []
    for section_id in SECTION_ORDER:
        if section_id not in sections:
            continue
        section_data = sections[section_id]
        # Override label with language-appropriate heading (D-05, Pitfall 3)
        label = get_section_label(section_id, language)
        prose = section_data.get('prose', '')
        html_content = _prose_to_html(prose, accent_color) if prose else ''
        sections_list.append({
            'id': slugify(label),
            'label': label,
            'html_content': html_content,
        })

    # Convert logo paths to file:/// URIs (Pitfall 1)
    client_logo = ''
    if config.get('client_logo') and os.path.isfile(config['client_logo']):
        client_logo = _to_file_uri(config['client_logo'])

    company_logo = ''
    if config.get('company_logo') and os.path.isfile(config['company_logo']):
        company_logo = _to_file_uri(config['company_logo'])

    boilerplate = COVER_BOILERPLATE.get(language, COVER_BOILERPLATE['EN'])

    return template.render(
        primary_color=config.get('primary_color', '#1B365D'),
        accent_color=accent_color,
        client_name=config.get('client_name', ''),
        report_name=config.get('report_name', ''),
        version=config.get('version', '1.0'),
        date=format_date(date.today(), language),
        lang='fr' if language == 'FR' else 'en',
        toc_heading=boilerplate['toc_heading'],
        client_logo=client_logo,
        company_logo=company_logo,
        sections=sections_list,
    )


def build_pdf(sections: dict, config: dict, docx_path: str) -> str:
    """Build PDF from sections using Jinja2 template + Playwright (D-12).

    Args:
        sections: Same dict passed to build_docx(). Keys are section IDs,
                  values have 'label' and 'prose' keys.
        config: JSON config dict with branding and metadata fields.
        docx_path: Absolute path to .docx file (used to derive .pdf filename per D-13).

    Returns:
        Absolute path to saved .pdf file.

    Raises:
        Any exception from Playwright or Jinja2 -- caller (generate.py)
        catches and handles gracefully per D-10/D-11.
    """
    from playwright.sync_api import sync_playwright

    # 1. Render HTML
    print("  Rendering HTML template...", file=sys.stderr)
    html_content = _render_html(sections, config)

    # 2. Derive PDF path from DOCX path (D-13: same stem, .pdf extension)
    pdf_path = docx_path.rsplit('.docx', 1)[0] + '.pdf'

    # 3. Generate PDF via Playwright (sync API per anti-pattern guidance)
    print("  Launching Playwright Chromium...", file=sys.stderr)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(html_content, wait_until="networkidle")
        page.pdf(
            path=pdf_path,
            format="Letter",
            print_background=True,  # MANDATORY for color rendering (Pitfall 2)
            margin={
                "top": "20mm",
                "bottom": "20mm",
                "left": "15mm",
                "right": "15mm",
            },
        )
        browser.close()

    return os.path.abspath(pdf_path)
