# whsihaun.github.io

Personal academic homepage. Static, no dependencies.

- **Edit content:** `content.json` (empty values hide items; `TODO` text is highlighted until replaced)
- **Images / PDFs:** put them in `images/` or `files/` and reference them as `images/me.jpg`, `files/cv.pdf`
- **Preview:** `python3 build.py --serve` → http://localhost:8000
- **Deploy:** push to `main` — GitHub Actions builds `dist/` and publishes to GitHub Pages
