"""Collects every visible string (text nodes + translatable attributes) from the built pages, SSR press pages and dynamic data."""
import sys, re, json, glob, urllib.request
from bs4 import BeautifulSoup, NavigableString, Comment
sys.path.insert(0, sys.argv[1])
from franchise_data import FRANCHISES
pub, out = sys.argv[2], sys.argv[3]
norm = lambda s: re.sub(r"\s+", " ", s).strip()
found = {}
def add(s, where):
    s = norm(s)
    if not s or not re.search(r"[A-Za-z]", s): return
    found.setdefault(s, set()).add(where)
def scan(html, where):
    soup = BeautifulSoup(html, "lxml")
    for t in soup.find_all(string=True):
        if isinstance(t, Comment): continue
        if t.parent.name in ("script", "style", "noscript", "svg", "title") and t.parent.name != "title": continue
        if t.find_parent(class_="prose") or t.find_parent(attrs={"class": "amap"}) and t.parent.name != "text": pass
        if t.find_parent(class_="prose"): continue
        add(str(t), where)
    for el in soup.find_all(True):
        for a in ("alt", "aria-label", "placeholder", "title"):
            if el.has_attr(a): add(el[a], where + "@" + a)
    m = soup.find("meta", attrs={"name": "description"})
    if m: add(m["content"], where + "@desc")
    if soup.title: add(soup.title.get_text(), where + "@title")
for f in sorted(glob.glob(pub + "/*.html")):
    if f.endswith("vogin.html"): continue
    scan(open(f, encoding="utf-8").read(), f.rsplit("/", 1)[1])
for u in ["/press", "/press/the-piaget-event-celebrating-fine-watchmaking-at-an-intimate-cocktail-evening", "/press?category=Brands", "/press/nope-404"]:
    try:
        scan(urllib.request.urlopen(urllib.request.Request("https://kennys-international.netlify.app" + u, headers={"user-agent": "x"}), timeout=30).read().decode(), "SSR" + u)
    except Exception as e:
        try: scan(e.read().decode(), "SSR" + u)
        except Exception: print("could not fetch", u, e)
for f in FRANCHISES:
    add(f["cat"], "fran"); add(f["blurb"], "fran")
    for l in f["locs"]:
        if l.get("label"): add(l["label"], "fran")
        for d, h in l["hours"]: add(d, "fran"); add(h, "fran")
json.dump({k: sorted(v) for k, v in sorted(found.items())}, open(out, "w"), ensure_ascii=False, indent=0)
print(len(found), "strings")
