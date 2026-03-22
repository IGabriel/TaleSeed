#!/usr/bin/env python3
"""Render README_CN.md into a self-contained HTML file.

This is a small, dependency-free Markdown subset renderer tailored for this repo.
It supports:
- Headings (#..######)
- Paragraphs
- Unordered lists (- )
- Fenced code blocks (```)
- Horizontal rules (---)
- Inline: **bold**, `code`, [text](url)
- GitHub-style pipe tables (basic)

Usage:
    python tools/render_readme_cn_html.py README_CN.md README_CN.html
"""

from __future__ import annotations

import html
import re
import sys
from pathlib import Path


def _inline(md: str) -> str:
    md = html.escape(md)

    # inline code
    md = re.sub(r"`([^`]+)`", lambda m: f"<code>{m.group(1)}</code>", md)
    # bold
    md = re.sub(r"\*\*([^*]+)\*\*", lambda m: f"<strong>{m.group(1)}</strong>", md)
    # links
    md = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        lambda m: f"<a href=\"{html.escape(m.group(2), quote=True)}\">{m.group(1)}</a>",
        md,
    )

    return md


def _is_table_line(line: str) -> bool:
    s = line.strip()
    return "|" in s and not s.startswith("```")


def _is_table_sep(line: str) -> bool:
    s = line.strip()
    if "|" not in s:
        return False
    # accept: | --- | --- | or ---|---
    parts = [p.strip() for p in s.strip("|").split("|")]
    if not parts:
        return False
    return all(re.fullmatch(r":?-{3,}:?", p) for p in parts)


def _parse_table(lines: list[str], start: int) -> tuple[str, int]:
    header = lines[start].rstrip("\n")
    if start + 1 >= len(lines) or not _is_table_sep(lines[start + 1]):
        return "", start

    def split_row(row: str) -> list[str]:
        return [c.strip() for c in row.strip().strip("|").split("|")]

    headers = split_row(header)
    i = start + 2
    rows: list[list[str]] = []
    while i < len(lines) and _is_table_line(lines[i]) and lines[i].strip() and not lines[i].lstrip().startswith("#"):
        # stop table if an obvious non-table line appears
        row = split_row(lines[i].rstrip("\n"))
        if len(row) != len(headers):
            break
        rows.append(row)
        i += 1

    th = "".join(f"<th>{_inline(h)}</th>" for h in headers)
    body = "".join(
        "<tr>" + "".join(f"<td>{_inline(c)}</td>" for c in r) + "</tr>" for r in rows
    )

    table_html = (
        "<div class=\"table-wrap\"><table>"
        f"<thead><tr>{th}</tr></thead>"
        f"<tbody>{body}</tbody>"
        "</table></div>"
    )
    return table_html, i


def render_markdown(md_text: str) -> str:
    lines = md_text.splitlines(True)

    out: list[str] = []
    in_code = False
    list_open = False
    i = 0

    def close_list() -> None:
        nonlocal list_open
        if list_open:
            out.append("</ul>")
            list_open = False

    while i < len(lines):
        line = lines[i].rstrip("\n")

        # code fences
        if line.strip().startswith("```"):
            if not in_code:
                close_list()
                in_code = True
                out.append("<pre><code>")
            else:
                in_code = False
                out.append("</code></pre>")
            i += 1
            continue

        if in_code:
            out.append(html.escape(line) + "\n")
            i += 1
            continue

        # tables
        if _is_table_line(line) and i + 1 < len(lines) and _is_table_sep(lines[i + 1]):
            close_list()
            table_html, new_i = _parse_table(lines, i)
            if table_html:
                out.append(table_html)
                i = new_i
                continue

        # headings
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            close_list()
            level = len(m.group(1))
            content = _inline(m.group(2).strip())
            out.append(f"<h{level}>{content}</h{level}>")
            i += 1
            continue

        # horizontal rule
        if line.strip() == "---":
            close_list()
            out.append("<hr/>")
            i += 1
            continue

        # unordered list
        if line.lstrip().startswith("- "):
            if not list_open:
                out.append("<ul>")
                list_open = True
            item = line.lstrip()[2:].strip()
            out.append(f"<li>{_inline(item)}</li>")
            i += 1
            continue
        else:
            close_list()

        # blank lines
        if not line.strip():
            out.append("")
            i += 1
            continue

        # paragraph
        out.append(f"<p>{_inline(line.strip())}</p>")
        i += 1

    close_list()

    # collapse consecutive empties
    cleaned: list[str] = []
    for part in out:
        if part == "" and (not cleaned or cleaned[-1] == ""):
            continue
        cleaned.append(part)

    return "\n".join(cleaned)


def main(argv: list[str] | None = None) -> int:
    argv = argv or sys.argv[1:]
    if len(argv) != 2:
        print("Usage: python tools/render_readme_cn_html.py README_CN.md README_CN.html", file=sys.stderr)
        return 2

    src = Path(argv[0])
    dst = Path(argv[1])

    md_text = src.read_text(encoding="utf-8")
    body = render_markdown(md_text)

    html_doc = f"""<!doctype html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\"/>
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"/>
  <title>TaleSeed README (中文)</title>
  <style>
    :root {{ color-scheme: light dark; }}
    body {{ max-width: 920px; margin: 32px auto; padding: 0 16px; font-family: system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, "Noto Sans", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif; line-height: 1.6; }}
    pre {{ padding: 12px 14px; overflow: auto; border-radius: 8px; background: rgba(127,127,127,0.12); }}
    code {{ font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; font-size: 0.95em; }}
    hr {{ border: 0; border-top: 1px solid rgba(127,127,127,0.35); margin: 24px 0; }}
    h1, h2, h3, h4 {{ line-height: 1.25; margin-top: 1.2em; }}
    .table-wrap {{ overflow: auto; }}
    table {{ border-collapse: collapse; width: 100%; margin: 12px 0; }}
    th, td {{ border: 1px solid rgba(127,127,127,0.35); padding: 8px 10px; text-align: left; vertical-align: top; }}
    th {{ background: rgba(127,127,127,0.12); }}
    a {{ color: inherit; }}
  </style>
</head>
<body>
{body}
</body>
</html>
"""

    dst.write_text(html_doc, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
