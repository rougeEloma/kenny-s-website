"""Builds the whole Kenny's International static site from index.base.html.
Run: python3 -I build2.py <scratchpad dir> <site dir>"""
import sys, re, json, html
sys.path.insert(0, sys.argv[1])
from franchise_data import FRANCHISES, DISTRIBUTION, FRAGRANCE

SP, SITE, TPL_OUT = sys.argv[1], sys.argv[2], sys.argv[3]
base = open(f"{SP}/index.base.html", encoding="utf-8").read()
MAP_SVG = open(f"{SP}/map.svg.txt", encoding="utf-8").read()

# ------------------------------------------------------------------ facts
ADDR_1 = "124 Boulevard du 30 Juin, Gombe, Kinshasa"
ADDR_2 = "Royal building, ref. K Lounge, opposite Interpol"
PHONE = "+243 818 592 999"
PHONE_HREF = "tel:+243818592999"
EMAIL = "serviceclient@kennysinternational.com"
HQ_MAPS = "https://www.google.com/maps/search/?api=1&query=Kenny%27s%2C%20124%20Boulevard%20du%2030%20Juin%2C%20Kinshasa&query_place_id=ChIJDx_WmmkzahoRD1H34Wt_27c"
HQ_EMBED = "https://maps.google.com/maps?q=-4.3128662,15.285098&z=16&output=embed"
KG_MAPS = "https://www.google.com/maps/search/?api=1&query=K%20Galerie%20Pointe-Noire&query_place_id=ChIJ6WR8jpSlYBoRVgQvkF967S8"
SOCIAL = dict(
    instagram="https://www.instagram.com/kennysinternational/",
    facebook="https://www.facebook.com/KennysInternationals",
    linkedin="https://www.linkedin.com/company/kennysinternational/")
KENNY_SITE = "https://kennyrawtani.com/"
KENNY_LI = "https://www.linkedin.com/in/kenny-rawtani-326a83201/"

NAV = [("index.html", "Home", "home"), ("about-us.html", "About us", "about"),
       ("group", "Brands", "brands", [("distribution-brands.html", "Kenny's Stores", "dist", "Distribution brands"),
                                      ("franchise-retail.html", "Franchises", "fran", "Franchise retail")]),
       ("k-galerie.html", "K-Galerie", "kg"), ("/press", "Press", "press"), ("contact.html", "Contact", "contact")]

ARROW = '<svg height="10" viewBox="0 0 46 10" preserveAspectRatio="none" fill="none" stroke="currentColor" stroke-width="1" aria-hidden="true"><path d="M0 5h45M40 1l5 4-5 4"></path></svg>'
BTN_ARROW = '<svg width="22" height="12" viewBox="0 0 22 12" fill="none" stroke="currentColor" stroke-width="1.4" aria-hidden="true"><path d="M0 6h21M16 1l5 5-5 5"></path></svg>'
ICON = dict(
    instagram='<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="5"></rect><circle cx="12" cy="12" r="4"></circle></svg>',
    facebook='<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M14 8h3V4h-3a4 4 0 0 0-4 4v3H7v4h3v6h4v-6h3l1-4h-4V8z"></path></svg>',
    linkedin='<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M7 10v8M7 6v.01M11 18v-5a3 3 0 0 1 6 0v5M11 10v8"></path></svg>')
EXT = 'target="_blank" rel="noopener"'
ICON16 = {k: v.replace('width="13" height="13"', 'width="16" height="16"') for k, v in ICON.items()}

def lnk(href, text, ext=False):
    return f'<a class="lnk" href="{href}"{" " + EXT if ext else ""}>{text}{ARROW}</a>'

# ------------------------------------------------------------------ fix the base page's global rules
for a, b in [(".ph{position:absolute;inset:0;opacity:0;transition:opacity 1.2s ease}", ".hero .ph{position:absolute;inset:0;opacity:0;transition:opacity 1.2s ease}"),
             (".ph.on{opacity:1}", ".hero .ph.on{opacity:1}"),
             (".ph img{width:100%;height:100%;object-fit:cover}", ".hero .ph img{width:100%;height:100%;object-fit:cover}")]:
    assert base.count(a) == 1, a
    base = base.replace(a, b)
base = base.replace(".lgk{background-image:url(assets/logos-kennys.png);background-size:100% 2000%}", ".lgk{background-image:url(assets/logos-kennys.png);background-size:100% 2100%}")
assert "2100%" in base

# ------------------------------------------------------------------ CSS shared by every page
SHARED_CSS = """
/* buttons and clickable tiles */
.btn{display:inline-flex;align-items:center;justify-content:center;gap:18px;min-height:54px;padding:0 34px;border:1px solid #000;background:transparent;color:#000;text-decoration:none;font:inherit;font-size:11px;letter-spacing:.24em;text-transform:uppercase;font-weight:600;cursor:pointer;transition:background .35s,color .35s,border-color .35s}
.btn svg{transition:transform .5s cubic-bezier(.2,.8,.1,1)}
.btn:hover{background:#000;color:#fff}
.btn:hover svg{transform:translateX(6px)}
.btn.solid{background:#000;color:#fff}
.btn.solid:hover{background:var(--gold);border-color:var(--gold);color:#000}
.on-dark .btn{border-color:var(--gold);color:#fff}
.on-dark .btn:hover{background:var(--gold);color:#000}
.morebar{display:flex;justify-content:center;margin-top:clamp(48px,5vw,80px)}
a.tile,button.tile{width:100%;margin:0;padding:0;border-top:0;border-left:0;background:#fff;font:inherit;color:inherit;text-decoration:none;cursor:pointer}
.tile .vw{position:absolute;top:16px;right:16px;width:30px;height:30px;display:flex;align-items:center;justify-content:center;border:1px solid #E8E8E8;color:var(--gold-ink);transition:background .35s,border-color .35s,color .35s}
.tile:hover .vw,.tile:focus-visible .vw{background:var(--gold);border-color:var(--gold);color:#000}
.navlist{gap:clamp(20px,2.3vw,44px) !important;align-items:center}
/* Brands dropdown */
.ndd{position:relative;display:flex;align-items:center}
.ndd>.navi{background:none;border:0;cursor:pointer;font:inherit;font-size:11px;letter-spacing:.2em;text-transform:uppercase;font-weight:500;display:inline-flex;align-items:center;gap:8px}
.ndd .chev{transition:transform .3s}
.ndd:hover .chev,.ndd.open .chev{transform:rotate(180deg)}
.ddp{position:absolute;top:100%;left:50%;min-width:270px;transform:translate(-50%,10px);padding:10px;background:#0B0B0B;border:1px solid #2B2B2B;border-top:2px solid var(--gold);opacity:0;visibility:hidden;transition:opacity .25s,transform .25s,visibility 0s .25s;z-index:60;box-shadow:0 18px 40px rgba(0,0,0,.35)}
.ddp::before{content:"";position:absolute;left:0;right:0;top:-14px;height:14px}
.ndd:hover .ddp,.ndd.open .ddp,.ndd:focus-within .ddp{opacity:1;visibility:visible;transform:translate(-50%,2px);transition-delay:0s}
.ddp a{display:block;padding:14px 16px;text-decoration:none;color:#fff;transition:background .25s}
.ddp a span{display:block;font-size:11px;letter-spacing:.2em;text-transform:uppercase;font-weight:500}
.ddp a small{display:block;margin-top:6px;font-size:13px;color:#8C8C8C}
.ddp a:hover,.ddp a:focus-visible{background:#1A1A1A}
.ddp a:hover span,.ddp a[aria-current] span{color:var(--gold)}
.mgrp{margin:14px 0 2px;font-size:11px;letter-spacing:.24em;text-transform:uppercase;font-weight:500;color:var(--gold)}
/* live news cards */
.news-sk{display:block}
.news-sk .ph{background:linear-gradient(90deg,#F1EFEA 0,#F8F7F3 50%,#F1EFEA 100%);background-size:200% 100%;animation:sk 1.4s linear infinite}
.news-sk i{display:block;height:12px;margin-top:22px;background:#F1EFEA;width:40%}
.news-sk i+i{width:85%;height:16px}
@keyframes sk{from{background-position:200% 0}to{background-position:-200% 0}}
.dot-sep{color:#BDBDBD;margin:0 4px}
/* header: dark gradient at the top, white once scrolled */
:root{--hh:clamp(68px,9vh,96px)}
.htop,.ptop{position:fixed !important;top:0;left:0;right:0;height:var(--hh);z-index:70;isolation:isolate;background:transparent !important;border-bottom:0 !important}
.htop::before,.ptop::before{content:"";position:absolute;left:0;right:0;top:0;height:calc(100% + 56px);background:linear-gradient(180deg,rgba(0,0,0,.62) 0%,rgba(0,0,0,.32) 55%,rgba(0,0,0,0) 100%);z-index:-1;pointer-events:none;transition:opacity .55s ease}
.htop::after,.ptop::after{content:"";position:absolute;inset:0;background:#fff;box-shadow:0 1px 0 rgba(0,0,0,.07),0 12px 32px rgba(0,0,0,.07);opacity:0;z-index:-1;pointer-events:none;transition:opacity .55s ease}
.htop.scrolled::before,.ptop.scrolled::before{opacity:0}
.htop.scrolled::after,.ptop.scrolled::after{opacity:1}
.htop img,.ptop img{transition:filter .55s ease}
.htop.scrolled img,.ptop.scrolled img{filter:none !important}
.htop>div:first-child>a,.ptop>div:first-child>a{transition:color .55s ease}
.htop.scrolled>div:first-child>a,.ptop.scrolled>div:first-child>a{color:#000 !important}
.navi,.mbtn{transition:color .55s ease}
.soc{transition:border-color .55s ease,color .55s ease}
.scrolled .navi{color:rgba(0,0,0,.6)}
.scrolled .navi:hover,.scrolled .navi.act{color:#000}
.scrolled .soc{border-color:rgba(0,0,0,.28);color:#000}
.scrolled .soc:hover{border-color:var(--gold-ink);color:var(--gold-ink)}
.scrolled .mbtn{color:#000}
section[id]{scroll-margin-top:var(--hh)}
.lang{display:inline-flex;align-items:center;gap:4px;padding-left:clamp(14px,1.6vw,24px);border-left:1px solid rgba(255,255,255,.28);font-size:11px;letter-spacing:.18em;font-weight:500;transition:border-color .55s ease}
.lang button{background:none;border:0;cursor:pointer;font:inherit;letter-spacing:inherit;padding:8px 3px;min-height:36px;color:rgba(255,255,255,.5);transition:color .55s ease}
.lang button:hover{color:#fff}
.lang button[aria-pressed="true"]{color:#fff;font-weight:600}
.lang span{color:rgba(255,255,255,.35);transition:color .55s ease}
.scrolled .lang{border-left-color:rgba(0,0,0,.18)}
.scrolled .lang button{color:rgba(0,0,0,.42)}
.scrolled .lang button:hover,.scrolled .lang button[aria-pressed="true"]{color:#000}
.scrolled .lang span{color:rgba(0,0,0,.25)}
@media (max-width:1180px){.lang{border-left:0;padding-left:0}}

@media (max-width:1180px){
  .navlist{display:none !important}
  .mbtn{display:inline-flex;align-items:center}
}
"""

SUB_CSS = """
/* sub-page header */
.ptop{position:sticky;top:0;z-index:30;display:flex;align-items:center;justify-content:space-between;gap:24px;height:clamp(68px,9vh,96px);padding:0 clamp(22px,3.4vw,56px) 0 var(--g);background:#000;color:#fff;border-bottom:1px solid #1E1E1E}
.ptop #mnav{position:absolute;top:100%;left:0;right:0}
.crumb{display:flex;gap:12px;align-items:center;margin:0 0 clamp(40px,4vw,64px);font-size:11px;letter-spacing:.24em;text-transform:uppercase;font-weight:500;color:#8C8C8C}
.crumb a{text-decoration:none;color:#BDBDBD;transition:color .3s}
.crumb a:hover{color:var(--gold)}
.phead{background:#000;color:#fff;padding:calc(var(--hh) + clamp(56px,7vw,120px)) 0 clamp(80px,9vw,150px)}
.ptitle{margin:0;font-size:clamp(34px,5.2vw,96px);line-height:1.02}
.count{font-size:13px;color:#8C8C8C;margin:22px 0 0}
.sec{padding:clamp(100px,10vw,170px) 0}
.h2{margin:0;font-size:clamp(28px,3.2vw,60px);line-height:1.1}
.body{font-size:16px;line-height:1.8;color:#4A4A4A;font-weight:300}
.on-dark .body{color:#BDBDBD}
.fraglist{list-style:none;margin:0;padding:0;columns:4;column-gap:clamp(28px,3vw,56px)}
.fraglist li{break-inside:avoid;padding:16px 0;border-bottom:1px solid #E8E8E8;font-size:16px;color:#3A3A3A;display:flex;gap:16px}
.fraglist li span{color:var(--gold-ink);font-size:11px;letter-spacing:.12em;min-width:22px;padding-top:3px}
.closing{background:#000;color:#fff;padding:clamp(100px,10vw,180px) 0;text-align:center}
.closing .stmt{margin:0 auto;max-width:1100px;font-size:clamp(24px,3vw,52px);line-height:1.22}
.closing .cities{margin:34px 0 0;font-size:13px;letter-spacing:.24em;text-transform:uppercase;color:var(--gold)}
@media (max-width:1100px){.fraglist{columns:3}}
@media (max-width:820px){.fraglist{columns:2}}
@media (max-width:480px){.fraglist{columns:1}}

/* franchise pop-up card */
.fcard{width:min(680px,calc(100% - 32px));max-height:calc(100dvh - 48px);padding:0;border:1px solid var(--gold);background:#fff;color:#000;overflow:auto;overscroll-behavior:contain}
.fcard::backdrop{background:rgba(0,0,0,.62);-webkit-backdrop-filter:blur(6px);backdrop-filter:blur(6px)}
.fcard[open]{animation:fcin .55s cubic-bezier(.2,.8,.1,1)}
@keyframes fcin{from{opacity:0;transform:translateY(28px)}to{opacity:1;transform:none}}
.fc-x{position:absolute;top:14px;right:14px;width:44px;height:44px;display:flex;align-items:center;justify-content:center;background:#fff;border:1px solid #E8E8E8;cursor:pointer;color:#000;transition:background .3s,border-color .3s;z-index:2}
.fc-x:hover{background:var(--gold);border-color:var(--gold)}
.fc-logo{position:relative;display:flex;align-items:center;justify-content:center;height:clamp(150px,22vh,210px);background:#F5F3EE;border-bottom:1px solid #E8E8E8}
.fc-logo .lg{width:min(300px,60%);aspect-ratio:12/5;background-repeat:no-repeat}
.fc-body{padding:clamp(28px,4vw,48px)}
.fc-name{margin:14px 0 0;font-size:clamp(22px,2.4vw,32px);line-height:1.15}
.fc-blurb{margin:16px 0 0;font-size:16px;line-height:1.7;color:#4A4A4A}
.fc-loc{margin-top:34px;padding-top:28px;border-top:1px solid #E8E8E8}
.fc-loc h3{margin:0 0 20px;font-size:11px;letter-spacing:.24em;text-transform:uppercase;font-weight:600;color:var(--gold-ink)}
.fc-dl{display:grid;grid-template-columns:120px minmax(0,1fr);gap:14px 20px;margin:0;font-size:15px;line-height:1.6}
.fc-dl dt{font-size:10px;letter-spacing:.2em;text-transform:uppercase;font-weight:500;color:#8C8C8C;padding-top:4px}
.fc-dl dd{margin:0;color:#1A1A1A}
.fc-dl a{text-decoration:none;border-bottom:1px solid var(--gold);transition:color .3s}
.fc-dl a:hover{color:var(--gold-ink)}
.fc-hours{border-collapse:collapse}
.fc-hours th{font-weight:400;text-align:left;padding:0 22px 4px 0;color:#4A4A4A;white-space:nowrap}
.fc-hours td{padding:0 0 4px;white-space:nowrap}
.fc-loc .lnk{margin-top:14px}
@media (max-width:600px){
  .fcard{width:100%;max-width:100%;max-height:90dvh;margin:auto 0 0;border-left:0;border-right:0;border-bottom:0}
  .fcard[open]{animation-name:fcup}
  .fc-dl{grid-template-columns:minmax(0,1fr);gap:4px}
  .fc-dl dd{margin-bottom:14px}
}
@keyframes fcup{from{transform:translateY(100%)}to{transform:none}}

/* about: stats, beliefs, timeline, founder, map */
.stats{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:24px;margin:clamp(56px,6vw,96px) 0 0;padding-top:clamp(36px,4vw,56px);border-top:1px solid #2B2B2B}
.stats dt{font-size:10px;letter-spacing:.24em;text-transform:uppercase;font-weight:500;color:#8C8C8C}
.stats dd{margin:14px 0 0;font-size:clamp(26px,2.8vw,48px)}
.beliefs{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(4,minmax(0,1fr));border-top:1px solid #2B2B2B}
.beliefs li{padding:clamp(36px,4vw,56px) clamp(20px,2.4vw,40px) 0 0}
.beliefs li+li{padding-left:clamp(20px,2.4vw,40px);border-left:1px solid #2B2B2B}
.beliefs svg{width:46px;height:46px;color:var(--gold)}
.beliefs h3{margin:28px 0 0;font-size:clamp(15px,1.3vw,20px)}
.beliefs p{margin:14px 0 0;font-size:15px;line-height:1.7;color:#BDBDBD;font-weight:300}
.tl-head{display:flex;justify-content:space-between;align-items:end;gap:24px;margin:clamp(72px,7vw,120px) 0 36px}
.tl-ctrl{display:flex;gap:12px}
.tl-btn{width:48px;height:48px;display:inline-flex;align-items:center;justify-content:center;border:1px solid #000;background:#fff;color:#000;cursor:pointer;transition:background .3s,color .3s,opacity .3s}
.tl-btn:hover{background:#000;color:#fff}
.tl-btn:disabled{opacity:.25;cursor:default;background:#fff;color:#000}
.tl{list-style:none;margin:0;padding:10px 0 10px;display:grid;grid-auto-flow:column;grid-auto-columns:clamp(250px,23vw,330px);overflow-x:auto;scroll-snap-type:x mandatory;scrollbar-width:none;overscroll-behavior-x:contain}
.tl::-webkit-scrollbar{display:none}
.tl li{position:relative;scroll-snap-align:start;padding:46px 36px 0 0;border-top:1px solid #000}
.tl li::before{content:"";position:absolute;top:-7px;left:0;width:12px;height:12px;transform:rotate(45deg);background:#fff;border:1.5px solid #000}
.tl li.key::before{background:var(--gold);border-color:var(--gold)}
.tl .yr{margin:0;font-size:clamp(26px,2.4vw,40px)}
.tl .yr.gold{color:var(--gold-ink)}
.tl ul{list-style:none;margin:20px 0 0;padding:0}
.tl ul li{all:unset;display:block;padding:10px 0;border-bottom:1px solid #E8E8E8;font-size:15px;line-height:1.55;color:#3A3A3A}
.tl-note{margin:18px 0 0;font-size:13px;color:#8C8C8C}
.founder{position:relative;background:#000;color:#fff;overflow:hidden}
.founder::before{content:"";position:absolute;right:-10%;bottom:-30%;width:70%;aspect-ratio:1;background:radial-gradient(closest-side,rgba(201,165,92,.22),rgba(201,165,92,0));pointer-events:none}
.founder .wrap{position:relative;display:grid;grid-template-columns:minmax(0,1.05fr) minmax(0,1fr);gap:clamp(40px,6vw,120px);align-items:end}
.founder .txt{padding:clamp(100px,10vw,170px) 0}
.founder .pic{align-self:end;display:flex;justify-content:center}
.founder .pic img{width:100%;max-width:520px;height:auto;max-height:780px;object-fit:contain;object-position:bottom}
.sig{display:block;width:min(340px,80%);height:auto;margin:40px 0 0;opacity:.95}
.flinks{display:flex;align-items:center;gap:28px;margin-top:34px;padding-top:28px;border-top:1px solid #2B2B2B;flex-wrap:wrap}
.sq{width:44px;height:44px;display:inline-flex;align-items:center;justify-content:center;border:1px solid rgba(255,255,255,.55);color:#fff;transition:border-color .3s,color .3s,background .3s}
.sq:hover{border-color:var(--gold);color:var(--gold)}
.where{background:#F5F3EE}
.where .wrap{display:grid;grid-template-columns:minmax(0,.8fr) minmax(0,1.2fr);gap:clamp(40px,6vw,110px);align-items:center}
.clist{list-style:none;margin:40px 0 0;padding:0;border-top:1px solid #D9D3C6}
.clist li{display:flex;justify-content:space-between;gap:20px;align-items:baseline;padding:18px 0;border-bottom:1px solid #D9D3C6}
.clist .c{font-size:clamp(14px,1.2vw,18px)}
.clist .n{font-size:11px;letter-spacing:.24em;text-transform:uppercase;font-weight:500;color:var(--gold-ink)}
.amap{width:100%;height:auto;display:block;overflow:visible}
.amap .m-oth path{fill:#E4DED1;stroke:#F5F3EE;stroke-width:1.4}
.amap .m-home path{fill:#C9B58A;stroke:#F5F3EE;stroke-width:1.4}
.amap .m-cty{font-family:"Syncopate","Michroma",sans-serif;font-size:15px;letter-spacing:.2em;fill:#86671F;opacity:.75}
.amap .m-pin rect{fill:#000}
.amap .m-city{font-family:"Jost",sans-serif;font-size:21px;font-weight:500;letter-spacing:.04em;fill:#000;paint-order:stroke;stroke:#F5F3EE;stroke-width:5px;stroke-linejoin:round}
.amap .m-pulse{fill:none;stroke:#86671F;stroke-width:1.5;transform-box:fill-box;transform-origin:center;animation:pulse 2.6s var(--d) ease-out infinite}
@keyframes pulse{from{transform:scale(.6);opacity:.9}to{transform:scale(3.2);opacity:0}}
.social{display:flex;justify-content:center;gap:14px;flex-wrap:wrap;margin-top:44px}
.social a{display:inline-flex;align-items:center;gap:14px;min-height:54px;padding:0 28px;border:1px solid #3A3A3A;color:#fff;text-decoration:none;font-size:11px;letter-spacing:.24em;text-transform:uppercase;font-weight:600;transition:border-color .3s,background .3s,color .3s}
.social a svg{width:16px;height:16px}
.social a:hover{background:var(--gold);border-color:var(--gold);color:#000}

/* k-galerie */
.feat{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(3,minmax(0,1fr));border-top:1px solid #E8E8E8}
.feat li{padding:clamp(32px,3.4vw,52px) clamp(20px,2.4vw,40px) 0 0}
.feat li+li{padding-left:clamp(20px,2.4vw,40px);border-left:1px solid #E8E8E8}
.feat .num{font-size:11px;letter-spacing:.24em;color:var(--gold-ink);font-weight:600}
.feat h3{margin:22px 0 0;font-size:clamp(16px,1.4vw,22px)}
.stores{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:0 clamp(24px,3vw,56px)}
.stores li{padding:20px 0;border-bottom:1px solid #2B2B2B;font-size:clamp(13px,1.05vw,16px)}
.visit{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:clamp(28px,3vw,56px)}
.visit > div{padding-top:30px;border-top:1px solid #E8E8E8}
.visit h3{margin:0 0 18px;font-size:11px;letter-spacing:.24em;text-transform:uppercase;font-weight:600;color:var(--gold-ink)}
.visit p{margin:0;font-size:16px;line-height:1.75;color:#1A1A1A}
.hrs{border-collapse:collapse;font-size:16px}
.hrs th{font-weight:400;text-align:left;padding:0 28px 6px 0;color:#6A6A6A;white-space:nowrap}
.hrs td{padding:0 0 6px;white-space:nowrap}

/* contact */
.cgrid{display:grid;grid-template-columns:minmax(0,.85fr) minmax(0,1.15fr);gap:clamp(48px,7vw,140px);align-items:start}
.cinfo{display:grid;gap:0}
.cinfo > div{padding:28px 0;border-top:1px solid #E8E8E8}
.cinfo > div:last-child{border-bottom:1px solid #E8E8E8}
.cinfo h3{margin:0 0 14px;font-size:11px;letter-spacing:.24em;text-transform:uppercase;font-weight:600;color:var(--gold-ink)}
.cinfo p{margin:0;font-size:17px;line-height:1.7;color:#1A1A1A}
.cinfo .sm{font-size:15px;color:#6A6A6A}
.cinfo a.big{text-decoration:none;border-bottom:1px solid var(--gold);transition:color .3s}
.cinfo a.big:hover{color:var(--gold-ink)}
.socrow{display:flex;gap:10px;margin-top:4px}
.socrow a{width:44px;height:44px;display:inline-flex;align-items:center;justify-content:center;border:1px solid #D0D0D0;color:#000;transition:background .3s,border-color .3s}
.socrow a:hover{background:var(--gold);border-color:var(--gold)}
.cform{background:#FAF9F6;border:1px solid #ECE8DF;padding:clamp(28px,4vw,60px)}
.frow{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:0 28px}
.fld{display:block;margin:0 0 30px}
.fld span{display:block;margin-bottom:10px;font-size:10px;letter-spacing:.22em;text-transform:uppercase;font-weight:600;color:#4A4A4A}
.fld span i{font-style:normal;color:#8C8C8C;font-weight:500;letter-spacing:.12em;text-transform:none;font-size:12px}
.fld input,.fld select,.fld textarea{width:100%;box-sizing:border-box;border:0;border-bottom:1px solid #BDBDBD;border-radius:0;background:transparent;padding:10px 0 12px;font:inherit;font-size:17px;color:#000;transition:border-color .3s;-webkit-appearance:none;appearance:none}
.fld select{background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8' fill='none' stroke='%2386671F' stroke-width='1.4'%3E%3Cpath d='M1 1l5 5 5-5'/%3E%3C/svg%3E");background-repeat:no-repeat;background-position:right 2px center;padding-right:28px;cursor:pointer}
.fld textarea{min-height:150px;resize:vertical;line-height:1.6}
.fld input:focus,.fld select:focus,.fld textarea:focus{outline:none;border-bottom-color:var(--gold-ink);box-shadow:0 1px 0 0 var(--gold-ink)}
.fld input:user-invalid,.fld textarea:user-invalid{border-bottom-color:#A23B2A}
.fnote{margin:0 0 26px;font-size:13px;line-height:1.6;color:#6A6A6A}
.hp{position:absolute;left:-9999px;width:1px;height:1px;overflow:hidden}
.fmsg{margin:22px 0 0;font-size:15px;line-height:1.6}
.fmsg.err{color:#A23B2A}
.fdone{text-align:left}
.fdone svg{width:46px;height:46px;color:var(--gold-ink)}
.fdone h2{margin:26px 0 0;font-size:clamp(22px,2.2vw,32px);line-height:1.2}
.fdone p{margin:16px 0 0;font-size:16px;line-height:1.7;color:#4A4A4A}
.cmap{position:relative;aspect-ratio:21/8;min-height:320px;background:#EEE;border-top:1px solid #E8E8E8}
.cmap iframe{position:absolute;inset:0;width:100%;height:100%;border:0;filter:grayscale(1) contrast(1.05)}
.cmap .pinbox{position:absolute;left:var(--g);bottom:28px;background:#000;color:#fff;padding:22px 26px;max-width:340px;border-left:2px solid var(--gold)}

@media (max-width:1100px){
  .founder .wrap,.where .wrap,.cgrid{grid-template-columns:minmax(0,1fr) !important}
  .founder .txt{padding-bottom:0}
  .founder .pic img{max-width:420px}
  .beliefs,.stats{grid-template-columns:repeat(2,minmax(0,1fr))}
  .beliefs li:nth-child(3){border-left:0;padding-left:0}
  .beliefs li{padding-bottom:36px}
  .stores{grid-template-columns:repeat(2,minmax(0,1fr))}
}
@media (max-width:820px){
  .feat,.visit{grid-template-columns:minmax(0,1fr)}
  .feat li+li{border-left:0;padding-left:0}
  .feat li{padding-bottom:28px}
  .cmap{aspect-ratio:auto;height:420px}
  .cmap .pinbox{left:16px;right:16px;max-width:none}
}
@media (max-width:600px){
  .amap .m-city{font-size:38px;stroke-width:10px}
  .amap .m-city.below{text-anchor:middle;transform:translate(22px,50px)}
  .amap .m-cty{font-size:26px}
  .beliefs{grid-template-columns:minmax(0,1fr)}
  .beliefs li+li{border-left:0;padding-left:0}
  .stats{grid-template-columns:repeat(2,minmax(0,1fr))}
  .stores,.frow{grid-template-columns:minmax(0,1fr)}
  .tl-head{flex-direction:column;align-items:flex-start}
}
"""

style = re.search(r"<style>(.*?)</style>", base, re.S).group(1)
head_links = re.search(r'(<link rel="icon".*?rel="stylesheet">)', base, re.S).group(1)
import hashlib as _hl
_fr = json.load(open(f"{SP}/i18n/fr.json", encoding="utf-8"))
from legal_data import pairs as _legal_pairs
for _en, _frt in _legal_pairs(): _fr.setdefault(re.sub(r"\s+", " ", _en).strip(), _frt)
_engine = open(f"{SP}/i18n/engine.js", encoding="utf-8").read().replace("__DICT__", json.dumps(_fr, ensure_ascii=False, sort_keys=True))
open(f"{SITE}/assets/i18n.js", "w", encoding="utf-8").write(_engine)
_v = _hl.sha1(_engine.encode()).hexdigest()[:10]
I18N_HEAD = """<script>try{var _l=localStorage.getItem('kp-lang')||((navigator.languages&&navigator.languages[0])||navigator.language||'').slice(0,2).toLowerCase();if(_l==='fr'){document.documentElement.lang='fr';document.documentElement.classList.add('i18n-wait');setTimeout(function(){document.documentElement.classList.remove('i18n-wait')},1500);}}catch(e){}</script>
<style>.i18n-wait body{opacity:0}</style>"""
I18N_JS = f'<script src="/assets/i18n.js?v={_v}"></script>'
LANG_SW = '<div class="lang" role="group" aria-label="Language"><button type="button" data-lang="fr" aria-pressed="false" lang="fr">FRA</button><span aria-hidden="true">|</span><button type="button" data-lang="en" aria-pressed="true" lang="en">ENG</button></div>'
head_links = head_links + "\n" + I18N_HEAD
EMBLEM = '<img src="assets/emblem.png" alt="" style="width: 30px; height: 30px; filter: invert(1)">'

def social_icons():
    return ('<span class="hidesm" style="display: flex; gap: 6px">'
            + "".join(f'<a class="soc" href="{SOCIAL[k]}" {EXT} aria-label="{k.capitalize() if k != "linkedin" else "LinkedIn"}">{ICON[k]}</a>' for k in ("instagram", "facebook", "linkedin"))
            + '</span>')

CHEV = '<svg class="chev" width="9" height="6" viewBox="0 0 9 6" fill="none" stroke="currentColor" stroke-width="1.3" aria-hidden="true"><path d="M1 1l3.5 3.5L8 1"/></svg>'

def nav_html(active, mobile_style):
    def cur(k): return ' aria-current="page"' if k == active else ""
    parts, mparts = [], []
    for item in NAV:
        if item[0] == "group":
            _, label, key, subs = item
            on = active in [s[2] for s in subs]
            links = "".join(f'<a href="{h}"{cur(k)}><span>{t}</span><small>{d}</small></a>' for h, t, k, d in subs)
            parts.append(f'          <div class="ndd"><button class="navi{" act" if on else ""}" type="button" aria-expanded="false" aria-haspopup="true" data-dd>{label}{CHEV}</button><div class="ddp" role="group" aria-label="{label}">{links}</div></div>')
            mparts.append(f'        <p class="mgrp">{label}</p>' + "".join(
                f'<a class="wide msub" href="{h}" data-act="close"{cur(k)} style="text-decoration: none; padding: 12px 0 12px 18px; font-size: 14px{"; color: var(--gold)" if k == active else ""}">{t}</a>' for h, t, k, d in subs))
        else:
            h, t, k = item
            parts.append(f'          <a class="navi{" act" if k == active else ""}" href="{h}"{cur(k)}>{t}</a>')
            mparts.append(f'        <a class="wide" href="{h}" data-act="close"{cur(k)} style="text-decoration: none; padding: 14px 0; font-size: 16px{"; color: var(--gold)" if k == active else ""}">{t}</a>')
    return "\n".join(parts), f'<nav id="mnav" hidden aria-label="Mobile" style="{mobile_style}">\n' + "\n".join(mparts) + '\n      </nav>'

def footer():
    explore = "".join(f'<li><a href="{h}" style="text-decoration: none">{t}</a></li>' for h, t in
                      [("about-us.html", "About us"), ("/press", "Press"), ("contact.html", "Contact"),
                       ("terms-and-conditions.html", "Terms &amp; conditions"), ("privacy-policy.html", "Privacy policy")])
    follow = "".join(f'<li><a href="{SOCIAL[k]}" {EXT} style="text-decoration: none">{n}</a></li>' for k, n in
                     [("instagram", "Instagram"), ("facebook", "Facebook"), ("linkedin", "LinkedIn")])
    return f"""<!-- FOOTER (black) -->
<footer class="on-dark" style="background: #000; color: #fff; padding: clamp(90px,9vw,150px) 0 36px">
  <div class="wrap">
    <div class="two" style="display: grid; grid-template-columns: minmax(0,1.4fr) repeat(3,minmax(0,1fr)); gap: 48px">
      <div>
        <div style="display: flex; align-items: center; gap: 16px">
          <img src="assets/emblem.png" alt="" style="width: 48px; height: 48px; filter: invert(1)">
          <span class="wide" style="font-size: 15px; line-height: 1.5">Kenny's<br>International</span>
        </div>
        <p class="gold" style="margin: 28px 0 0; font-size: 15px">Sharing the luxury of your life since 1993.</p>
      </div>
      <nav aria-label="Footer">
        <p class="cap gold" style="margin: 0 0 20px">Explore</p>
        <ul style="list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 12px; font-size: 15px; color: #BDBDBD">
          {explore}
        </ul>
      </nav>
      <div>
        <p class="cap gold" style="margin: 0 0 20px">Head office</p>
        <p style="margin: 0; font-size: 15px; line-height: 1.7; color: #BDBDBD">{ADDR_1}<br>{ADDR_2}<br><a href="{PHONE_HREF}" style="text-decoration: none">{PHONE}</a><br><a href="mailto:{EMAIL}" style="text-decoration: none; word-break: break-all">{EMAIL}</a></p>
      </div>
      <div>
        <p class="cap gold" style="margin: 0 0 20px">Follow</p>
        <ul style="list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 12px; font-size: 15px; color: #BDBDBD">
          {follow}
        </ul>
      </div>
    </div>
    <div style="margin-top: 80px; padding-top: 26px; border-top: 1px solid #2B2B2B; display: flex; justify-content: space-between; gap: 16px; flex-wrap: wrap; font-size: 13px; color: #8C8C8C">
      <span>© 2026 Kenny's Group. All rights reserved.</span>
      <span>Kinshasa, Lubumbashi, Kolwezi, Pointe-Noire</span>
    </div>
  </div>
</footer>"""

MENU_JS = """<script>(function(){
  var mnav=document.getElementById('mnav'), mbtn=document.querySelector('[data-act="menu"]');
  document.addEventListener('click',function(e){
    var b=e.target.closest('[data-act]'); if(!b) return;
    var a=b.getAttribute('data-act');
    if(a==='menu'){ var open=mnav.hidden; mnav.hidden=!open; mbtn.setAttribute('aria-expanded',open?'true':'false'); }
    else if(a==='close'){ mnav.hidden=true; mbtn.setAttribute('aria-expanded','false'); }
  });
  document.addEventListener('keydown',function(e){ if(e.key==='Escape' && mnav && !mnav.hidden){ mnav.hidden=true; mbtn.setAttribute('aria-expanded','false'); mbtn.focus(); } });
})();</script>""" + "\n" + """<script>(function(){
  var dds=[].slice.call(document.querySelectorAll('.ndd'));
  function close(except){ dds.forEach(function(d){ if(d!==except){ d.classList.remove('open'); d.querySelector('[data-dd]').setAttribute('aria-expanded','false'); } }); }
  dds.forEach(function(d){
    var b=d.querySelector('[data-dd]');
    b.addEventListener('click',function(e){ e.stopPropagation(); var o=!d.classList.contains('open'); close(d); d.classList.toggle('open',o); b.setAttribute('aria-expanded',o?'true':'false'); });
    d.addEventListener('mouseenter',function(){ b.setAttribute('aria-expanded','true'); });
    d.addEventListener('mouseleave',function(){ if(!d.classList.contains('open')) b.setAttribute('aria-expanded','false'); });
    d.addEventListener('focusout',function(e){ if(!d.contains(e.relatedTarget)){ d.classList.remove('open'); b.setAttribute('aria-expanded','false'); } });
  });
  document.addEventListener('click',function(){ close(); });
  document.addEventListener('keydown',function(e){ if(e.key==='Escape'){ var o=dds.filter(function(d){return d.classList.contains('open')})[0]; close(); if(o) o.querySelector('[data-dd]').focus(); } });
  var hd=document.querySelector('.htop,.ptop'), tk=0;
  function hs(){ tk=0; if(hd) hd.classList.toggle('scrolled', window.scrollY > hd.offsetHeight); }
  window.addEventListener('scroll',function(){ if(!tk) tk=requestAnimationFrame(hs); },{passive:true}); hs();
  [].slice.call(document.querySelectorAll('[data-copy]')).forEach(function(b){ b.addEventListener('click',function(){ var u=b.getAttribute('data-copy'), s=b.parentNode.querySelector('.copied'); (navigator.clipboard?navigator.clipboard.writeText(u):Promise.reject()).then(function(){ if(s){ s.textContent='Link copied'; setTimeout(function(){ s.textContent=''; },2000);} }).catch(function(){ prompt('Copy this link:',u); }); }); });
})();</script>"""

DD_JS = "<script>" + MENU_JS.split("\n<script>", 1)[1]

def sub_header(active):
    desk, mob = nav_html(active, "z-index: 20; background: #000; border-bottom: 1px solid var(--gold); color: #fff; padding: 16px 7% 26px; flex-direction: column; display: flex")
    return f"""<header class="ptop">
  <div style="display: flex; align-items: center; gap: 22px">
    <a href="index.html" aria-label="Kenny's International, home" style="display: flex; align-items: center; gap: 12px; text-decoration: none; color: #fff">
      {EMBLEM}
      <span class="cap" style="font-size: 11px; font-weight: 500">Kenny's International</span>
    </a>
    {social_icons()}
  </div>
  <div style="display: flex; align-items: center; gap: 24px">
    <nav class="navlist" aria-label="Main" style="display: flex">
{desk}
    </nav>
    {LANG_SW}
    <button class="mbtn" type="button" data-act="menu" aria-expanded="false" aria-controls="mnav" aria-label="Open menu">Menu</button>
  </div>
  {mob}
</header>"""

def page(fn, title, desc, body, active, extra_script=""):
    doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
{head_links}
<style>{style}{SHARED_CSS}{SUB_CSS}</style>
</head>
<body>
<div class="k" style="--gold: #C9A55C">

{sub_header(active)}

<main id="top">
{body}
</main>

{footer()}

</div>
{MENU_JS}
{extra_script}
{I18N_JS}
</body>
</html>
"""
    open(f"{SITE}/{fn}", "w", encoding="utf-8").write(doc)

def phead(crumb, kicker, title, intro, extra=""):
    return f"""<section class="phead on-dark" aria-labelledby="page-h">
  <div class="wrap">
    <p class="crumb"><a href="index.html">Home</a><span aria-hidden="true">/</span><span>{crumb}</span></p>
    <div class="two" style="display: grid; grid-template-columns: minmax(0,1.3fr) minmax(0,1fr); gap: 40px; align-items: end">
      <div>
        <p class="cap gold rev" style="margin: 0 0 22px">{kicker}</p>
        <h1 id="page-h" class="wide ptitle rev">{title}</h1>
      </div>
      <p class="rise" style="margin: 0; max-width: 460px; justify-self: end; font-size: 16px; line-height: 1.8; color: #BDBDBD; font-weight: 300">{intro}</p>
    </div>{extra}
  </div>
</section>"""

def sliced(img, label, ratio="21/9", pos="50% 50%"):
    bands = "\n".join(f'      <div class="band" style="top: {i * 100 / 6:.4f}%; height: 16.7167%"><div class="bi"><img src="{img}" alt="" style="top: -{i * 100}%; object-position: {pos}"></div></div>' for i in range(6))
    return f'<div class="sband" role="img" aria-label="{label}" style="position: relative; aspect-ratio: {ratio}; overflow: hidden">\n{bands}\n    </div>'

def closing(stmt, btn_href, btn_text, cities=False):
    c = '\n    <p class="cities rise">Kinshasa · Lubumbashi · Kolwezi · Pointe-Noire</p>' if cities else ""
    return f"""<section class="closing on-dark" aria-label="{html.escape(btn_text)}">
  <div class="wrap">
    <img src="assets/emblem.png" alt="" style="width: 54px; height: 54px; filter: invert(1); margin: 0 auto 40px">
    <p class="wide stmt rev">{stmt}</p>{c}
    <div class="rise" style="margin-top: 48px"><a class="btn" href="{btn_href}">{btn_text} {BTN_ARROW}</a></div>
  </div>
</section>"""

def sechead(kicker, title, hid, right=""):
    return f"""    <div class="two" style="display: grid; grid-template-columns: minmax(0,1fr) minmax(0,1fr); gap: 40px; align-items: end; margin-bottom: clamp(56px,6vw,96px)">
      <div>
        <p class="cap gold rev" style="margin: 0 0 18px">{kicker}</p>
        <h2 id="{hid}" class="wide h2 rev">{title}</h2>
      </div>
      {right}
    </div>"""

# ================================================================== Distribution brands
SPRITE_ROWS = 21  # logos-kennys.png: the original 20 houses + Piaget (row 20)
def lgk_pos(i): return f"{i * 100 / (SPRITE_ROWS - 1):.4f}%"
DIST = [(n, i) for i, n in enumerate(DISTRIBUTION)]
DIST.insert(4, ("Piaget", 20))
def dtile(n, i): return f'      <li class="tile"><span class="lg lgk" style="background-position: 0 {lgk_pos(i)}" aria-hidden="true"></span><span class="nm cap">{n}</span></li>'
dist_tiles = "\n".join(dtile(n, i) for n, i in DIST)
frag = "\n".join(f'      <li><span>{i+1:02d}</span>{html.escape(n)}</li>' for i, n in enumerate(FRAGRANCE))
page("distribution-brands.html", "Distribution brands | Kenny's International",
     "The watch, jewellery, fashion, fragrance and beauty houses available in every Kenny's store in Kinshasa, Lubumbashi, Kolwezi and Pointe-Noire.",
     phead("Distribution brands", "Distribution brands", "Kenny's Stores",
           "The world's leading watch, jewellery and fashion houses, presented together under one roof since 1993.") + f"""

<section class="sec" aria-labelledby="houses-h" style="background: #fff">
  <div class="wrap">
{sechead("Watches, jewellery and fashion", "The houses", "houses-h", f'<p class="count rise" style="justify-self: end">{len(DIST)} houses</p>')}
    <ul class="g5" style="list-style: none; margin: 0; padding: 0; display: grid; grid-template-columns: repeat(5,minmax(0,1fr)); border-top: 1px solid #E8E8E8; border-left: 1px solid #E8E8E8">
{dist_tiles}
    </ul>
  </div>
</section>

<section class="sec" aria-labelledby="frag-h" style="background: #FAF9F6">
  <div class="wrap">
{sechead("Also in our stores", "Fragrance and beauty", "frag-h", f'<p class="count rise" style="justify-self: end">{len(FRAGRANCE)} brands</p>')}
    <ul class="fraglist rise">
{frag}
    </ul>
  </div>
</section>

""" + closing("All these brands are available in every Kenny's store.", "contact.html", "Contact us", cities=True), "dist")

# ================================================================== Franchise retail
PLUS = '<svg width="12" height="12" viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="1.3" aria-hidden="true"><path d="M6 0v12M0 6h12"></path></svg>'
def spos(f):
    cls, pos = f["sprite"]
    if cls == "lgk": pos = lgk_pos(round(float(pos.rstrip("%")) * 19 / 100))
    return cls, pos

def ftile(f, href=None):
    cls, pos = spos(f)
    badge = '<span class="badge cap">New store</span>' if f.get("new") else ""
    inner = f'{badge}<span class="vw" aria-hidden="true">{PLUS}</span><span class="lg {cls}" style="background-position: 0 {pos}" aria-hidden="true"></span><span class="nm cap">{f["name"]}</span>'
    if href:
        return f'      <li><a class="tile" href="{href}" aria-label="{html.escape(f["name"])}, store details">{inner}</a></li>'
    return f'      <li><button class="tile" type="button" data-brand="{f["slug"]}" aria-haspopup="dialog" aria-label="{html.escape(f["name"])}, store details">{inner}</button></li>'

fr_tiles = "\n".join(ftile(f) for f in FRANCHISES)
data = {f["slug"]: dict(name=f["name"], cat=f["cat"], blurb=f["blurb"], new=bool(f.get("new")), cls=spos(f)[0], pos=spos(f)[1], locs=f["locs"]) for f in FRANCHISES}
fr_script = """<script>(function(){
  var DATA=""" + json.dumps(data, ensure_ascii=False) + """;
  var dlg=document.getElementById('fcard'), path=location.pathname+location.search;
  function esc(s){return String(s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
  function maps(n,l){return 'https://www.google.com/maps/search/?api=1&query='+encodeURIComponent(n+', '+l.addr)+'&query_place_id='+l.pid}
  function open(slug){
    var b=DATA[slug]; if(!b) return;
    var lg=document.getElementById('fc-lg'); lg.className='lg '+b.cls; lg.style.backgroundPosition='0 '+b.pos;
    document.getElementById('fc-cat').textContent=b.cat+(b.new?' · New store':'');
    document.getElementById('fc-name').textContent=b.name;
    document.getElementById('fc-blurb').textContent=b.blurb;
    var many=b.locs.length>1;
    document.getElementById('fc-locs').innerHTML=b.locs.map(function(l,i){
      var h='<table class="fc-hours"><tbody>'+l.hours.map(function(r){return '<tr><th scope="row">'+esc(r[0])+'</th><td>'+esc(r[1])+'</td></tr>'}).join('')+'</tbody></table>';
      var title=many?('Store '+(i+1)+(l.label?' · '+l.label:'')):(l.label||'The store');
      return '<div class="fc-loc"><h3>'+esc(title)+'</h3><dl class="fc-dl">'
        +'<dt>Address</dt><dd>'+esc(l.addr)+'</dd>'
        +(l.tel?'<dt>Phone</dt><dd><a href="tel:'+l.tel.replace(/\\s/g,'')+'">'+esc(l.tel)+'</a></dd>':'')
        +'<dt>Opening hours</dt><dd>'+h+'</dd></dl>'
        +'<a class="lnk" href="'+maps(b.name,l)+'" target="_blank" rel="noopener">Directions <svg height="10" viewBox="0 0 46 10" preserveAspectRatio="none" fill="none" stroke="currentColor" stroke-width="1" aria-hidden="true"><path d="M0 5h45M40 1l5 4-5 4"></path></svg></a></div>';
    }).join('');
    if(!dlg.open) dlg.showModal();
    dlg.scrollTop=0;
    try{history.replaceState(null,'','#'+slug)}catch(e){}
  }
  function close(){ if(dlg.open) dlg.close(); }
  dlg.addEventListener('close',function(){ try{history.replaceState(null,'',path)}catch(e){} });
  dlg.addEventListener('click',function(e){ if(e.target===dlg || e.target.closest('[data-fc="close"]')) close(); });
  document.addEventListener('click',function(e){ var t=e.target.closest('[data-brand]'); if(t) open(t.getAttribute('data-brand')); });
  var h=location.hash.slice(1); if(h && DATA[h]) open(h);
})();</script>"""
page("franchise-retail.html", "Franchise retail | Kenny's International",
     "Puma, Lacoste, Calvin Klein, Tommy Hilfiger, Boggi Milano and more: the brand stores run by Kenny's Group in Kinshasa, with addresses and opening hours.",
     phead("Franchise retail", "Franchise retail", "Our own stores",
           "International brands with their own stores, run by Kenny's Group. Select a brand to see its address, phone number and opening hours.") + f"""

<section class="sec" aria-labelledby="fr-h" style="background: #fff">
  <div class="wrap">
{sechead("Kinshasa", "The brands", "fr-h", f'<p class="count rise" style="justify-self: end">{len(FRANCHISES)} brands</p>')}
    <ul class="g4" style="list-style: none; margin: 0; padding: 0; display: grid; grid-template-columns: repeat(4,minmax(0,1fr)); border-top: 1px solid #E8E8E8; border-left: 1px solid #E8E8E8">
{fr_tiles}
    </ul>
  </div>
</section>

""" + closing("Sharing the luxury of your life since 1993.", "contact.html", "Contact us") + """

<dialog class="fcard" id="fcard" aria-labelledby="fc-name">
  <button class="fc-x" type="button" data-fc="close" aria-label="Close"><svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4" aria-hidden="true"><path d="M1 1l14 14M15 1L1 15"></path></svg></button>
  <div class="fc-logo"><span class="lg" id="fc-lg" aria-hidden="true"></span></div>
  <div class="fc-body">
    <p class="cap gold" id="fc-cat" style="margin: 0"></p>
    <h2 class="wide fc-name" id="fc-name"></h2>
    <p class="fc-blurb" id="fc-blurb"></p>
    <div id="fc-locs"></div>
  </div>
</dialog>""", "fran", fr_script)

# ================================================================== About us
BELIEF_ICONS = dict(
  integrity='<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="1.4" aria-hidden="true"><path d="M24 4l16 6v12c0 10-7 18-16 22C15 40 8 32 8 22V10z"/><path d="M17 24l5 5 9-10"/></svg>',
  diversity='<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="1.4" aria-hidden="true"><circle cx="24" cy="14" r="5"/><circle cx="11" cy="19" r="4"/><circle cx="37" cy="19" r="4"/><path d="M15 40v-6a9 9 0 0 1 18 0v6M4 38v-4a7 7 0 0 1 10-6.3M44 38v-4a7 7 0 0 0-10-6.3"/></svg>',
  quality='<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="1.4" aria-hidden="true"><circle cx="24" cy="19" r="13"/><circle cx="24" cy="19" r="7"/><path d="M16 29l-4 15 7-4 5 6 3-11M32 29l4 15-7-4"/></svg>',
  excellence='<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="1.4" aria-hidden="true"><path d="M24 5l5.6 12.2 13.4 1.4-10 9 2.8 13.1L24 34l-11.8 6.7L15 27.6l-10-9 13.4-1.4z"/></svg>')
BELIEFS = [("integrity", "Integrity", "Honest, lasting relationships with our clients, our teams and the houses we represent."),
           ("diversity", "Diversity", "Teams that bring together many cultures, languages and talents."),
           ("quality", "Quality", "Authentic products, carefully selected and presented with care."),
           ("excellence", "Excellence", "A standard of service worthy of the brands in our stores.")]

TIMELINE = [
  ("1993", True, ["Kenny Rawtani begins his journey in Congo-Brazzaville, then founds Kenny's International in Kinshasa"]),
  ("2011", False, ["Kenny's opens in Brazzaville"]),
  ("2013", False, ["Kenny's opens in Pointe-Noire"]),
  ("2014", False, ["Kenny's opens in Mali"]),
  ("2015", False, ["Kenny's opens in Malabo"]),
  ("2017", False, ["Kenny's Watchmaking & Jewellery opens", "Mango opens in Kinshasa"]),
  ("2018", False, ["Kenny's opens in Abidjan"]),
  ("2019", False, ["Kenny's opens in Kinshasa", "Kenny's opens in Burkina Faso", "Etam, Maison 123 and Jennyfer open in Kinshasa"]),
  ("2020", False, ["Celio*, Tommy Hilfiger and Calvin Klein open in Kinshasa"]),
  ("2021", False, ["Kyra opens in Kinshasa", "Mango and Celio* open in Limete"]),
  ("2022", False, ["Montblanc, Lacoste, Puma and Paul &amp; Shark open in Kinshasa", "Jennyfer opens in Limete", "Paul &amp; Shark opens in Abidjan", "Mango and Kyra open in Brazzaville"]),
  ("2023", False, ["Kenny's opens in Kolwezi", "Patchi, Aldo and Okaïdi open in Kinshasa"]),
  ("2026", True, ["Boggi Milano opens its own Kenny's Group store in Kinshasa"]),
]
tl_items = "\n".join(
    f'      <li{" class=\"key\"" if key else ""}><p class="wide yr{" gold" if key else ""}">{y}</p><ul>' + "".join(f"<li>{e}</li>" for e in evs) + "</ul></li>"
    for y, key, evs in TIMELINE)
cities = [("Kinshasa", "DR Congo"), ("Lubumbashi", "DR Congo"), ("Kolwezi", "DR Congo"), ("Pointe-Noire", "Congo")]
about_body = phead("About us", "About us", "Who we are",
    "Kenny's Group has established itself as a leading name in fashion and lifestyle retail, serving a large customer base across Africa. With a portfolio of more than 70 brands, the group has become a major player in the industry, with over 2,000 staff members from many cultures.",
    extra="""
    <dl class="stats rise">
      <div><dt>Since</dt><dd class="wide gold">1993</dd></div>
      <div><dt>Brands</dt><dd class="wide gold">70+</dd></div>
      <div><dt>Staff members</dt><dd class="wide gold">2,000+</dd></div>
      <div><dt>Cities</dt><dd class="wide gold">4</dd></div>
    </dl>""") + f"""

<section class="sec" aria-labelledby="mission-h" style="background: #fff">
  <div class="wrap two" style="display: grid; grid-template-columns: minmax(0,1fr) minmax(0,1.1fr); gap: clamp(48px,7vw,140px); align-items: center">
    {sliced("assets/about-storefront.jpg", "The Kenny's flagship store in Kinshasa", "5/4")}
    <div>
      <p class="cap gold rev" style="margin: 0 0 18px">Our mission</p>
      <h2 id="mission-h" class="wide h2 rev">Inspiring confidence</h2>
      <p class="body rise" style="margin: 30px 0 0; max-width: 520px">Our mission is to inspire self-expression and confidence by bringing the world's leading fashion, watch and jewellery houses to our clients.</p>
      <p class="body rise" style="margin: 18px 0 0; max-width: 520px">We believe everyone deserves to feel good about the way they look. We are committed to offering authentic, high-quality products and a level of service worthy of the brands we represent.</p>
    </div>
  </div>
</section>

<section class="sec on-dark" aria-labelledby="beliefs-h" style="background: #000; color: #fff">
  <div class="wrap">
{sechead("What guides us", "Our beliefs", "beliefs-h")}
    <ul class="beliefs">
""" + "\n".join(f'      <li class="rise{" r2" if i % 2 else ""}">{BELIEF_ICONS[k]}<h3 class="wide">{t}</h3><p>{d}</p></li>' for i, (k, t, d) in enumerate(BELIEFS)) + f"""
    </ul>
  </div>
</section>

<section class="sec" aria-labelledby="began-h" style="background: #fff">
  <div class="wrap">
    <div class="two" style="display: grid; grid-template-columns: minmax(0,1fr) minmax(0,1.1fr); gap: clamp(48px,7vw,140px); align-items: start">
      <div>
        <p class="cap gold rev" style="margin: 0 0 18px">Since 1993</p>
        <h2 id="began-h" class="wide h2 rev">How it all began</h2>
        <p class="rise" style="margin: 30px 0 0; max-width: 480px; font-size: clamp(18px,1.5vw,22px); line-height: 1.6; color: #1A1A1A">Kenny embarked on his journey in 1993, armed with steadfast determination and a modest store.</p>
      </div>
      <div>
        <p class="body rise" style="margin: 0">Kenny's Group is a well-established lifestyle retail company that has operated since 1993. Its portfolio of more than 50 international franchise concepts spans several African countries, with stores offering leading fashion and accessory brands alongside beauty and cosmetic products.</p>
        <p class="body rise" style="margin: 18px 0 0">The group has become a one-stop destination for fashion enthusiasts, with a loyal customer base. Its commitment to quality products and service has made it a significant regional employer.</p>
      </div>
    </div>
    <div class="tl-head">
      <p class="cap gold" id="tl-h" style="margin: 0">Our journey</p>
      <div class="tl-ctrl">
        <button class="tl-btn" type="button" data-tl="-1" aria-label="Earlier years" aria-controls="tl"><svg width="22" height="12" viewBox="0 0 22 12" fill="none" stroke="currentColor" stroke-width="1.4" aria-hidden="true"><path d="M22 6H1M6 1L1 6l5 5"></path></svg></button>
        <button class="tl-btn" type="button" data-tl="1" aria-label="Later years" aria-controls="tl">{BTN_ARROW}</button>
      </div>
    </div>
    <ol class="tl" id="tl" aria-labelledby="tl-h" tabindex="0">
{tl_items}
    </ol>
  </div>
</section>

<section class="founder on-dark" aria-labelledby="founder-h">
  <div class="wrap">
    <div class="txt">
      <p class="cap gold rev" style="margin: 0 0 18px">The founder</p>
      <h2 id="founder-h" class="wide h2 rev">Mr Kenny Rawtani</h2>
      <p class="rise" style="margin: 18px 0 0; font-size: 13px; letter-spacing: .2em; text-transform: uppercase; color: #fff">Founder and Chairman of Kenny's Group</p>
      <p class="body rise" style="margin: 30px 0 0; max-width: 520px">With more than 30 years of experience in African markets, Kenny Rawtani began his career in Congo-Brazzaville in 1993 before settling in Kinshasa, where he founded Kenny's International.</p>
      <p class="body rise" style="margin: 18px 0 0; max-width: 520px">The company started with high-end menswear and ready-to-wear, led by its own bespoke tailoring brand, Kenny's. It has since grown into a leading franchise developer across Africa, with a portfolio of top international brands.</p>
      <img class="sig rise" src="assets/kenny-signature.png" alt="Kenny Rawtani's signature" width="1068" height="146">
      <div class="flinks rise">
        {lnk(KENNY_SITE, "Know more", ext=True)}
        <a class="sq" href="{KENNY_LI}" {EXT} aria-label="Kenny Rawtani on LinkedIn">{ICON["linkedin"].replace('width="13" height="13"', 'width="16" height="16"')}</a>
      </div>
    </div>
    <div class="pic rise r2"><img src="assets/kenny-rawtani.webp" alt="Portrait of Kenny Rawtani, Founder and Chairman of Kenny's Group" width="627" height="1000" loading="lazy"></div>
  </div>
</section>

<section class="sec where" aria-labelledby="where-h">
  <div class="wrap">
    <div>
      <p class="cap gold rev" style="margin: 0 0 18px">Where we are</p>
      <h2 id="where-h" class="wide h2 rev">Central Africa</h2>
      <p class="body rise" style="margin: 30px 0 0; max-width: 460px">Our stores are in four cities across the Democratic Republic of the Congo and the Republic of the Congo.</p>
      <ul class="clist rise">
""" + "\n".join(f'        <li><span class="wide c">{c}</span><span class="n">{n}</span></li>' for c, n in cities) + f"""
      </ul>
    </div>
    <div class="rise r2">{MAP_SVG}</div>
  </div>
</section>

<section class="closing on-dark" aria-labelledby="social-h">
  <div class="wrap">
    <img src="assets/emblem.png" alt="" style="width: 54px; height: 54px; filter: invert(1); margin: 0 auto 40px">
    <h2 id="social-h" class="wide stmt rev" style="font-weight: 400">We are social</h2>
    <p class="body rise" style="margin: 22px auto 0; max-width: 520px">Follow Kenny's International for new arrivals, store openings and events.</p>
    <div class="social rise">
""" + "\n".join(f'      <a href="{SOCIAL[k]}" {EXT}>{ICON[k]}{n}</a>' for k, n in [("linkedin", "LinkedIn"), ("facebook", "Facebook"), ("instagram", "Instagram")]) + """
    </div>
  </div>
</section>"""
about_js = """<script>(function(){
  var tl=document.getElementById('tl'), btns=[].slice.call(document.querySelectorAll('[data-tl]'));
  function step(){ var li=tl.querySelector('li'); return li ? li.getBoundingClientRect().width : 300; }
  function upd(){ var max=tl.scrollWidth-tl.clientWidth-2; btns[0].disabled=tl.scrollLeft<=2; btns[1].disabled=tl.scrollLeft>=max; }
  btns.forEach(function(b){ b.addEventListener('click',function(){ tl.scrollBy({left:step()*+b.getAttribute('data-tl'),behavior:'smooth'}); }); });
  tl.addEventListener('scroll',upd,{passive:true}); window.addEventListener('resize',upd); upd();
})();</script>"""
page("about-us.html", "About us | Kenny's International",
     "Kenny's Group: fashion and lifestyle retail since 1993. Our mission, our beliefs, our history and our founder, Kenny Rawtani.",
     about_body, "about", about_js)

# ================================================================== K-Galerie
kg_stores = ["Boggi Milano", "Dolce &amp; Gabbana", "Emporio Armani", "Pal Zileri", "Paul &amp; Shark", "Adidas",
             "Mango", "Okaïdi", "Kiko Milano", "Kyra", "Samsonite", "Tumi"]
kg_body = phead("K-Galerie", "Pointe-Noire, Congo", "K-Galerie",
    "Pointe-Noire's new landmark, dedicated entirely to Kenny's Group stores, with a rooftop, a lounge bar and padel courts.") + f"""

<section class="sec" aria-labelledby="kg-h" style="background: #fff">
  <div class="wrap">
    {sliced("assets/kgalerie-hero.jpg", "K-Galerie seen from above, with its rooftop padel courts", "21/9", "50% 45%")}
    <div class="two" style="display: grid; grid-template-columns: minmax(0,1fr) minmax(0,1fr); gap: clamp(48px,7vw,140px); margin-top: clamp(56px,6vw,96px); align-items: start">
      <div>
        <img class="rise" src="assets/kgalerie-logo.png" alt="K-Galerie" style="width: 110px; height: auto; margin-bottom: 36px">
        <p class="cap gold rev" style="margin: 0 0 18px">The new landmark</p>
        <h2 id="kg-h" class="wide h2 rev">One address, every Kenny's store</h2>
      </div>
      <div>
        <p class="body rise" style="margin: 0">A shopping destination fully managed by Kenny's Group, where every store is one of ours. Fashion, accessories, beauty and travel come together under one roof in the heart of Pointe-Noire.</p>
      </div>
    </div>
    <ul class="feat" style="margin-top: clamp(64px,6vw,100px)">
      <li class="rise"><span class="num">01</span><h3 class="wide">Rooftop</h3></li>
      <li class="rise r2"><span class="num">02</span><h3 class="wide">Lounge bar</h3></li>
      <li class="rise r3"><span class="num">03</span><h3 class="wide">Padel courts</h3></li>
    </ul>
  </div>
</section>

<section class="sec on-dark" aria-labelledby="inside-h" style="background: #000; color: #fff">
  <div class="wrap">
{sechead("Inside K-Galerie", "The stores", "inside-h", '<p class="count rise" style="justify-self: end">' + str(len(kg_stores)) + ' stores</p>')}
    <ul class="wide stores rise">
""" + "\n".join(f"      <li>{s}</li>" for s in kg_stores) + f"""
    </ul>
  </div>
</section>

<section class="sec" aria-labelledby="visit-h" style="background: #fff">
  <div class="wrap">
{sechead("Plan your visit", "Visit K-Galerie", "visit-h")}
    <div class="visit">
      <div class="rise"><h3>Location</h3><p>K-Galerie<br>Pointe-Noire, Republic of the Congo</p><div style="margin-top: 14px">{lnk(KG_MAPS, "Directions", ext=True)}</div></div>
      <div class="rise r2"><h3>Opening hours</h3><table class="hrs"><tbody><tr><th scope="row">Mon – Sat</th><td>09:00 – 21:00</td></tr><tr><th scope="row">Sunday</th><td>09:00 – 15:00</td></tr></tbody></table></div>
      <div class="rise r3"><h3>Questions</h3><p>Our customer service team is happy to help.</p><div style="margin-top: 14px">{lnk("contact.html", "Contact us")}</div></div>
    </div>
  </div>
</section>"""
page("k-galerie.html", "K-Galerie, Pointe-Noire | Kenny's International",
     "K-Galerie, Pointe-Noire's new shopping landmark, dedicated entirely to Kenny's Group stores, with a rooftop, a lounge bar and padel courts.",
     kg_body, "kg")

# ================================================================== Contact
CHECK = '<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="1.4" aria-hidden="true"><circle cx="24" cy="24" r="21"/><path d="M15 24.5l6 6 12-13"/></svg>'
topics = ["General enquiry", "Products and brands", "Our stores", "Partnerships and franchises", "Press", "Careers"]
contact_body = phead("Contact", "Contact", "Get in touch",
    "A question about a brand, a store or a partnership? Send us a message and our customer service team will reply.") + f"""

<section class="sec" aria-label="Contact details and form" style="background: #fff">
  <div class="wrap cgrid">
    <div class="cinfo">
      <div class="rise">
        <h3>Head office</h3>
        <p>{ADDR_1}</p>
        <p class="sm">{ADDR_2}</p>
        <div style="margin-top: 10px">{lnk(HQ_MAPS, "Directions", ext=True)}</div>
      </div>
      <div class="rise">
        <h3>Phone</h3>
        <p><a class="big" href="{PHONE_HREF}">{PHONE}</a></p>
      </div>
      <div class="rise">
        <h3>Email</h3>
        <p><a class="big" href="mailto:{EMAIL}" style="word-break: break-all">{EMAIL}</a></p>
      </div>
      <div class="rise">
        <h3>Flagship store hours</h3>
        <table class="hrs"><tbody><tr><th scope="row">Mon – Sat</th><td>08:00 – 20:00</td></tr><tr><th scope="row">Sunday</th><td>09:30 – 20:00</td></tr></tbody></table>
      </div>
      <div class="rise">
        <h3>Follow us</h3>
        <div class="socrow">""" + "".join(f'<a href="{SOCIAL[k]}" {EXT} aria-label="{n}">{ICON16[k]}</a>' for k, n in [("instagram", "Instagram"), ("facebook", "Facebook"), ("linkedin", "LinkedIn")]) + f"""</div>
      </div>
    </div>

    <div class="cform rise r2" id="form">
      <form name="contact" method="POST" action="/contact?sent=1#form" data-netlify="true" netlify-honeypot="company-website" id="cform" novalidate>
        <input type="hidden" name="form-name" value="contact">
        <input type="hidden" name="subject" value="New message from the Kenny's International website (%{{submissionId}})">
        <p class="hp" aria-hidden="true"><label>Leave this field empty <input name="company-website" tabindex="-1" autocomplete="off"></label></p>
        <h2 class="wide" style="margin: 0 0 12px; font-size: clamp(20px,1.8vw,28px)">Send a message</h2>
        <p class="fnote">Fields marked * are required.</p>
        <div class="frow">
          <label class="fld"><span>Full name *</span><input name="name" type="text" autocomplete="name" required></label>
          <label class="fld"><span>Email *</span><input name="email" type="email" autocomplete="email" required></label>
        </div>
        <div class="frow">
          <label class="fld"><span>Phone <i>(optional)</i></span><input name="phone" type="tel" autocomplete="tel" inputmode="tel"></label>
          <label class="fld"><span>Topic</span><select name="topic">""" + "".join(f'<option value="{t}">{t}</option>' for t in topics) + """</select></label>
        </div>
        <label class="fld"><span>Message *</span><textarea name="message" required rows="6"></textarea></label>
        <button class="btn solid" type="submit" id="fsend">Send message """ + BTN_ARROW + """</button>
        <p class="fmsg" id="fmsg" role="status" aria-live="polite"></p>
      </form>
      <div class="fdone" id="fdone" hidden tabindex="-1">
        """ + CHECK + """
        <h2 class="wide">Thank you</h2>
        <p>Your message has been sent to our customer service team. We will get back to you as soon as possible.</p>
        <button class="btn" type="button" id="fagain" style="margin-top: 30px">Send another message</button>
      </div>
    </div>
  </div>
</section>

<section class="cmap" aria-label="Map of the Kenny's head office in Kinshasa">
  <iframe src=\"""" + HQ_EMBED + """\" title="Map: Kenny's, 124 Boulevard du 30 Juin, Kinshasa" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
  <div class="pinbox"><p class="cap gold" style="margin: 0 0 10px">Kenny's flagship</p><p style="margin: 0; font-size: 15px; line-height: 1.6">""" + ADDR_1 + """</p></div>
</section>"""
contact_js = """<script>(function(){
  var f=document.getElementById('cform'), done=document.getElementById('fdone'), msg=document.getElementById('fmsg'), send=document.getElementById('fsend');
  function showDone(){ f.hidden=true; done.hidden=false; done.focus(); }
  if(/[?&]sent=1/.test(location.search)) showDone();
  f.addEventListener('submit',function(e){
    e.preventDefault(); msg.textContent=''; msg.className='fmsg';
    if(!f.checkValidity()){
      var bad=f.querySelector(':invalid'); msg.textContent='Please fill in your name, a valid email address and your message.'; msg.className='fmsg err'; if(bad) bad.focus(); return;
    }
    send.disabled=true; send.style.opacity='.6';
    fetch('/',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:new URLSearchParams(new FormData(f)).toString()})
      .then(function(r){ if(!r.ok) throw new Error(r.status); f.reset(); showDone(); })
      .catch(function(){ msg.innerHTML='Sorry, your message could not be sent. Please try again or email us at <a href="mailto:""" + EMAIL + """">""" + EMAIL + """</a>.'; msg.className='fmsg err'; })
      .then(function(){ send.disabled=false; send.style.opacity=''; });
  });
  document.getElementById('fagain').addEventListener('click',function(){ done.hidden=true; f.hidden=false; f.querySelector('input[name=name]').focus(); });
})();</script>"""
page("contact.html", "Contact | Kenny's International",
     "Contact Kenny's International: head office at 124 Boulevard du 30 Juin, Gombe, Kinshasa. Phone " + PHONE + ", email " + EMAIL + ".",
     contact_body, "contact", contact_js)

# ================================================================== Legal pages
import legal_data as LD
LEGAL_CSS = """<style>
.lgl{display:grid;grid-template-columns:minmax(0,260px) minmax(0,760px);gap:clamp(48px,7vw,120px);align-items:start}
.lgl-toc{position:sticky;top:110px}
.lgl-toc p{margin:0 0 22px}
.lgl-toc ol{list-style:none;margin:0;padding:0;counter-reset:t;display:flex;flex-direction:column;gap:12px}
.lgl-toc li{counter-increment:t;display:flex;gap:14px;font-size:14px;line-height:1.5}
.lgl-toc li::before{content:counter(t,decimal-leading-zero);font-size:11px;letter-spacing:.12em;font-weight:600;color:var(--gold-ink);padding-top:2px;min-width:20px}
.lgl-toc a{color:#6A6A6A;text-decoration:none;transition:color .3s}
.lgl-toc a:hover{color:#000}
.lgl-sec{padding:0 0 clamp(44px,4vw,64px);margin:0 0 clamp(44px,4vw,64px);border-bottom:1px solid #E8E8E8;scroll-margin-top:110px}
.lgl-sec:last-child{border-bottom:0;margin-bottom:0;padding-bottom:0}
.lgl-sec h2{display:flex;gap:18px;align-items:baseline;margin:0 0 26px;font-size:clamp(16px,1.35vw,21px);line-height:1.4;color:#000}
.lgl-sec h2 .n{font-family:"Jost",sans-serif;font-size:12px;letter-spacing:.14em;font-weight:600;color:var(--gold-ink)}
.lgl-sec p,.lgl-sec li{font-size:17px;line-height:1.85;color:#3A3A3A;font-weight:300}
.lgl-sec p{margin:0 0 1.1em}
.lgl-sec p:last-child{margin-bottom:0}
.lgl-sec ul{list-style:none;margin:0 0 1.2em;padding:0}
.lgl-sec ul:last-child{margin-bottom:0}
.lgl-sec li{position:relative;padding-left:30px;margin:0 0 .6em}
.lgl-sec li::before{content:"";position:absolute;left:4px;top:.75em;width:7px;height:7px;transform:rotate(45deg);background:var(--gold)}
.lgl-ct{margin:22px 0 0;padding:28px 30px;background:#F6F4EF;display:grid;gap:18px}
.lgl-ct div{display:grid;grid-template-columns:130px minmax(0,1fr);gap:16px;font-size:16px;line-height:1.6}
.lgl-ct dt{font-size:11px;letter-spacing:.24em;text-transform:uppercase;font-weight:600;color:var(--gold-ink);padding-top:4px}
.lgl-ct dd{margin:0;color:#000;word-break:break-word}
.lgl-ct a{color:inherit;text-decoration:none;border-bottom:1px solid var(--gold)}
.upd{margin:clamp(40px,4vw,64px) 0 0;display:flex;gap:12px;align-items:center;color:#BDBDBD}
@media (max-width:900px){.lgl{grid-template-columns:minmax(0,1fr)}.lgl-toc{position:static;padding-bottom:40px;border-bottom:1px solid #E8E8E8}}
@media (max-width:600px){.lgl-ct{padding:22px 20px}.lgl-ct div{grid-template-columns:minmax(0,1fr);gap:4px}.lgl-sec p,.lgl-sec li{font-size:16px}}
</style>"""

def _e(s): return html.escape(s, quote=False)

def legal_page(d):
    toc, secs = [], []
    for i, ((h_en, _), blocks) in enumerate(d["sections"], 1):
        sid = f"s{i}"
        toc.append(f'<li><a href="#{sid}">{_e(h_en)}</a></li>')
        out = []
        for b in blocks:
            if b[0] == "p":
                out.append(f"<p>{_e(b[1])}</p>")
            elif b[0] == "ul":
                out.append("<ul>" + "".join(f"<li>{_e(en)}</li>" for en, _ in b[1]) + "</ul>")
            elif b[0] == "link":
                out.append(f'<div style="margin-top: 22px">{lnk(b[1], b[2])}</div>')
            elif b[0] == "contact":
                out.append(f"""<dl class="lgl-ct">
          <div><dt>Head office</dt><dd>{ADDR_1}</dd></div>
          <div><dt>Email</dt><dd><a href="mailto:{EMAIL}">{EMAIL}</a></dd></div>
          <div><dt>Phone</dt><dd><a href="{PHONE_HREF}">{PHONE}</a></dd></div>
        </dl>""")
        secs.append(f'      <section class="lgl-sec" id="{sid}" aria-labelledby="{sid}-h">\n        <h2 class="wide" id="{sid}-h"><span class="n">{i:02d}</span><span>{_e(h_en)}</span></h2>\n        ' + "\n        ".join(out) + "\n      </section>")
    upd = f'\n    <p class="upd cap"><span>Last updated</span><span aria-hidden="true">·</span><span>{LD.UPDATED}</span></p>'
    body = LEGAL_CSS + "\n" + phead(_e(d["crumb"][0]), "Legal", _e(d["title"][0]), _e(d["intro"][0]), upd) + f"""

<section class="sec" style="background: #fff">
  <div class="wrap lgl">
    <nav class="lgl-toc" aria-label="On this page">
      <p class="cap gold">On this page</p>
      <ol>
        {"".join(toc)}
      </ol>
    </nav>
    <div>
{chr(10).join(secs)}
    </div>
  </div>
</section>"""
    page(d["file"], html.escape(d["meta_title"][0], quote=False), html.escape(d["desc"][0]), body, "legal")

legal_page(LD.TERMS)
legal_page(LD.PRIVACY)

# ================================================================== Homepage
idx = base.replace("</style>", SHARED_CSS + "</style>", 1)

# hero header nav + mobile nav
desk, mob = nav_html("home", "position: absolute; top: 100%; left: 0; right: 0; z-index: 20; background: rgba(0,0,0,.92); color: #fff; padding: 16px 7% 26px; display: flex; flex-direction: column")
idx = re.sub(r'(<nav class="navlist" aria-label="Main" style=")[^"]*(">).*?(</nav>)', lambda m: m.group(1) + "display: flex" + m.group(2) + "\n" + desk + "\n        " + m.group(3), idx, count=1, flags=re.S)
idx = re.sub(r'<nav id="mnav" hidden.*?</nav>', lambda m: mob, idx, count=1, flags=re.S)
idx = re.sub(r'<span class="hidesm" style="display: flex; gap: 6px">.*?</span>\n', lambda m: social_icons() + "\n", idx, count=1, flags=re.S)

# hero slide buttons
for old, new in [('<a class="more" href="#houses" style="margin-top: 26px">Explore the houses</a>', '<a class="more" href="distribution-brands.html" style="margin-top: 26px">Explore the houses</a>'),
                 ('<a class="more" href="#kgalerie" style="margin-top: 26px">Discover K-Galerie</a>', '<a class="more" href="k-galerie.html" style="margin-top: 26px">Discover K-Galerie</a>'),
                 ('<a class="more" href="#franchise" style="margin-top: 26px">See our own stores</a>', '<a class="more" href="franchise-retail.html#boggi-milano" style="margin-top: 26px">See the Boggi Milano store</a>'),
                 ('<a class="more" href="#houses" style="margin-top: 26px">Discover the selection</a>', '<a class="more" href="distribution-brands.html" style="margin-top: 26px">Discover the selection</a>')]:
    assert idx.count(old) == 1, old
    idx = idx.replace(old, new)

# slide 4: latest Press article (filled in by script; falls back to a generic Press slide)
m = re.search(r'      <div class="sl" data-i="3">.*?\n      </div>\n', idx, re.S)
assert m
idx = idx[:m.start()] + """      <div class="sl" data-i="3" id="hs-news">
        <div class="tw">
          <p class="ttl t-white" aria-hidden="true"><span>latest</span><span class="l2">news</span></p>
          <h2 class="ttl t-ko ko3"><span>latest</span><span class="l2">news</span></h2>
        </div>
        <div class="hinfo">
          <p class="cap" style="margin: 0 0 14px; display: flex; gap: 14px; flex-wrap: wrap"><span style="color: var(--gold)">04</span><span style="color: #fff" id="hs-meta">Press</span></p>
          <p id="hs-title" style="margin: 0; max-width: 420px; font-size: 17px; line-height: 1.5; color: #fff; font-weight: 500">Store openings, brand news and private events from Kenny's International.</p>
          <a class="more" href="/press" style="margin-top: 26px">See all press</a>
        </div>
      </div>
""" + idx[m.end():]
for a, b in [('<div class="ph" data-i="3"><img src="assets/hero-dg.jpg" alt="Dolce &amp; Gabbana jewellery on display" style="object-position: 50% 50%"></div>',
              '<div class="ph" data-i="3"><img id="hs-img" src="assets/about-storefront.jpg" alt="" style="object-position: 50% 50%"></div>'),
             ('.ko3{background-image:url(assets/hero-dg.jpg);background-position:50% 50%}', '.ko3{background-image:url(assets/about-storefront.jpg);background-position:50% 50%}'),
             ('aria-label="Dolce &amp; Gabbana at Kenny' + "'" + 's"', 'aria-label="Latest news"')]:
    assert idx.count(a) == 1, a[:60]
    idx = idx.replace(a, b)
HERO_NEWS_JS = """<script>(function(){
  var M=['January','February','March','April','May','June','July','August','September','October','November','December'];
  fetch('/api/articles?limit=1').then(function(r){ if(!r.ok) throw 0; return r.json(); }).then(function(j){
    var a=j&&j.items&&j.items[0]; if(!a) return;
    var m=/^(\\d{4})-(\\d{2})-(\\d{2})/.exec(a.date||''), d=m?(+m[3])+' '+M[+m[2]-1]+' '+m[1]:'';
    document.getElementById('hs-meta').textContent=[a.category,d].filter(Boolean).join(' · ');
    document.getElementById('hs-title').textContent=a.title;
    if(a.cover&&a.cover.url){
      var img=document.getElementById('hs-img'); img.src=a.cover.url; img.alt=a.cover.alt||'';
      var ko=document.querySelector('#hs-news .ko3'); if(ko) ko.style.backgroundImage='url('+JSON.stringify(a.cover.url)+')';
    }
  }).catch(function(){});
})();</script>"""

# about teaser -> about page; k-galerie teaser -> k-galerie page
idx = idx.replace('<a class="lnk" href="#visit">Read our story', '<a class="lnk" href="about-us.html">Read our story', 1)
idx = idx.replace('<a class="lnk" href="#visit">Plan your visit', '<a class="lnk" href="k-galerie.html">Discover K-Galerie', 1)

# Kenny's Stores: 4 brands + button
m = re.search(r'(<section id="houses".*?)(    <ul class="g5".*?</ul>\n)(.*?)(  </div>\n</section>)', idx, re.S)
four_dist = "\n".join(dtile(n, i) for n, i in DIST[:4])
idx = idx[:m.start()] + m.group(1) + f"""    <ul class="g4" style="list-style: none; margin: 0; padding: 0; display: grid; grid-template-columns: repeat(4,minmax(0,1fr)); border-top: 1px solid #E8E8E8; border-left: 1px solid #E8E8E8">
{four_dist}
    </ul>
    <div class="morebar rise"><a class="btn" href="distribution-brands.html">See all distribution brands {BTN_ARROW}</a></div>
""" + m.group(4) + idx[m.end():]

# Franchises: 4 brands + button
m = re.search(r'(<section id="franchise".*?)(    <ul class="g4".*?</ul>\n)(  </div>\n</section>)', idx, re.S)
four_fr = "\n".join(ftile(f, href=f"franchise-retail.html#{f['slug']}") for f in FRANCHISES[:4])
idx = idx[:m.start()] + m.group(1) + f"""    <ul class="g4" style="list-style: none; margin: 0; padding: 0; display: grid; grid-template-columns: repeat(4,minmax(0,1fr)); border-top: 1px solid #E8E8E8; border-left: 1px solid #E8E8E8">
{four_fr}
    </ul>
    <div class="morebar rise"><a class="btn" href="franchise-retail.html">See all franchise brands {BTN_ARROW}</a></div>
""" + m.group(3) + idx[m.end():]

# remove Find a store section
idx, n = re.subn(r'<!-- FIND A STORE \(black\) -->.*?</section>\n\n', '', idx, count=1, flags=re.S)
assert n == 1

# footer
idx, n = re.subn(r'<!-- FOOTER \(black\) -->.*?</footer>', lambda m: footer(), idx, count=1, flags=re.S)
assert n == 1

idx = idx.replace('.hero .ph::after{content:"";position:absolute;inset:0;pointer-events:none;background:linear-gradient(180deg,rgba(0,0,0,.45) 0,rgba(0,0,0,0) 26%)}', '')
hm = re.search(r'\n    <header class="htop">.*?\n    </header>\n', idx, re.S); assert hm
header_html = hm.group(0); idx = idx[:hm.start()] + "\n" + idx[hm.end():]
mm = re.search(r'\s*<nav id="mnav" hidden.*?</nav>', idx, re.S); assert mm
mnav_html = mm.group(0); idx = idx[:mm.start()] + idx[mm.end():]
header_html = header_html.replace("\n    </header>", mnav_html + "\n    </header>")
assert idx.count('<main id="top">') == 1
idx = idx.replace('<main id="top">', header_html.strip() + '\n\n<main id="top">', 1)

# Latest news: real articles from the Press API (section hidden if there are none)
m = re.search(r'<section id="journal".*?</section>', idx, re.S)
assert m
NEWS = f"""<section id="journal" aria-labelledby="jr-h" style="background: #fff; padding: clamp(110px,11vw,190px) 0">
  <div class="wrap">
    <div style="display: flex; justify-content: space-between; align-items: end; gap: 24px; flex-wrap: wrap; margin-bottom: clamp(56px,6vw,96px)">
      <div>
        <p class="cap gold rev" style="margin: 0 0 18px">Press</p>
        <h2 id="jr-h" class="wide rev" style="margin: 0; font-size: clamp(30px,3.6vw,68px); line-height: 1.08">Latest news</h2>
      </div>
      <a class="lnk rise" href="/press">All articles{ARROW}</a>
    </div>
    <div class="g3" id="news-grid" aria-busy="true" style="display: grid; grid-template-columns: repeat(3,minmax(0,1fr)); gap: clamp(28px,3vw,56px)">
      <div class="news-sk" aria-hidden="true"><div class="ph" style="aspect-ratio: 4/3"></div><i></i><i></i></div>
      <div class="news-sk" aria-hidden="true"><div class="ph" style="aspect-ratio: 4/3"></div><i></i><i></i></div>
      <div class="news-sk" aria-hidden="true"><div class="ph" style="aspect-ratio: 4/3"></div><i></i><i></i></div>
    </div>
  </div>
</section>"""
idx = idx[:m.start()] + NEWS + idx[m.end():]
NEWS_JS = """<script>(function(){
  var g=document.getElementById('news-grid'), sec=document.getElementById('journal');
  var M=['January','February','March','April','May','June','July','August','September','October','November','December'];
  function d(s){ var m=/^(\\d{4})-(\\d{2})-(\\d{2})/.exec(s||''); return m ? (+m[3])+' '+M[+m[2]-1]+' '+m[1] : ''; }
  function esc(s){ return String(s==null?'':s).replace(/[&<>"']/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]}); }
  var A='""" + ARROW.replace("'", "\\'") + """';
  fetch('/api/articles?limit=3').then(function(r){ if(!r.ok) throw 0; return r.json(); }).then(function(j){
    var items=(j&&j.items)||[]; if(!items.length){ sec.hidden=true; return; }
    g.innerHTML=items.map(function(a,i){ return '<a class="card'+(i?' r'+(i+1):'')+'" href="/press/'+encodeURIComponent(a.slug)+'"><div class="ph"><img src="'+esc(a.cover&&a.cover.url)+'" alt="'+esc(a.cover&&a.cover.alt)+'" loading="lazy"></div><p class="cap gold" style="margin: 26px 0 0; font-size: 10px">'+esc(a.category)+' <span class="dot-sep">·</span> '+d(a.date)+'</p><h3 class="wide" style="margin: 14px 0 0; font-size: clamp(14px,1.15vw,18px); line-height: 1.45">'+esc(a.title)+'</h3><p style="margin: 14px 0 22px; font-size: 15px; line-height: 1.75; color: #6A6A6A">'+esc(a.excerpt)+'</p><span class="lnk">Read article'+A+'</span></a>'; }).join('');
    g.removeAttribute('aria-busy');
  }).catch(function(){ sec.hidden=true; });
})();</script>"""
idx = idx.replace("</body>", DD_JS + "\n" + NEWS_JS + "\n" + HERO_NEWS_JS + "\n" + I18N_JS + "\n</body>", 1)
assert idx.count('<button class="mbtn" type="button" data-act="menu"') == 1
idx = idx.replace('<button class="mbtn" type="button" data-act="menu"', LANG_SW + '\n        <button class="mbtn" type="button" data-act="menu"', 1)
idx = idx.replace("</head>", I18N_HEAD + "\n</head>", 1)
assert "Twenty of the world's leading" in idx
idx = idx.replace("Twenty of the world's leading", "Twenty-one of the world's leading")

# hero script scoped to the hero, plus Escape closes the menu
idx = idx.replace("document.querySelectorAll('.sl')", "document.querySelectorAll('.hero .sl')").replace("document.querySelectorAll('.ph')", "document.querySelectorAll('.hero .ph')")
open(f"{SITE}/index.html", "w", encoding="utf-8").write(idx)
print("built")

# ================================================================== Templates for the server-rendered Press pages
PRESS_CSS = """
.chips{display:flex;flex-wrap:wrap;gap:10px;margin:0 0 clamp(48px,5vw,80px)}
.chip{display:inline-flex;align-items:center;min-height:42px;padding:0 20px;border:1px solid #D9D9D9;text-decoration:none;color:#3A3A3A;font-size:11px;letter-spacing:.2em;text-transform:uppercase;font-weight:500;transition:border-color .3s,background .3s,color .3s}
.chip:hover{border-color:#000;color:#000}
.chip.on{background:#000;border-color:#000;color:#fff}
.feat-a{display:grid;grid-template-columns:minmax(0,1.25fr) minmax(0,1fr);gap:clamp(32px,5vw,90px);align-items:center;text-decoration:none;color:inherit;padding-bottom:clamp(64px,6vw,100px);margin-bottom:clamp(64px,6vw,100px);border-bottom:1px solid #E8E8E8}
.feat-a .ph{overflow:hidden;aspect-ratio:4/3;background:#EEE}
.feat-a .ph img{width:100%;height:100%;object-fit:cover;transition:transform 1.3s cubic-bezier(.2,.8,.1,1)}
.feat-a:hover .ph img{transform:scale(1.05)}
.feat-a h2{margin:22px 0 0;font-size:clamp(22px,2.4vw,40px);line-height:1.15;transition:color .35s}
.feat-a:hover h2{color:var(--gold-ink)}
.feat-a .ex{margin:22px 0 30px;font-size:16px;line-height:1.8;color:#4A4A4A;font-weight:300}
.pgrid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:clamp(48px,4vw,72px) clamp(28px,3vw,56px)}
.empty{padding:clamp(60px,8vw,120px) 0;text-align:center;border-top:1px solid #E8E8E8;border-bottom:1px solid #E8E8E8}
.empty .wide{margin:0;font-size:clamp(20px,2vw,30px)}
.empty p+p{margin:16px 0 26px;color:#6A6A6A}
.pager{display:flex;justify-content:space-between;align-items:center;gap:20px;margin-top:clamp(64px,6vw,100px);padding-top:36px;border-top:1px solid #E8E8E8}
.pager .pg{font-size:13px;color:#6A6A6A}
/* article */
.ahead{background:#000;color:#fff;padding:calc(var(--hh) + clamp(48px,6vw,100px)) 0 clamp(150px,14vw,240px)}
.atitle{margin:0;max-width:1100px;font-size:clamp(28px,4vw,68px);line-height:1.08}
.alead{margin:34px 0 0;max-width:760px;font-size:clamp(17px,1.4vw,21px);line-height:1.7;color:#BDBDBD;font-weight:300}
.acover{margin-top:calc(-1 * clamp(110px,11vw,190px))}
.acover figure{margin:0;overflow:hidden;background:#111}
.acover img{width:100%;max-height:78vh;object-fit:cover}
.abody{padding:clamp(64px,7vw,120px) 0 clamp(100px,10vw,170px);background:#fff}
.agrid{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,760px) minmax(0,1fr);gap:40px;align-items:start}
.aside{position:sticky;top:clamp(110px,13vh,140px)}
.aside .share{flex-direction:column;align-items:flex-start}
.prose{grid-column:2;font-size:18px;line-height:1.85;color:#2A2A2A}
.prose>*:first-child,.abody-text>*:first-child{margin-top:0}
.prose p{margin:0 0 1.35em}
.prose h2{font-family:"Syncopate","Michroma",sans-serif;font-weight:400;text-transform:uppercase;letter-spacing:.04em;font-size:clamp(18px,1.6vw,24px);line-height:1.35;color:#000;margin:2.4em 0 1em}
.prose h3{font-size:clamp(18px,1.4vw,21px);font-weight:600;color:#000;margin:2em 0 .7em}
.prose a{color:inherit;text-decoration:none;border-bottom:1px solid var(--gold);transition:color .3s}
.prose a:hover{color:var(--gold-ink)}
.prose strong{font-weight:600;color:#000}
.prose ul,.prose ol{margin:0 0 1.5em;padding:0;list-style:none}
.prose li{position:relative;padding-left:30px;margin:0 0 .7em}
.prose ul>li::before{content:"";position:absolute;left:4px;top:.72em;width:7px;height:7px;transform:rotate(45deg);background:var(--gold)}
.prose ol{counter-reset:li}
.prose ol>li{counter-increment:li}
.prose ol>li::before{content:counter(li,decimal-leading-zero);position:absolute;left:0;top:.2em;font-size:12px;letter-spacing:.12em;font-weight:600;color:var(--gold-ink)}
.prose blockquote{margin:2em 0;padding:6px 0 6px 28px;border-left:2px solid var(--gold);font-size:clamp(20px,1.7vw,26px);line-height:1.55;color:#000;font-weight:300}
.prose blockquote p:last-child{margin:0}
.prose img{display:block;width:100%;height:auto;margin:2.2em 0}
.prose figure{margin:2.2em 0}
.prose figure img{margin:0}
.prose figcaption{margin-top:12px;font-size:13px;color:#8C8C8C}
.prose hr{border:0;height:1px;background:#E8E8E8;margin:2.6em 0}
.aend{display:flex;justify-content:space-between;align-items:center;gap:24px;flex-wrap:wrap;margin-top:3em;padding-top:28px;border-top:1px solid #E8E8E8}
.share{display:flex;align-items:center;gap:10px;position:relative}
.share .cap{font-size:10px;color:#8C8C8C;margin-right:4px}
.share a,.share button{width:40px;height:40px;display:inline-flex;align-items:center;justify-content:center;border:1px solid #D9D9D9;background:#fff;color:#000;cursor:pointer;transition:background .3s,border-color .3s}
.share a:hover,.share button:hover{background:var(--gold);border-color:var(--gold)}
.share .copied{font-size:12px;color:var(--gold-ink);min-width:1px}
.pv-banner{position:fixed;left:0;right:0;bottom:0;z-index:80;background:var(--gold,#C9A55C);color:#000;padding:12px 20px;text-align:center;font-size:14px;font-family:"Jost",sans-serif}
.pv-banner a{color:#000;font-weight:600}
@media (max-width:1100px){
  .agrid{grid-template-columns:minmax(0,1fr)}
  .prose{grid-column:1}
  .aside{display:none}
  .feat-a{grid-template-columns:minmax(0,1fr)}
  .pgrid{grid-template-columns:repeat(2,minmax(0,1fr))}
}
@media (max-width:600px){
  .pgrid{grid-template-columns:minmax(0,1fr)}
  .prose{font-size:17px}
  .acover{margin-top:-90px}
  .ahead{padding-bottom:130px}
}
"""

def absolutize(s):
    s = re.sub(r'\b(href|src)="(?!https?:|mailto:|tel:|#|/|data:)', r'\1="/', s)
    return s.replace("url(assets/", "url(/assets/")

def jsstr(s): return json.dumps(s, ensure_ascii=False)

tpl = "// Generated by the site builder. Do not edit by hand: change build3.py and rebuild.\n"
tpl += f"export const STYLE = {jsstr(absolutize(style + SHARED_CSS + SUB_CSS))};\n"
tpl += f"export const PRESS_CSS = {jsstr(PRESS_CSS)};\n"
tpl += f"export const HEAD_LINKS = {jsstr(absolutize(head_links))};\n"
tpl += f"export const HEADER_PRESS = {jsstr(absolutize(sub_header('press')))};\n"
tpl += f"export const FOOTER = {jsstr(absolutize(footer()))};\n"
tpl += f"export const SCRIPTS = {jsstr(MENU_JS + chr(10) + I18N_JS)};\n"
open(TPL_OUT, "w", encoding="utf-8").write(tpl)
print("templates written")
