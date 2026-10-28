"""Build a static, Hostinger-ready copy of the Kenny's site.

Netlify-only parts are replaced:
  /press pages (server-rendered)  -> static HTML snapshots
  /api/articles                   -> /api/articles.json
  Netlify Forms (contact)         -> contact.php (PHP mail)
  /vogin dashboard                -> left out (needs the Netlify backend)
"""
import json, os, re, shutil, subprocess, sys, urllib.parse

SRC = "/home/claude/site/kp/public"
OUT = sys.argv[1]
LIVE = "https://kennys-international.netlify.app"
DOMAIN = "https://kennysinternational.com"
CATS = ["Events", "Store openings", "Brands", "News"]
PER_PAGE = 13

def get(path, binary=False):
    r = subprocess.run(["curl", "-sS", "-f", "-m", "60", "--retry", "3", LIVE + path], capture_output=True)
    if r.returncode:
        raise SystemExit(f"fetch failed {path}: {r.stderr.decode()}")
    return r.stdout if binary else r.stdout.decode("utf-8")

def cat_slug(c):
    return re.sub(r"[^a-z0-9]+", "-", c.lower()).strip("-")

def press_url(category="", page=1):
    u = "/press"
    if category:
        u += "/category/" + cat_slug(category)
    if page > 1:
        u += f"/page/{page}"
    return u

def fix(html):
    # Netlify-injected script
    html = re.sub(r'<script[^>]*src="/\.netlify/[^"]*"[^>]*></script>', "", html)
    html = html.replace(LIVE, DOMAIN).replace(urllib.parse.quote(LIVE, safe=""), urllib.parse.quote(DOMAIN, safe=""))
    # list links with query strings -> static paths
    def q2(m):
        qs = urllib.parse.parse_qs(m.group(3).replace("&amp;", "&"))
        cat = qs.get("category", [""])[0]
        page = int(qs.get("page", ["1"])[0] or 1)
        return f'{m.group(1)}="{m.group(2) or ""}{press_url(cat, page)}"'
    html = re.sub(r'(href|content)="(https://kennysinternational\.com)?/press\?([^"]*)"', lambda m: q2(m), html)
    return html

def write(rel, data):
    p = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "wb" if isinstance(data, bytes) else "w", encoding=None if isinstance(data, bytes) else "utf-8") as f:
        f.write(data)

if os.path.exists(OUT):
    shutil.rmtree(OUT)
shutil.copytree(SRC, OUT, ignore=shutil.ignore_patterns("vogin.html"))

# ---- articles
items = json.loads(get("/api/articles?limit=24"))["items"]
media = set()
write("api/articles.json", json.dumps({"items": items}, ensure_ascii=False))

pages_written = []
def list_pages(category=""):
    n = len([a for a in items if not category or a["category"] == category])
    pages = max(1, -(-n // PER_PAGE))
    for p in range(1, pages + 1):
        qs = urllib.parse.urlencode({k: v for k, v in (("category", category), ("page", p if p > 1 else "")) if v})
        html = get("/press" + ("?" + qs if qs else ""))
        rel = press_url(category, p).lstrip("/") + "/index.html"
        write(rel, fix(html))
        pages_written.append(rel)
        media.update(re.findall(r'/media/[A-Za-z0-9_./-]+', html))

list_pages()
for c in CATS:
    list_pages(c)

for a in items:
    html = get("/press/" + urllib.parse.quote(a["slug"]))
    write(f"press/{a['slug']}/index.html", fix(html))
    pages_written.append(f"press/{a['slug']}/index.html")
    media.update(re.findall(r'/media/[A-Za-z0-9_./-]+', html))

notfound = subprocess.run(["curl", "-sS", "-m", "60", LIVE + "/press/__missing__"], capture_output=True).stdout.decode()
write("404.html", fix(notfound))

for m in sorted(media):
    write(m.lstrip("/"), get(m, binary=True))

# ---- homepage: static JSON instead of the function
p = os.path.join(OUT, "index.html")
s = open(p, encoding="utf-8").read()
n0 = s.count("/api/articles?limit=")
s = s.replace("fetch('/api/articles?limit=3').then(function(r){ if(!r.ok) throw 0; return r.json(); }).then(function(j){\n    var items=(j&&j.items)||[];",
              "fetch('/api/articles.json').then(function(r){ if(!r.ok) throw 0; return r.json(); }).then(function(j){\n    var items=((j&&j.items)||[]).slice(0,3);")
s = s.replace("fetch('/api/articles?limit=1')", "fetch('/api/articles.json')")
assert "/api/articles?limit=" not in s, "homepage fetch not patched"
open(p, "w", encoding="utf-8").write(s)

# ---- contact form -> PHP
p = os.path.join(OUT, "contact.html")
s = open(p, encoding="utf-8").read()
s = s.replace('action="/contact?sent=1#form" data-netlify="true" netlify-honeypot="company-website"', 'action="/contact.php"')
s = s.replace("fetch('/',{method:'POST'", "fetch('/contact.php',{method:'POST'")
assert "data-netlify" not in s and "fetch('/contact.php'" in s, "contact not patched"
open(p, "w", encoding="utf-8").write(s)

shutil.copytree(os.path.join(os.path.dirname(os.path.abspath(__file__)), "extra"), OUT, dirs_exist_ok=True)
print(f"{len(items)} articles, {len(pages_written)} press pages, {len(media)} media files")
