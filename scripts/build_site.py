from html import escape
from pathlib import Path
import re
import shutil


CONTENT_DIR = Path("content")
STATIC_DIR = Path("static")
OUTPUT_DIR = Path("public")


def page_title(markdown_text, fallback):
    for line in markdown_text.splitlines():
        if line.startswith("# "):
            title = line[2:].strip()
            if title:
                return title
    return fallback


def render_inline(text):
    rendered = escape(text)
    rendered = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        lambda match: f'<a href="{escape(match.group(2), quote=True)}">{match.group(1)}</a>',
        rendered,
    )
    rendered = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", rendered)
    rendered = re.sub(r"`([^`]+)`", r"<code>\1</code>", rendered)
    return rendered


def markdown_to_html(markdown_text):
    lines = markdown_text.splitlines()
    output = []
    paragraph = []
    in_list = False

    def flush_paragraph():
        if paragraph:
            output.append(f"<p>{render_inline(' '.join(paragraph))}</p>")
            paragraph.clear()

    def close_list():
        nonlocal in_list
        if in_list:
            output.append("</ul>")
            in_list = False

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            flush_paragraph()
            close_list()
            continue

        if line.startswith("### "):
            flush_paragraph(); close_list()
            output.append(f"<h3>{render_inline(line[4:])}</h3>")
        elif line.startswith("## "):
            flush_paragraph(); close_list()
            output.append(f"<h2>{render_inline(line[3:])}</h2>")
        elif line.startswith("# "):
            flush_paragraph(); close_list()
            output.append(f"<h1>{render_inline(line[2:])}</h1>")
        elif line.startswith("- "):
            flush_paragraph()
            if not in_list:
                output.append("<ul>")
                in_list = True
            output.append(f"<li>{render_inline(line[2:])}</li>")
        else:
            close_list()
            paragraph.append(line)

    flush_paragraph()
    close_list()
    return "\n".join(output)


def convert_local_markdown_links(html):
    return re.sub(
        r'href="([^"#:?]+)\.md([#?][^"]*)?"',
        r'href="\1.html\2"',
        html,
    )


def render_page(title, body):
    document_title = "Campus Status" if title == "Campus Status" else f"{title} - Campus Status"
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(document_title)}</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <header>
    <nav aria-label="Primary">
      <a href="index.html">Home</a>
      <a href="operations.html">Operations guide</a>
    </nav>
  </header>
  <main>
{body}
  </main>
  <footer>Campus Status</footer>
</body>
</html>
"""


def build_site(content_dir=CONTENT_DIR, static_dir=STATIC_DIR, output_dir=OUTPUT_DIR):
    content = Path(content_dir)
    static = Path(static_dir)
    output = Path(output_dir)

    if not content.is_dir():
        raise FileNotFoundError(f"Content directory does not exist: {content}")
    if not static.is_dir():
        raise FileNotFoundError(f"Static directory does not exist: {static}")

    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)

    pages = []
    for source in sorted(content.glob("*.md")):
        source_text = source.read_text(encoding="utf-8")
        title = page_title(source_text, source.stem.replace("-", " ").title())
        body = markdown_to_html(source_text)
        body = convert_local_markdown_links(body)
        target = output / f"{source.stem}.html"
        target.write_text(render_page(title, body), encoding="utf-8")
        pages.append(target)

    for source in sorted(static.iterdir()):
        if source.is_file():
            shutil.copy2(source, output / source.name)

    if not (output / "index.html").exists():
        raise ValueError("build did not produce index.html")

    return pages


def main():
    pages = build_site()
    print(f"Built {len(pages)} page(s) in {OUTPUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
