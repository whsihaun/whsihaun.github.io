#!/usr/bin/env python3
"""Render content.json into a static site in dist/ (stdlib only).

    python3 build.py            # build
    python3 build.py --serve    # build and preview at http://localhost:8000
"""
import datetime as dt
import html
import json
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(ROOT, "dist")
E = html.escape

ICONS = {
    "email": '<path d="M3 5h18v14H3z" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="m3 6 9 7 9-7" fill="none" stroke="currentColor" stroke-width="1.8"/>',
    "cv": '<path d="M6 2h9l5 5v15H6z" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M14 2v6h6M9 13h8M9 17h8" fill="none" stroke="currentColor" stroke-width="1.8"/>',
    "github": '<path fill="currentColor" d="M12 .5a11.5 11.5 0 0 0-3.64 22.41c.58.1.79-.25.79-.56v-2c-3.2.7-3.88-1.37-3.88-1.37-.52-1.33-1.28-1.69-1.28-1.69-1.05-.71.08-.7.08-.7 1.16.08 1.77 1.19 1.77 1.19 1.03 1.77 2.71 1.26 3.37.96.1-.75.4-1.26.73-1.55-2.56-.29-5.25-1.28-5.25-5.69 0-1.26.45-2.29 1.19-3.1-.12-.29-.52-1.46.11-3.05 0 0 .97-.31 3.17 1.18a11 11 0 0 1 5.78 0c2.2-1.49 3.17-1.18 3.17-1.18.63 1.59.23 2.76.11 3.05.74.81 1.19 1.84 1.19 3.1 0 4.42-2.7 5.39-5.27 5.68.41.36.78 1.06.78 2.14v3.17c0 .31.21.67.8.56A11.5 11.5 0 0 0 12 .5z"/>',
    "scholar": '<path fill="currentColor" d="M12 2 1 9l11 7 9-5.73V17h2V9zm-6 11.18v4.32L12 21l6-3.5v-4.32L12 17z"/>',
    "linkedin": '<path fill="currentColor" d="M4.98 3.5a2.5 2.5 0 1 1 0 5 2.5 2.5 0 0 1 0-5zM3 9.5h4V21H3zm7 0h3.8v1.6h.06c.53-1 1.83-2.05 3.77-2.05 4.03 0 4.77 2.65 4.77 6.1V21h-4v-5.1c0-1.22-.02-2.79-1.7-2.79-1.7 0-1.96 1.33-1.96 2.7V21h-4z"/>',
    "twitter": '<path fill="currentColor" d="M18.9 2H22l-7.4 8.46L23.3 22h-6.8l-5.3-6.95L5.1 22H2l7.9-9.05L1.6 2h7l4.8 6.35zm-1.2 18h1.7L7.4 3.9H5.6z"/>',
}
LABELS = {"email": "Email", "cv": "CV", "github": "GitHub", "scholar": "Scholar", "linkedin": "LinkedIn", "twitter": "X"}


def icon(name):
    return f'<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true">{ICONS[name]}</svg>'


def is_todo(s):
    return isinstance(s, str) and s.strip().upper().startswith("TODO")


def text(s):
    """Escape; mark TODO placeholders so they are visibly unfinished."""
    if is_todo(s):
        return f'<span class="todo">{E(s)}</span>'
    return E(s)


def link_buttons(links):
    out = [f'<a class="btn" href="{E(u)}">{E(k)}</a>' for k, u in (links or {}).items() if u]
    return f'<div class="btns">{"".join(out)}</div>' if out else ""


def section(sid, title, body):
    if not body:
        return ""
    return f'<section id="{sid}"><h2>{E(title)}</h2>{body}</section>'


def render(c):
    s, p = c["site"], c["profile"]
    contacts = []
    if p.get("email"):
        contacts.append(("email", f"mailto:{p['email']}"))
    if p.get("cv"):
        contacts.append(("cv", p["cv"]))
    for k, u in p.get("links", {}).items():
        if u and k in ICONS:
            contacts.append((k, u))
    contact_html = "".join(
        f'<a class="contact" href="{E(u)}" rel="me noopener">{icon(k)}<span>{LABELS[k]}</span></a>' for k, u in contacts)

    initials = "".join(w[0] for w in p["name"].split()[:2]).upper()
    photo = (f'<img class="photo" src="{E(p["photo"])}" alt="{E(p["name"])}">' if p.get("photo")
             else f'<div class="photo placeholder" aria-hidden="true">{E(initials)}</div>')
    native = f' <span class="native">{E(p["name_native"])}</span>' if p.get("name_native") else ""

    about = "".join(f"<p>{text(x)}</p>" for x in c.get("about", []))
    if c.get("interests"):
        about += '<ul class="chips">' + "".join(f"<li>{E(x)}</li>" for x in c["interests"]) + "</ul>"

    news = "".join(f'<li><time>{E(n["date"])}</time><span>{text(n["text"])}</span></li>' for n in c.get("news", []))
    news = f'<ul class="dated">{news}</ul>' if news else ""

    me = p["name"]
    pubs = ""
    for pub in c.get("publications", []):
        authors = E(pub.get("authors", "")).replace(E(me), f"<strong>{E(me)}</strong>")
        note = f' <span class="note">{E(pub["note"])}</span>' if pub.get("note") else ""
        pubs += (f'<li class="pub"><div class="pub-title">{text(pub["title"])}</div>'
                 f'<div class="pub-authors">{authors}</div>'
                 f'<div class="pub-venue">{E(pub.get("venue", ""))}{note}</div>{link_buttons(pub.get("links"))}</li>')
    pubs = f'<ol class="pubs">{pubs}</ol>' if pubs else ""

    projects = ""
    for pr in c.get("projects", []):
        img = (f'<img src="{E(pr["image"])}" alt="" loading="lazy">' if pr.get("image")
               else '<div class="thumb-placeholder" aria-hidden="true"></div>')
        tags = "".join(f"<li>{E(t)}</li>" for t in pr.get("tags", []))
        projects += (f'<article class="card">{img}<div class="card-body">'
                     f'<h3>{text(pr["title"])}</h3><div class="meta">{E(pr.get("period", ""))}</div>'
                     f'<p>{text(pr.get("summary", ""))}</p><ul class="tags">{tags}</ul>'
                     f'{link_buttons(pr.get("links"))}</div></article>')
    projects = f'<div class="cards">{projects}</div>' if projects else ""

    def timeline(rows):
        if not rows:
            return ""
        li = "".join(
            f'<li><time>{E(r["period"])}</time><div><div class="tl-title">{text(r["title"])}</div>'
            f'<div class="meta">{text(r.get("place", ""))}</div>'
            + (f'<div class="tl-detail">{E(r["detail"])}</div>' if r.get("detail") else "") + "</div></li>"
            for r in rows)
        return f'<ul class="timeline">{li}</ul>'

    awards = "".join(f'<li><time>{E(a["date"])}</time><span>{text(a["text"])}</span></li>' for a in c.get("awards", []))
    awards = f'<ul class="dated">{awards}</ul>' if awards else ""

    sections = [
        ("about", "About", about), ("news", "News", news), ("publications", "Publications", pubs),
        ("projects", "Projects", projects), ("education", "Education", timeline(c.get("education"))),
        ("experience", "Experience", timeline(c.get("experience"))), ("awards", "Awards", awards),
    ]
    nav = "".join(f'<a href="#{sid}">{E(t)}</a>' for sid, t, b in sections if b)
    body = "".join(section(*x) for x in sections)
    updated = s.get("updated") or dt.date.today().strftime("%B %Y")

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(s["title"])}</title>
<meta name="description" content="{E(s["description"])}">
<meta property="og:title" content="{E(s["title"])}">
<meta property="og:description" content="{E(s["description"])}">
<meta property="og:type" content="website">
<meta property="og:url" content="{E(s["url"])}">
<link rel="canonical" href="{E(s["url"])}">
<link rel="stylesheet" href="assets/style.css">
<script>document.documentElement.dataset.theme = localStorage.getItem("theme") || (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");</script>
</head>
<body>
<nav class="topnav"><div class="wrap"><a class="brand" href="#">{E(p["name"])}</a><div class="links">{nav}</div>
<button id="theme" class="theme" aria-label="Toggle dark mode">◐</button></div></nav>
<main class="wrap">
<header class="hero">{photo}<div>
<h1>{E(p["name"])}{native}</h1>
<div class="role">{E(p["role"])}</div>
<div class="affil">{E(p["affiliation"])}{(" · " + E(p["location"])) if p.get("location") else ""}</div>
<div class="contacts">{contact_html}</div>
</div></header>
{body}
</main>
<footer class="wrap">© {dt.date.today().year} {E(p["name"])} · Last updated {E(updated)}</footer>
<script src="assets/main.js"></script>
</body>
</html>
"""


def build():
    with open(os.path.join(ROOT, "content.json"), encoding="utf-8") as f:
        content = json.load(f)
    shutil.rmtree(DIST, ignore_errors=True)
    shutil.copytree(os.path.join(ROOT, "assets"), os.path.join(DIST, "assets"))
    for extra in ("files", "images"):
        if os.path.isdir(os.path.join(ROOT, extra)):
            shutil.copytree(os.path.join(ROOT, extra), os.path.join(DIST, extra))
    with open(os.path.join(DIST, "index.html"), "w", encoding="utf-8") as f:
        f.write(render(content))
    open(os.path.join(DIST, ".nojekyll"), "w").close()
    print(f"built {DIST}/index.html")


if __name__ == "__main__":
    build()
    if "--serve" in sys.argv:
        import functools
        import http.server
        handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=DIST)
        print("preview: http://localhost:8000")
        http.server.ThreadingHTTPServer(("127.0.0.1", 8000), handler).serve_forever()
