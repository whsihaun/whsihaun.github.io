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


def section(sid, number, title, body):
    if not body:
        return ""
    return (f'<section id="{sid}" class="content-section" aria-labelledby="{sid}-title">'
            f'<div class="section-heading"><p class="eyebrow">{number} / {E(title)}</p>'
            f'<h2 id="{sid}-title">{E(title)}<span class="punctuation">.</span></h2></div>'
            f'{body}</section>')


def render(c, page_id="home"):
    s, p = c["site"], c["profile"]
    me = p["name"]
    name_parts = me.split(" ", 1)
    name_html = f'<span>{E(name_parts[0])}</span>'
    if len(name_parts) > 1:
        name_html += f'<span class="name-last">{E(name_parts[1])}<span class="punctuation" aria-hidden="true">.</span></span>'
    initials = "".join(w[0] for w in me.split()[:2]).upper()
    photo = (f'<img src="{E(p["photo"])}" alt="Portrait of {E(me)}" width="512" height="682" fetchpriority="high">'
             if p.get("photo") else f'<div class="photo-placeholder">{E(initials)}</div>')
    about = "".join(f'<p>{text(x)}</p>' for x in c.get("about", []))
    interests = "".join(f'<li>{E(x)}</li>' for x in c.get("interests", []))
    interests_html = f'<ul class="interests" aria-label="Research interests">{interests}</ul>' if interests else ""
    research_link = '<a class="button button-primary" href="publications.html">View research <span aria-hidden="true">↗</span></a>' if c.get("publications") else ""
    email_link = (f'<a class="hero-email" href="mailto:{E(p["email"])}">{icon("email")}<span>{E(p["email"])}</span></a>'
                  if p.get("email") else "")
    previews = ""
    for index, pub in enumerate(c.get("publications", [])[:2], 1):
        previews += (f'<a class="home-work-item" href="publications.html#paper-{index}">'
                     f'<div class="home-work-topline"><span>{index:02d}</span><span aria-hidden="true">↗</span></div>'
                     f'<h3>{text(pub.get("short_title", pub["title"]))}</h3>'
                     f'<p class="home-work-title">{text(pub["title"])}</p>'
                     f'<p class="home-work-status">{E(pub.get("venue", ""))}</p></a>')
    home_work = f'<aside class="home-work" aria-label="Research in progress"><p class="eyebrow">Research in progress</p>{previews}</aside>' if previews else ""
    facts = []
    for label, value in (("Affiliation", p.get("affiliation")), ("Status", p.get("role")), ("Location", p.get("location"))):
        if value:
            facts.append(f'<div><dt>{label}</dt><dd>{E(value)}</dd></div>')
    if p.get("email"):
        facts.append(f'<div><dt>Email</dt><dd><a href="mailto:{E(p["email"])}">{E(p["email"])}</a></dd></div>')
    github_url = p.get("links", {}).get("github")
    if github_url:
        github_name = github_url.rstrip("/").split("/")[-1]
        facts.append(f'<div><dt>GitHub</dt><dd><a href="{E(github_url)}" rel="me noopener">{E(github_name)} <span aria-hidden="true">↗</span></a></dd></div>')
    facts_html = f'<dl class="profile-facts">{"".join(facts)}</dl>'
    location = f'<span>{E(p["location"])}</span>' if p.get("location") else ""
    hero = f'''<section id="home" class="hero" aria-labelledby="hero-name">
<div class="hero-topline"><p class="eyebrow">01 / Home</p><p class="location">{location}</p></div>
<div class="hero-grid home-grid"><div class="hero-copy">
<h1 id="hero-name" aria-label="{E(me)}">{name_html}</h1>
<p class="hero-role">{E(p["role"])}</p>
<p class="hero-affiliation">{E(p["affiliation"])}</p>
<div class="about-copy">{about}</div>
<div class="hero-actions">{research_link}</div>
{email_link}
</div>{home_work}</div>
<div class="hero-bottom">{interests_html}<a class="scroll-link" href="about.html">About me <span aria-hidden="true">↗</span></a></div>
</section>'''
    profile_panel = f'''<div class="profile-panel"><div class="portrait-composition">
<div class="portrait-orbit orbit-one" aria-hidden="true"></div><div class="portrait-orbit orbit-two" aria-hidden="true"></div>
<div class="portrait-cross" aria-hidden="true">✦</div><div class="portrait-photo">{photo}</div>
</div>{facts_html}</div>'''

    pubs = ""
    for index, pub in enumerate(c.get("publications", []), 1):
        authors = E(pub.get("authors", "")).replace(E(me), f'<strong>{E(me)}</strong>')
        note = f'<span class="pub-note">{E(pub["note"])}</span>' if pub.get("note") else ""
        pubs += (f'<li id="paper-{index}" class="publication"><span class="publication-number" aria-hidden="true">{index:02d}</span>'
                 f'<div class="publication-content"><h3>{text(pub["title"])}</h3>'
                 f'<p class="pub-authors">{authors}</p>'
                 f'<p class="pub-status"><span class="status-dot" aria-hidden="true"></span>{E(pub.get("venue", ""))}{note}</p>'
                 f'{link_buttons(pub.get("links"))}</div></li>')
    publications = section("publications", "03", "Publications", f'<ol class="publications-list">{pubs}</ol>' if pubs else "")

    education_rows = ""
    for row in c.get("education", []):
        period = f'<p class="education-period">{E(row["period"])}</p>' if row.get("period") else ""
        detail = f'<p class="education-detail">{E(row["detail"])}</p>' if row.get("detail") else ""
        education_rows += (f'<li><span class="education-symbol" aria-hidden="true">↗</span><div>'
                           f'<h3>{text(row.get("place", ""))}</h3><p class="education-degree">{text(row["title"])}</p>{period}{detail}</div></li>')
    education = section("education", "04", "Education", f'<ul class="education-list">{education_rows}</ul>' if education_rows else "")

    academic = "".join(f'<div class="resume-entry"><h3>{text(row.get("place", ""))}</h3><p>{text(row["title"])}</p></div>'
                       for row in c.get("education", []))
    experience = "".join(f'<div class="resume-entry"><h3>{text(row["title"])}</h3><p>{text(row["description"])}</p></div>'
                         for row in c.get("research_experience", []))
    work = "".join(f'<div class="work-summary"><h3>{text(pub["title"])}</h3><p>{E(pub.get("venue", ""))}</p></div>'
                   for pub in c.get("publications", []))
    details = ""
    for title, entries in (("Education", academic), ("Research experience", experience), ("Manuscripts", work)):
        if entries:
            details += f'<div class="resume-group"><p class="eyebrow">{title}</p>{entries}</div>'
    about_page = section("about", "02", "About", f'<div class="about-layout">{profile_panel}<div class="resume-column">{details}</div></div>')

    contacts = []
    if p.get("email"):
        contacts.append(f'<a class="contact-email" href="mailto:{E(p["email"])}">{E(p["email"])}<span aria-hidden="true">↗</span></a>')
    social_links = ""
    for key, url in p.get("links", {}).items():
        if url and key in ICONS:
            social_links += f'<a class="social-link" href="{E(url)}" rel="me noopener">{icon(key)}{E(LABELS[key])}<span aria-hidden="true">↗</span></a>'
    if p.get("cv"):
        social_links += f'<a class="social-link" href="{E(p["cv"])}">{icon("cv")}CV<span aria-hidden="true">↗</span></a>'
    note = f'<p class="contact-note">{text(p["contact_note"])}</p>' if p.get("contact_note") else ""
    contact_body = f'<div class="contact-content">{note}{"".join(contacts)}<div class="social-links">{social_links}</div></div>' if contacts or social_links or note else ""
    contact = section("contact", "05", "Contact", contact_body)

    sections = [("home", "Home", hero), ("about", "About", about_page), ("publications", "Publications", publications),
                ("education", "Education", education), ("contact", "Contact", contact)]
    filenames = {sid: "index.html" if sid == "home" else f"{sid}.html" for sid, _, _ in sections}
    nav_items = []
    for sid, title, section_body in sections:
        if section_body:
            active = ' class="active" aria-current="page"' if sid == page_id else ""
            nav_items.append(f'<a href="{filenames[sid]}"{active}><span>{E(title)}</span><span class="nav-arrow" aria-hidden="true">↗</span></a>')
    nav = "".join(nav_items)
    title, body = next((title, body) for sid, title, body in sections if sid == page_id)
    page_title = s["title"] if page_id == "home" else f'{title} | {s["title"]}'
    page_url = s["url"].rstrip("/") + ("/" if page_id == "home" else "/" + filenames[page_id])
    updated = s.get("updated") or dt.date.today().strftime("%B %Y")
    github = p.get("links", {}).get("github", "")
    sidebar_github = f'<a class="sidebar-social" href="{E(github)}" aria-label="GitHub">{icon("github")}</a>' if github else ""
    sidebar_email = f'<a class="sidebar-social" href="mailto:{E(p["email"])}" aria-label="Email">{icon("email")}</a>' if p.get("email") else ""
    return f'''<!doctype html>
<html lang="en" data-theme="dark">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="dark light">
<title>{E(page_title)}</title>
<meta name="description" content="{E(s["description"])}">
<meta property="og:title" content="{E(page_title)}">
<meta property="og:description" content="{E(s["description"])}">
<meta property="og:type" content="website">
<meta property="og:url" content="{E(page_url)}">
<link rel="canonical" href="{E(page_url)}">
<link rel="stylesheet" href="assets/style.css">
<script>try {{ document.documentElement.dataset.theme = localStorage.getItem("theme") || "dark"; }} catch (_) {{}}</script>
</head>
<body id="top" class="page-{page_id}">
<a class="skip-link" href="#main">Skip to content</a>
<aside class="sidebar" aria-label="Site navigation">
<a class="brand" href="index.html">{E(s["title"])}<span aria-hidden="true">.</span></a>
<nav class="navigation" aria-label="Main navigation">{nav}</nav>
<div class="sidebar-bottom"><div class="sidebar-socials">{sidebar_email}{sidebar_github}</div>
<button id="theme" class="theme-toggle" aria-label="Switch to light theme"><span class="theme-icon" aria-hidden="true">◐</span><span class="theme-label">Light mode</span></button>
<p class="sidebar-credit">© {dt.date.today().year} {E(me)}<br>Seoul, Korea</p></div>
</aside>
<main id="main" class="main-content">{body}
<footer><span>© {dt.date.today().year} {E(me)}</span><span>Last updated {E(updated)}</span><a href="#top">Back to top ↑</a></footer>
</main>
<script src="assets/main.js"></script>
</body>
</html>
'''


def build():
    with open(os.path.join(ROOT, "content.json"), encoding="utf-8") as f:
        content = json.load(f)
    shutil.rmtree(DIST, ignore_errors=True)
    shutil.copytree(os.path.join(ROOT, "assets"), os.path.join(DIST, "assets"))
    for extra in ("files", "images"):
        if os.path.isdir(os.path.join(ROOT, extra)):
            shutil.copytree(os.path.join(ROOT, extra), os.path.join(DIST, extra))
    for page_id in ("home", "about", "publications", "education", "contact"):
        filename = "index.html" if page_id == "home" else f"{page_id}.html"
        with open(os.path.join(DIST, filename), "w", encoding="utf-8") as f:
            f.write(render(content, page_id))
    open(os.path.join(DIST, ".nojekyll"), "w").close()
    print(f"built 5 pages in {DIST}")


if __name__ == "__main__":
    build()
    if "--serve" in sys.argv:
        import functools
        import http.server
        handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=DIST)
        print("preview: http://localhost:8000")
        http.server.ThreadingHTTPServer(("127.0.0.1", 8000), handler).serve_forever()
