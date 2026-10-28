"""Copies the old WordPress Press articles into the new site through its dashboard API.
Usage: python3 -I import_old.py <posts_full.json> <work dir> <base url> <password> [--go]
Without --go it only converts and reports (no uploads, no articles created)."""
import sys, json, re, html, io, os, hashlib, urllib.request, http.cookiejar
from bs4 import BeautifulSoup, NavigableString, Tag
from PIL import Image

posts_path, work, base, pw = sys.argv[1:5]
GO = "--go" in sys.argv
os.makedirs(work, exist_ok=True)
SKIP = {4619}  # Piaget: already on the new site
CATS = {4613: "Store openings", 4437: "News", 4349: "Events", 4272: "Store openings", 4188: "Events", 4067: "Store openings",
        3931: "Store openings", 3692: "Store openings", 3679: "Store openings", 3195: "Brands", 2707: "Store openings",
        3127: "News", 3140: "Brands", 3154: "Store openings", 3164: "Store openings"}
EMOJI = re.compile("[\U0001F000-\U0001FAFF☀-➿️‍]+")

def best_src(img):
    cands = []
    for part in (img.get("srcset") or "").split(","):
        bits = part.strip().split()
        if len(bits) == 2 and bits[1].endswith("w"):
            cands.append((int(bits[1][:-1]), bits[0]))
    if cands:
        return max(cands)[1]
    return img.get("data-src") or img.get("src") or ""

def key(url):  # same photo regardless of size suffix
    return re.sub(r"-(\d+x\d+|scaled)(?=\.\w+$)", "", url.split("?")[0].rsplit("/", 1)[-1]).lower()

def convert(content):
    soup = BeautifulSoup(content, "lxml")
    root = soup.body or soup
    out = []  # list of html strings (blocks)
    images = []

    def inline(node):
        if isinstance(node, NavigableString):
            return html.escape(str(node), quote=False)
        if not isinstance(node, Tag):
            return ""
        name = node.name
        inner = "".join(inline(c) for c in node.children)
        if name in ("strong", "b"):
            return f"<strong>{inner}</strong>" if inner.strip() else inner
        if name in ("em", "i"):
            return f"<em>{inner}</em>" if inner.strip() else inner
        if name == "br":
            return "<br>"
        if name == "a":
            href = node.get("href", "")
            if re.match(r"^(https?:|mailto:|tel:)", href) and inner.strip():
                return f'<a href="{html.escape(href)}">{inner}</a>'
            return inner
        if name == "img":
            return ""
        return inner

    def para(text):
        t = text.strip()
        t = re.sub(r"^(<br>\s*)+|(\s*<br>)+$", "", t).strip()
        if t and re.sub(r"<[^>]+>|&nbsp;|\s", "", t):
            out.append(f"<p>{t}</p>")

    def block(node):
        if isinstance(node, NavigableString):
            para(html.escape(str(node), quote=False)); return
        if not isinstance(node, Tag) or node.name in ("script", "style", "noscript"):
            return
        n = node.name
        if n == "img":
            src = best_src(node)
            if src:
                images.append(src); out.append(("IMG", src, node.get("alt", "")))
            return
        if n in ("figure",) or "swiper" in " ".join(node.get("class", [])) or "gallery" in " ".join(node.get("class", [])):
            imgs = node.find_all("img")
            if imgs:
                for im in imgs:
                    src = best_src(im)
                    if src:
                        images.append(src); out.append(("IMG", src, im.get("alt", "")))
                cap = node.find("figcaption", recursive=False)
                if cap and cap.get_text(strip=True) and len(imgs) == 1:
                    out.append(f"<p><em>{html.escape(cap.get_text(' ', strip=True))}</em></p>")
                return
        if n in ("h1", "h2", "h3", "h4", "h5", "h6"):
            level = "h2" if n in ("h1", "h2") else "h3"
            txt = EMOJI.sub("", "".join(inline(c) for c in node.children)).strip()
            plain = html.unescape(re.sub(r"<[^>]+>", "", txt)).strip()
            if plain and len(plain) > 100:
                out.append(f"<p><strong>{re.sub(r'</?strong>', '', txt)}</strong></p>")
            elif plain:
                out.append(f"<{level}>{txt}</{level}>")
            for im in node.find_all("img"):
                block(im)
            return
        if n == "p":
            for im in node.find_all("img"):
                src = best_src(im)
                if src:
                    images.append(src); out.append(("IMG", src, im.get("alt", "")))
            inner = "".join(inline(c) for c in node.children).strip()
            plain = html.unescape(re.sub(r"<[^>]+>", "", inner)).strip()
            if re.fullmatch(r"(<strong>.*?</strong>\s*)+", inner, re.S) and 3 < len(plain) <= 90 and not plain.endswith((".", ":", "!", "?")):
                out.append(f"<h3>{EMOJI.sub('', re.sub(r'</?strong>', '', inner)).strip()}</h3>"); return
            para(inner); return
        if n in ("ul", "ol"):
            items = [("".join(inline(c) for c in li.children)).strip() for li in node.find_all("li", recursive=False)]
            items = [i for i in items if re.sub(r"<[^>]+>|\s", "", i)]
            if items:
                out.append(f"<{n}>" + "".join(f"<li>{i}</li>" for i in items) + f"</{n}>")
            return
        if n == "blockquote":
            t = " ".join(p.get_text(" ", strip=True) for p in node.find_all("p")) or node.get_text(" ", strip=True)
            if t:
                out.append(f"<blockquote><p>{html.escape(t)}</p></blockquote>")
            return
        if n == "hr":
            out.append("<hr>"); return
        # containers: div, section, span, etc.
        kids = list(node.children)
        if all(isinstance(k, NavigableString) or (isinstance(k, Tag) and k.name in ("strong", "b", "em", "i", "a", "br", "span")) for k in kids):
            para("".join(inline(k) for k in kids)); return
        for k in kids:
            block(k)

    for child in list(root.children):
        block(child)
    return out, images

def first_para_text(blocks, limit=300):
    for b in blocks:
        if isinstance(b, str) and b.startswith("<p>"):
            t = html.unescape(re.sub(r"<[^>]+>", "", b)).strip()
            t = EMOJI.sub("", t).strip()
            if len(t) < 40:
                continue
            if len(t) <= limit:
                return t
            cut = t[:limit]
            s = max(cut.rfind(". "), cut.rfind("! "), cut.rfind("? "))
            return (cut[:s + 1] if s > 120 else cut[:cut.rfind(" ")].rstrip(",;:") + "…")
    return ""

# ---------- HTTP helpers ----------
cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
def api(method, path, body=None, raw=None, ctype=None):
    data = raw if raw is not None else (json.dumps(body).encode() if body is not None else None)
    req = urllib.request.Request(base + path, data=data, method=method, headers={"x-kp": "1", "content-type": ctype or "application/json", "user-agent": "KennysImporter/1.0"})
    try:
        with opener.open(req, timeout=90) as r:
            return r.status, json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"{}")

def fetch(url):
    p = os.path.join(work, hashlib.sha1(url.encode()).hexdigest()[:16])
    if os.path.exists(p):
        return open(p, "rb").read()
    req = urllib.request.Request(url, headers={"user-agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read()
    open(p, "wb").write(data)
    return data

def prepare(data):
    im = Image.open(io.BytesIO(data))
    im = im.convert("RGB")
    im.thumbnail((2000, 2000), Image.LANCZOS)
    buf = io.BytesIO(); im.save(buf, "JPEG", quality=85, optimize=True, progressive=True)
    return buf.getvalue(), im.size

uploaded = {}
def upload(url):
    k = key(url)
    if k in uploaded:
        return uploaded[k]
    data = fetch(url)
    jpg, size = prepare(data)
    if not GO:
        uploaded[k] = f"/media/DRYRUN/{k}"; return uploaded[k]
    st, j = api("POST", "/api/admin/upload", raw=jpg, ctype="image/jpeg")
    if st != 201:
        raise RuntimeError(f"upload failed {st} {j} for {url}")
    uploaded[k] = j["url"]
    return j["url"]

posts = json.load(open(posts_path))
if GO:
    st, j = api("POST", "/api/auth/login", {"email": "refdigital@kennysinternational.com", "password": pw})
    assert st == 200, (st, j)
    st, j = api("GET", "/api/admin/articles")
    existing = {a["title"].lower() for a in j["items"]}
else:
    existing = set()

report = []
for p in sorted(posts, key=lambda x: x["date"]):
    if p["id"] in SKIP:
        continue
    title = html.unescape(p["title"]["rendered"]).strip().rstrip(".").strip()
    if title.lower() in existing:
        report.append((p["id"], title, "already on the new site, skipped")); continue
    blocks, imgs = convert(p["content"]["rendered"])
    while blocks and isinstance(blocks[-1], str) and blocks[-1].startswith("<h3>"):  # a closing "heading" is a signature
        last = blocks.pop(); blocks.append("<p><em>" + last[4:-5] + "</em></p>"); break
    fm = None
    if p.get("featured_media"):
        try:
            fmo = p["_embedded"]["wp:featuredmedia"][0]
            fm = (fmo.get("source_url"), fmo.get("alt_text") or "")
        except Exception:
            fm = None
    img_blocks = [b for b in blocks if isinstance(b, tuple)]
    if fm and fm[0]:
        cover_src, cover_alt = fm
    elif img_blocks:
        cover_src, cover_alt = img_blocks[0][1], img_blocks[0][2]
    else:
        cover_src, cover_alt = None, ""
    # don't repeat the cover photo as the first photo in the text
    if cover_src:
        for i, b in enumerate(blocks):
            if isinstance(b, tuple):
                if key(b[1]) == key(cover_src):
                    blocks.pop(i)
                break
    body_parts = []
    for b in blocks:
        if isinstance(b, tuple):
            body_parts.append(f'<img src="{upload(b[1])}" alt="{html.escape(b[2] or "")}">')
        else:
            body_parts.append(b)
    body = "\n".join(body_parts)
    cover = {"url": upload(cover_src) if cover_src else "", "alt": (cover_alt or title)[:200]}
    excerpt = first_para_text(blocks) or title
    art = {"title": title, "excerpt": excerpt, "body": body, "category": CATS.get(p["id"], "News"),
           "date": p["date"][:10], "status": "published" if cover["url"] else "draft", "cover": cover}
    n_img = sum(1 for b in blocks if isinstance(b, tuple))
    if GO:
        st, j = api("POST", "/api/admin/articles", art)
        if st != 201:
            art["status"] = "draft"; st, j = api("POST", "/api/admin/articles", art)
        report.append((p["id"], title, f"{st} {j.get('article', {}).get('status')} /press/{j.get('article', {}).get('slug')} photos={n_img} {j.get('error', '')}"))
    else:
        report.append((p["id"], title, f"{art['category']} {art['date']} photos_in_text={n_img} cover={'yes' if cover['url'] else 'NO'} excerpt={excerpt[:70]!r}"))
        open(os.path.join(work, f"preview-{p['id']}.html"), "w").write(f"<h1>{html.escape(title)}</h1><p><i>{html.escape(excerpt)}</i></p>{body}")

for r in report:
    print(r[0], "|", r[1], "|", r[2])
print("photos prepared:", len(uploaded))
