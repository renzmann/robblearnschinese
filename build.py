"""Static site generator for robblearnschinese.com"""

import re
import shutil
import sys
from pathlib import Path

SRC = Path("src")
BUILD = Path("build")


def parse_front_matter(text):
    """Split text into (vars_dict, body). Front matter is above the --- line."""
    vars_ = {}
    lines = text.split("\n")
    body_start = 0
    for i, line in enumerate(lines):
        if line.strip() == "---":
            body_start = i + 1
            break
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if ":" in stripped:
            key, _, val = stripped.partition(":")
            vars_[key.strip()] = val.strip()
    body = "\n".join(lines[body_start:])
    return vars_, body


def slurp(path):
    """Read file, ensuring it ends with exactly one newline (matches awk slurp)."""
    text = path.read_text(encoding="utf-8")
    if not text.endswith("\n"):
        text += "\n"
    return text


def expand_includes(text, partials_dir):
    """Expand {{> filename.html}} directives, reading from partials_dir."""
    def replace_include(m):
        before, filename, after = m.group(1), m.group(2), m.group(3)
        content = slurp(partials_dir / filename)
        return before + content + after

    return re.sub(
        r"^(.*?)\{\{\s*>\s*(\S+)\s*\}\}(.*)$",
        replace_include,
        text,
        flags=re.MULTILINE,
    )


def substitute_vars(text, vars_):
    """Replace {{key}} with value from vars. Content first, then others."""
    # Content first (may contain other {{var}} patterns that shouldn't be touched
    # until layout expansion is done)
    if "content" in vars_:
        text = text.replace("{{content}}", vars_["content"])
        text = re.sub(r"\{\{\s*content\s*\}\}", vars_["content"], text)

    for key, val in vars_.items():
        if key == "content":
            continue
        text = re.sub(r"\{\{\s*" + re.escape(key) + r"\s*\}\}", val, text)

    return text


POST_TEMPLATE = """\
<h2 class="date-header" id="{date}">
  <span class="date">{date}</span>
  <span class="hours">{hours}</span>
  <a href="#{date}" class="header-anchor">¶</a>
</h2>
<h3>{title}</h3>
{body}"""


def assemble_posts(dirname):
    """Read all post files from src/posts/<dirname>/, return assembled HTML."""
    posts_dir = SRC / "posts" / dirname
    if not posts_dir.is_dir():
        return ""

    post_files = sorted(posts_dir.glob("*.html"), reverse=True)
    parts = []
    for pf in post_files:
        vars_, body = parse_front_matter(pf.read_text(encoding="utf-8"))
        html = POST_TEMPLATE.format(
            date=vars_.get("date", ""),
            hours=vars_.get("hours", ""),
            title=vars_.get("title", ""),
            body=body,
        )
        parts.append(html)

    return "\n\n".join(parts)


def render_page(page_path):
    """Render a single page file to final HTML."""
    vars_, body = parse_front_matter(page_path.read_text(encoding="utf-8"))

    # Assemble posts if this page has a posts directory
    if "posts" in vars_ and vars_["posts"]:
        posts_html = assemble_posts(vars_["posts"])
        body = body.replace("{{posts}}", posts_html)

    vars_["content"] = body

    layout_name = vars_.get("layout", "")
    if not layout_name:
        print(f"error: missing required front matter key 'layout' in {page_path}", file=sys.stderr)
        sys.exit(1)

    layout = slurp(SRC / "layouts" / f"{layout_name}.html")

    # First pass: expand includes in layout
    layout = expand_includes(layout, SRC / "partials")
    # Substitute variables
    out = substitute_vars(layout, vars_)
    # Second pass: expand includes that were inside content
    out = expand_includes(out, SRC / "partials")

    # The awk renderer's slurp adds a trailing \n to every file read,
    # which cascades through layout/partial expansion. Match that behavior.
    if not out.endswith("\n\n"):
        out = out.rstrip("\n") + "\n\n\n"

    return out


def main():
    # Clean and create build directory
    if BUILD.exists():
        shutil.rmtree(BUILD)
    BUILD.mkdir()

    # Copy CNAME
    cname = Path("CNAME")
    if cname.exists():
        shutil.copy2(cname, BUILD / "CNAME")

    # Render all pages
    for page in sorted(SRC.glob("pages/*.html")):
        out = render_page(page)
        dest = BUILD / page.name
        dest.write_text(out, encoding="utf-8", newline="\n")

    # Copy static assets
    static_src = SRC / "static"
    if static_src.is_dir():
        shutil.copytree(static_src, BUILD / "static")


if __name__ == "__main__":
    main()
