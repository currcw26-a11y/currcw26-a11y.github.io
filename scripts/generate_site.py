# Builds every HTML page for the site from locations.txt + the processed photos
# in photos/web. Re-run this any time you add a location or change locations.txt
# (after running process-photos.ps1 on any new photos).
import json
import os
import re
import time

BUILD_VERSION = int(time.time())

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCATIONS_TXT = os.path.join(ROOT, "locations.txt")
WEB_FULL = os.path.join(ROOT, "photos", "web", "full")
WEB_THUMB = os.path.join(ROOT, "photos", "web", "thumb")
LOCATIONS_OUT = os.path.join(ROOT, "locations")
SITE_NAME = "Aerials by Clive Curry"
MONTHS = ["January","February","March","April","May","June","July","August","September","October","November","December"]


def slugify(name):
    s = name.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def friendly_date(iso):
    if iso == "unknown":
        return "unknown"
    y, m, d = iso.split("-")
    return f"{MONTHS[int(m)-1]} {int(d)}, {y}"


def friendly_month_year(iso):
    y, m, d = iso.split("-")
    return f"{MONTHS[int(m)-1]} {y}"


def date_range_label(dmin, dmax):
    if dmin == dmax:
        return friendly_date(dmin)
    ymin, mmin, _ = dmin.split("-")
    ymax, mmax, _ = dmax.split("-")
    if ymin == ymax and mmin == mmax:
        return friendly_month_year(dmin)
    return f"{friendly_month_year(dmin)} – {friendly_month_year(dmax)}"


def parse_locations():
    rows = []
    with open(LOCATIONS_TXT, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = [p.strip() for p in line.split("|")]
            name, date_part = parts[0], parts[1]
            cover = parts[2] if len(parts) > 2 and parts[2] else None
            if " to " in date_part:
                dmin, dmax = date_part.split(" to ")
            else:
                dmin = dmax = date_part
            slug = slugify(name)
            photos = photos_for(slug)
            rows.append({
                "name": name, "dmin": dmin, "dmax": dmax, "slug": slug,
                "cover_pref": cover, "photos": photos, "count": len(photos),
            })
    # Portfolio order follows the order lines appear in locations.txt.
    return rows


def photos_for(slug):
    thumb_dir = os.path.join(WEB_THUMB, slug)
    if not os.path.isdir(thumb_dir):
        return []
    names = sorted(f for f in os.listdir(thumb_dir) if f.lower().endswith(".jpg"))
    return names


def cover_photo(loc):
    photos = loc["photos"]
    if not photos:
        return None
    if loc["cover_pref"]:
        wanted = os.path.splitext(loc["cover_pref"])[0].lower() + ".jpg"
        for p in photos:
            if p.lower() == wanted:
                return p
    return photos[0]


NAV = """<nav class="site-nav{extra}">
  <a class="brand" href="{root}index.html">{site_name}<span class="brand-tagline">Drone Photography</span></a>
  <button class="nav-toggle" aria-label="Menu">&#9776;</button>
  <div class="nav-links">
    <a href="{root}portfolio.html">Portfolio</a>
    <a href="{root}about.html">About</a>
  </div>
</nav>"""

FOOTER = """<footer class="site-footer">&copy; {year} Clive Curry. All photos are original work.</footer>"""

HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;600&family=Inter:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{root}css/style.css?v={build_version}">
</head>
<body>
"""

TAIL = """
<script src="{root}js/main.js?v={build_version}"></script>
</body>
</html>
"""


def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def build_index(locations):
    root = ""
    hero_img = f"{root}photos/web/full/colorado/DJI_0022.jpg"
    body = HEAD.format(
        title=f"{SITE_NAME} — Drone Photography Portfolio",
        description="Aerial drone photography portfolio by Clive Curry, featuring landscapes and coastlines from across the U.S. and abroad.",
        root=root,
        build_version=BUILD_VERSION,
    )
    body += NAV.format(extra="", root=root, site_name=SITE_NAME)
    body += f"""
<header class="hero" style="background-image:url('{hero_img}');">
  <div class="hero-content">
    <h1 class="hero-name">Clive Curry</h1>
    <p class="hero-sub">Drone Photography Portfolio</p>
  </div>
</header>
"""
    body += TAIL.format(root=root, build_version=BUILD_VERSION)
    write(os.path.join(ROOT, "index.html"), body)


def build_portfolio(locations):
    root = ""
    body = HEAD.format(
        title=f"Portfolio — {SITE_NAME}",
        description="Browse drone photography locations from Clive Curry's aerial photography portfolio.",
        root=root,
        build_version=BUILD_VERSION,
    )
    body += NAV.format(extra=" always-solid solid", root=root, site_name=SITE_NAME)
    body += """
<div class="container page-header">
  <h1>Portfolio</h1>
</div>
<div class="container">
  <div class="location-grid">
"""
    for loc in locations:
        cover = cover_photo(loc)
        cover_src = f"{root}photos/web/thumb/{loc['slug']}/{cover}" if cover else ""
        body += f"""    <a class="location-card" href="{root}locations/{loc['slug']}.html">
      <img src="{cover_src}" alt="Aerial drone photo of {loc['name']}" loading="lazy">
      <span class="location-card-label">{loc['name']}</span>
    </a>
"""
    body += "  </div>\n</div>\n"
    body += FOOTER.format(year=2026)
    body += TAIL.format(root=root, build_version=BUILD_VERSION)
    write(os.path.join(ROOT, "portfolio.html"), body)


def build_location_pages(locations):
    root = "../"
    for i, loc in enumerate(locations):
        photos = loc["photos"]
        next_loc = locations[(i + 1) % len(locations)]
        date_label = date_range_label(loc["dmin"], loc["dmax"])
        body = HEAD.format(
            title=f"{loc['name']} Drone Photos — {SITE_NAME}",
            description=f"Aerial drone photography from {loc['name']}, {date_label}.",
            root=root,
            build_version=BUILD_VERSION,
        )
        body += NAV.format(extra=" always-solid solid", root=root, site_name=SITE_NAME)
        body += f"""
<div class="container page-header">
  <h1>{loc['name']}</h1>
  <p class="page-meta">{loc['name']} &middot; {date_label}</p>
</div>
<div class="container">
  <div class="photo-grid">
"""
        for p in photos:
            thumb_src = f"{root}photos/web/thumb/{loc['slug']}/{p}"
            full_src = f"{root}photos/web/full/{loc['slug']}/{p}"
            alt = f"Aerial drone photo of {loc['name']}"
            body += f"""    <button type="button" data-lightbox-full="{full_src}" data-lightbox-alt="{alt}">
      <img src="{thumb_src}" alt="{alt}" loading="lazy">
    </button>
"""
        body += "  </div>\n"
        body += f"""  <div class="location-footer-nav">
    <a href="{root}portfolio.html">&larr; Back to Portfolio</a>
    <a href="{root}locations/{next_loc['slug']}.html">Next location: {next_loc['name']} &rarr;</a>
  </div>
</div>
"""
        body += FOOTER.format(year=2026)
        body += TAIL.format(root=root, build_version=BUILD_VERSION)
        write(os.path.join(LOCATIONS_OUT, f"{loc['slug']}.html"), body)


def build_about():
    root = ""
    about_txt_path = os.path.join(ROOT, "about.txt")
    with open(about_txt_path, encoding="utf-8") as f:
        raw = f.read().strip()
    paragraphs = [p.strip() for p in raw.split("\n\n") if p.strip()]

    # pull out an email if present, to turn into a mailto link + contact row
    email_match = re.search(r"[\w.+-]+@[\w-]+\.[\w-]+(?:\.[\w-]+)*", raw)
    email = email_match.group(0).rstrip(".") if email_match else None

    about_html_paras = "".join(f"    <p>{p}</p>\n" for p in paragraphs)

    about_photo_rel = "photos/web/full/about/about.jpg"
    about_photo_abs = os.path.join(ROOT, "photos", "web", "full", "about", "about.jpg")
    has_photo = os.path.exists(about_photo_abs)

    hero_img = f"{root}photos/web/full/florida/DJI_0038.jpg"

    body = HEAD.format(
        title=f"About — {SITE_NAME}",
        description="About Clive Curry, drone photographer and student at Wake Forest University.",
        root=root,
        build_version=BUILD_VERSION,
    )
    body += NAV.format(extra="", root=root, site_name=SITE_NAME)
    body += f"""
<div class="about-hero" style="background-image:url('{hero_img}');">
  <div class="about-wrap">
    <div class="about-text">
      <h1>About Me</h1>
{about_html_paras}
      <div class="contact-links">
"""
    if email:
        body += f'        <a href="mailto:{email}">{email}</a>\n'
    body += """      </div>
    </div>
"""
    if has_photo:
        body += f"""    <div class="about-photo">
      <img src="{root}{about_photo_rel}" alt="Clive Curry with his drone" loading="lazy">
    </div>
"""
    body += "  </div>\n</div>\n"
    body += TAIL.format(root=root, build_version=BUILD_VERSION)
    write(os.path.join(ROOT, "about.html"), body)
    return has_photo


def main():
    locations = parse_locations()
    build_index(locations)
    build_portfolio(locations)
    build_location_pages(locations)
    has_about_photo = build_about()
    print(f"Built: index.html, portfolio.html, about.html, and {len(locations)} location pages.")
    if not has_about_photo:
        print("NOTE: no about photo found yet at photos/web/full/about/about.jpg -- about.html was built without one.")


if __name__ == "__main__":
    main()
