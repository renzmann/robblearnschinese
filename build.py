"""Static site generator for robblearnschinese.com"""

import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

SRC = Path("src")
BUILD = Path("build")



@dataclass
class FrontMatter:
    vars: dict[str, str]
    body: str
    date: str


def parse_front_matter(path: Path) -> FrontMatter:
    """Split text into (vars_dict, body). Front matter is above the --- line."""
    vars_: dict[str, str] = {}
    lines: list[str] = path.read_text(encoding="utf-8").split("\n")
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
    return FrontMatter(vars=vars_, body=body, date=path.stem)


def slurp(path: Path) -> str:
    """Read file as text, ensuring it ends with exactly one newline."""
    text = path.read_text(encoding="utf-8")
    if not text.endswith("\n"):
        text += "\n"
    return text


def expand_includes(text: str, partials_dir: Path):
    """Expand {{> filename.html}} directives, reading from partials_dir."""
    def replace_include(m: re.Match) -> str:
        before, filename, after = m.group(1), m.group(2), m.group(3)
        content = slurp(partials_dir / filename)
        return before + content + after
    return re.sub(
        r"^(.*?)\{\{\s*>\s*(\S+)\s*\}\}(.*)$",
        replace_include,
        text,
        flags=re.MULTILINE,
    )


def substitute_vars(text: str, vars_: dict[str, str]):
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


def assemble_posts(dirname: str) -> str:
    """Read all post files from src/posts/<dirname>/, return assembled HTML."""
    posts_dir = SRC / "posts" / dirname
    if not posts_dir.is_dir():
        return ""

    post_files = sorted(posts_dir.glob("*.html"), reverse=True)
    parts = []
    for pf in post_files:
        front_matter = parse_front_matter(pf)
        html = POST_TEMPLATE.format(
            date=front_matter.date,
            hours=front_matter.vars.get("hours", ""),
            title=front_matter.vars.get("title", ""),
            body=front_matter.body,
        )
        parts.append(html)

    return "\n\n".join(parts)


def render_page(page_path):
    """Render a single page file to final HTML."""
    front_matter = parse_front_matter(page_path)
    vars_, body = front_matter.vars, front_matter.body

    if "posts" in vars_ and vars_["posts"]:
        posts_html = assemble_posts(vars_["posts"])
        body = front_matter.body.replace("{{posts}}", posts_html)

    vars_["content"] = body

    layout_name = vars_.get("layout", "")
    if not layout_name:
        print(f"error: missing required front matter key 'layout' in {page_path}", file=sys.stderr)
        sys.exit(1)

    layout = slurp(SRC / "layouts" / f"{layout_name}.html")
    layout = expand_includes(layout, SRC / "partials")
    out = substitute_vars(layout, vars_)
    # Second pass for when includes are a part of body content
    out = expand_includes(out, SRC / "partials")

    if not out.endswith("\n\n"):
        out = out.rstrip("\n") + "\n\n\n"

    return out


def main():
    if BUILD.exists():
        shutil.rmtree(BUILD)
    BUILD.mkdir()

    cname = Path("CNAME")
    if cname.exists():
        shutil.copy2(cname, BUILD / "CNAME")

    for page in sorted(SRC.glob("pages/*.html")):
        out = render_page(page)
        dest = BUILD / page.name
        dest.write_text(out, encoding="utf-8", newline="\n")

    static_src = SRC / "static"
    if static_src.is_dir():
        shutil.copytree(static_src, BUILD / "static")


if __name__ == "__main__":
    main()
