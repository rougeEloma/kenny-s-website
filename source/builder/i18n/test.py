import sys, json, re
from playwright.sync_api import sync_playwright
base, out = sys.argv[1], sys.argv[2]
pages = ["/index.html", "/about-us.html", "/distribution-brands.html", "/franchise-retail.html", "/k-galerie.html", "/contact.html"]
LEFT = """() => { const out=new Set(); const w=document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  let n; while((n=w.nextNode())){ const p=n.parentElement; if(!p||p.closest('script,style,.prose,[data-noi18n]')) continue;
  if(p.closest('[hidden]')) continue; const t=n.nodeValue.replace(/\\s+/g,' ').trim(); if(/[a-z]{3}/.test(t) && !n.__kpEn) out.add(t); }
  document.querySelectorAll('[alt],[aria-label],[placeholder]').forEach(e=>['alt','aria-label','placeholder'].forEach(a=>{const v=e.getAttribute(a); if(v && /[a-z]{3}/.test(v) && !(e.__kpAttr&&e.__kpAttr[a])) out.add('@'+a+': '+v);}));
  return [...out]; }"""
errs=[]
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={"width": 1440, "height": 900}, locale="en-US")
    d = ctx.new_page(); d.on("pageerror", lambda e: errs.append(str(e)))
    d.goto(base + "/index.html"); d.wait_for_timeout(600)
    print("default (en browser):", d.evaluate("document.documentElement.lang"))
    d.click('.htop [data-lang="fr"]'); d.wait_for_timeout(400)
    print("after click:", d.evaluate("document.documentElement.lang"), "| title:", d.title())
    for pg in pages:
        d.goto(base + pg); d.wait_for_timeout(900)
        if pg == "/franchise-retail.html": d.click('[data-brand="mango"]'); d.wait_for_timeout(500)
        if pg == "/contact.html": d.click("#fsend"); d.wait_for_timeout(200)
        left = d.evaluate(LEFT)
        print(f"\n== {pg} [{d.evaluate('document.documentElement.lang')}] title: {d.title()}")
        for t in left: print("   ", t[:110])
        if pg == "/franchise-retail.html": d.keyboard.press("Escape")
        d.screenshot(path=f"{out}/fr{pg.replace('/','-').replace('.html','')}.png", full_page=False)
    d.goto(base + "/about-us.html"); d.wait_for_timeout(500)
    d.click('.ptop [data-lang="en"]'); d.wait_for_timeout(300)
    print("\nswitch back:", d.evaluate("document.documentElement.lang"), "| h1:", d.inner_text("h1"), "| title:", d.title())
    fr = b.new_context(viewport={"width": 390, "height": 844}, locale="fr-FR").new_page()
    fr.goto(base + "/index.html"); fr.wait_for_timeout(800)
    print("french browser default:", fr.evaluate("document.documentElement.lang"), "| nav:", fr.inner_text(".htop .lang"))
    fr.screenshot(path=f"{out}/m-fr-home.png")
    fr.click('[data-act="menu"]'); fr.wait_for_timeout(300); fr.screenshot(path=f"{out}/m-fr-menu.png")
    b.close()
print("errors:", errs)
