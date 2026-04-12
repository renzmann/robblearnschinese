# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build

```bash
python build.py   # build site into build/
rm -rf build      # clean
```

Output goes to `build/`. Deployed to GitHub Pages on push to `main` via `.github/workflows/static.yml`. Zero external dependencies — stdlib Python only.

## Architecture

`build.py` is the entire build system. It:

1. Reads pages from `src/pages/*.html` — each has YAML-style front matter above a `---` delimiter
2. Loads the layout from `src/layouts/<layout>.html`
3. Expands `{{> filename.html}}` partial includes from `src/partials/`
4. Substitutes `{{variable}}` placeholders with front matter values
5. For pages with `posts: <dirname>` in front matter, assembles individual post files from `src/posts/<dirname>/` into a `{{posts}}` placeholder — posts are sorted reverse-chronologically by filename and wrapped in date-header boilerplate
6. Copies `src/static/` and `CNAME` into `build/`

### Page format

```html
layout: default
title: Page Title
description: Meta description
bodyclass:
posts: chinese
---

{{posts}}
```

### Post format

Individual post files live in `src/posts/<language>/YYYY-MM-DD.html`:

```html
date: 2026-4-9
hours: 71
title: Post title
---
<p>HTML body here.</p>
```

The date-header boilerplate (`<h2>`, date/hours spans, anchor link) is generated automatically from front matter. Partials like `{{> distant_time_table.html }}` work inside post bodies.
