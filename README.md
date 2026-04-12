# Robb Learns Chinese

Source for [robblearnschinese.com](https://robblearnschinese.com) — a journal
of learning Mandarin (and Japanese) through comprehensible input.

## Building

```
python build.py
```

That's it.  Output lands in `build/`.  No dependencies beyond Python 3.

To clean up: `rm -rf build`

## Adding a post

Drop a new `.html` file in `src/posts/chinese/` (or `japanese/`) with front
matter at the top:

```html
date: 2026-5-10
hours: 100
title: Your post title here
---
<p>Write HTML here.</p>
```

Rebuild, and it shows up in reverse chronological order automatically.
