// Server-rendered Press pages, using the same header, footer and styles as the static site.
import { STYLE, HEAD_LINKS, HEADER_PRESS, FOOTER, SCRIPTS, PRESS_CSS } from "./templates.mjs";

export const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
export function fmtDate(iso) {
  const m = /^(\d{4})-(\d{2})-(\d{2})/.exec(iso || "");
  return m ? `${+m[3]} ${MONTHS[+m[2] - 1]} ${m[1]}` : "";
}
const ARROW = '<svg height="10" viewBox="0 0 46 10" preserveAspectRatio="none" fill="none" stroke="currentColor" stroke-width="1" aria-hidden="true"><path d="M0 5h45M40 1l5 4-5 4"></path></svg>';
const ICONS = {
  facebook: '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M14 8h3V4h-3a4 4 0 0 0-4 4v3H7v4h3v6h4v-6h3l1-4h-4V8z"></path></svg>',
  linkedin: '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M7 10v8M7 6v.01M11 18v-5a3 3 0 0 1 6 0v5M11 10v8"></path></svg>',
  whatsapp: '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M4 20l1.3-3.9A8 8 0 1 1 8 19z"></path><path d="M9 9.5c.4 2 2.1 3.9 4.5 4.6l1.2-1.2 2 .9c-.3 1.2-1.4 1.9-2.6 1.7-3.4-.6-6.1-3.3-6.6-6.6-.2-1.2.5-2.3 1.7-2.6l.9 2z"></path></svg>',
  link: '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1-1"></path></svg>',
};

function doc({ title, desc, canonical, ogImage, ogType = "website", extraHead = "", body, banner = "" }) {
  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${esc(title)}</title>
<meta name="description" content="${esc(desc)}">
<link rel="canonical" href="${esc(canonical)}">
<meta property="og:type" content="${ogType}">
<meta property="og:title" content="${esc(title)}">
<meta property="og:description" content="${esc(desc)}">
<meta property="og:url" content="${esc(canonical)}">
${ogImage ? `<meta property="og:image" content="${esc(ogImage)}">\n<meta name="twitter:card" content="summary_large_image">` : ""}
${extraHead}
${HEAD_LINKS}
<style>${STYLE}${PRESS_CSS}</style>
</head>
<body>
${banner}
<div class="k" style="--gold: #C9A55C">
${HEADER_PRESS}
<main id="top">
${body}
</main>
${FOOTER}
</div>
${SCRIPTS}
</body>
</html>`;
}

const card = (a, cls = "") => `<a class="card${cls}" href="/press/${esc(a.slug)}">
        <div class="ph"><img src="${esc(a.cover?.url)}" alt="${esc(a.cover?.alt)}" loading="lazy"></div>
        <p class="cap gold" style="margin: 26px 0 0; font-size: 10px">${esc(a.category)} <span class="dot-sep">·</span> <time datetime="${esc(a.date)}">${fmtDate(a.date)}</time></p>
        <h3 class="wide" style="margin: 14px 0 0; font-size: clamp(14px,1.15vw,18px); line-height: 1.45">${esc(a.title)}</h3>
        <p style="margin: 14px 0 22px; font-size: 15px; line-height: 1.75; color: #6A6A6A">${esc(a.excerpt)}</p>
        <span class="lnk">Read article${ARROW}</span>
      </a>`;

export function renderPressList({ items, page, pages, category, categories, origin }) {
  const q = (p, c = category) => {
    const s = new URLSearchParams();
    if (c) s.set("category", c);
    if (p > 1) s.set("page", p);
    const str = s.toString();
    return "/press" + (str ? "?" + str : "");
  };
  const chips = [`<a class="chip${!category ? " on" : ""}" href="/press"${!category ? ' aria-current="page"' : ""}>All</a>`]
    .concat(categories.map((c) => `<a class="chip${c === category ? " on" : ""}" href="${q(1, c)}"${c === category ? ' aria-current="page"' : ""}>${esc(c)}</a>`)).join("");
  const featured = page === 1 && items.length ? items[0] : null;
  const rest = featured ? items.slice(1) : items;
  const feat = featured ? `
    <a class="feat-a" href="/press/${esc(featured.slug)}">
      <div class="ph"><img src="${esc(featured.cover?.url)}" alt="${esc(featured.cover?.alt)}"></div>
      <div class="ft">
        <p class="cap gold" style="margin: 0">Latest <span class="dot-sep">·</span> ${esc(featured.category)} <span class="dot-sep">·</span> <time datetime="${esc(featured.date)}">${fmtDate(featured.date)}</time></p>
        <h2 class="wide">${esc(featured.title)}</h2>
        <p class="ex">${esc(featured.excerpt)}</p>
        <span class="lnk">Read article${ARROW}</span>
      </div>
    </a>` : "";
  const grid = rest.length ? `<div class="g3 pgrid">${rest.map((a) => card(a)).join("\n")}</div>` : "";
  const empty = !items.length ? `<div class="empty"><p class="wide">No articles yet</p><p>${category ? "There are no articles in this category yet." : "News and events will appear here soon."}</p>${category ? `<a class="lnk" href="/press">See all articles${ARROW}</a>` : ""}</div>` : "";
  const pager = pages > 1 ? `<nav class="pager" aria-label="Pages">${page > 1 ? `<a class="btn" href="${q(page - 1)}">Newer</a>` : "<span></span>"}<span class="pg">Page ${page} of ${pages}</span>${page < pages ? `<a class="btn" href="${q(page + 1)}">Older</a>` : "<span></span>"}</nav>` : "";

  const body = `<section class="phead on-dark" aria-labelledby="page-h">
  <div class="wrap">
    <p class="crumb"><a href="/index.html">Home</a><span aria-hidden="true">/</span><span>Press</span></p>
    <div class="two" style="display: grid; grid-template-columns: minmax(0,1.3fr) minmax(0,1fr); gap: 40px; align-items: end">
      <div>
        <p class="cap gold rev" style="margin: 0 0 22px">Press</p>
        <h1 id="page-h" class="wide ptitle rev">News &amp; events</h1>
      </div>
      <p class="rise" style="margin: 0; max-width: 460px; justify-self: end; font-size: 16px; line-height: 1.8; color: #BDBDBD; font-weight: 300">Store openings, brand news and private events from Kenny's International.</p>
    </div>
  </div>
</section>

<section class="sec" aria-label="Articles" style="background: #fff; padding-top: clamp(56px,6vw,96px)">
  <div class="wrap">
    <nav class="chips" aria-label="Categories">${chips}</nav>
    ${feat}
    ${grid}
    ${empty}
    ${pager}
  </div>
</section>`;
  return doc({
    title: (category ? `${category} | ` : "") + "Press | Kenny's International",
    desc: "News, store openings and events from Kenny's International in Kinshasa, Lubumbashi, Kolwezi and Pointe-Noire.",
    canonical: origin + q(page),
    ogImage: featured?.cover?.url ? origin + featured.cover.url : origin + "/assets/hero-kennys.jpg",
    body,
  });
}

export function renderArticle({ a, related, origin, preview }) {
  const url = `${origin}/press/${a.slug}`;
  const share = encodeURIComponent(url), t = encodeURIComponent(a.title);
  const shareBar = `<div class="share">
        <span class="cap">Share</span>
        <a href="https://www.facebook.com/sharer/sharer.php?u=${share}" target="_blank" rel="noopener" aria-label="Share on Facebook">${ICONS.facebook}</a>
        <a href="https://www.linkedin.com/sharing/share-offsite/?url=${share}" target="_blank" rel="noopener" aria-label="Share on LinkedIn">${ICONS.linkedin}</a>
        <a href="https://wa.me/?text=${t}%20${share}" target="_blank" rel="noopener" aria-label="Share on WhatsApp">${ICONS.whatsapp}</a>
        <button type="button" data-copy="${esc(url)}" aria-label="Copy link">${ICONS.link}</button>
        <span class="copied" role="status" aria-live="polite"></span>
      </div>`;
  const rel = related.length ? `
<section class="sec" aria-labelledby="more-h" style="background: #FAF9F6">
  <div class="wrap">
    <div class="two" style="display: grid; grid-template-columns: minmax(0,1fr) auto; gap: 40px; align-items: end; margin-bottom: clamp(48px,5vw,80px)">
      <div><p class="cap gold" style="margin: 0 0 18px">Press</p><h2 id="more-h" class="wide h2">More news</h2></div>
      <a class="lnk" href="/press">All articles${ARROW}</a>
    </div>
    <div class="g3 pgrid">${related.map((r) => card(r)).join("\n")}</div>
  </div>
</section>` : "";
  const ld = {
    "@context": "https://schema.org", "@type": "NewsArticle", headline: a.title, description: a.excerpt,
    image: a.cover?.url ? [origin + a.cover.url] : undefined, datePublished: a.date, dateModified: a.updatedAt,
    publisher: { "@type": "Organization", name: "Kenny's International", logo: { "@type": "ImageObject", url: origin + "/assets/emblem.png" } },
    mainEntityOfPage: url,
  };
  const body = `<article>
<header class="ahead on-dark">
  <div class="wrap">
    <p class="crumb"><a href="/index.html">Home</a><span aria-hidden="true">/</span><a href="/press">Press</a><span aria-hidden="true">/</span><span>${esc(a.category)}</span></p>
    <p class="cap gold rev" style="margin: 0 0 24px">${esc(a.category)} <span class="dot-sep">·</span> <time datetime="${esc(a.date)}">${fmtDate(a.date)}</time></p>
    <h1 class="wide atitle rev">${esc(a.title)}</h1>
    <p class="alead rise">${esc(a.excerpt)}</p>
  </div>
</header>
${a.cover?.url ? `<div class="acover"><div class="wrap"><figure><img src="${esc(a.cover.url)}" alt="${esc(a.cover.alt)}"></figure></div></div>` : ""}
<div class="abody">
  <div class="wrap agrid">
    <aside class="aside">${shareBar}</aside>
    <div class="prose">
      <div class="abody-text" data-noi18n>${a.body}</div>
      <div class="aend">
        <a class="lnk" href="/press">Back to Press${ARROW}</a>
        ${shareBar}
      </div>
    </div>
  </div>
</div>
</article>
${rel}`;
  return doc({
    title: `${a.title} | Kenny's International`,
    desc: a.excerpt,
    canonical: url,
    ogImage: a.cover?.url ? origin + a.cover.url : "",
    ogType: "article",
    extraHead: `<meta property="article:published_time" content="${esc(a.date)}">\n<script type="application/ld+json">${JSON.stringify(ld).replace(/</g, "\\u003c")}</script>${preview ? '\n<meta name="robots" content="noindex">' : ""}`,
    body,
    banner: preview ? `<div class="pv-banner" role="status">Preview${a.status !== "published" ? " of a draft" : ""}: only signed-in team members can see ${a.status !== "published" ? "this page" : "this preview link"}. <a href="/vogin">Back to the dashboard</a></div>` : "",
  });
}

export function renderNotFound({ origin }) {
  return doc({
    title: "Article not found | Kenny's International",
    desc: "This article could not be found.",
    canonical: origin + "/press",
    body: `<section class="phead on-dark" style="min-height: 60vh"><div class="wrap">
      <p class="crumb"><a href="/index.html">Home</a><span aria-hidden="true">/</span><a href="/press">Press</a></p>
      <p class="cap gold" style="margin: 0 0 22px">404</p>
      <h1 class="wide ptitle">Article not found</h1>
      <p style="margin: 30px 0 40px; max-width: 520px; font-size: 16px; line-height: 1.8; color: #BDBDBD; font-weight: 300">This article may have been moved or removed.</p>
      <a class="btn" href="/press">See all articles</a>
    </div></section>`,
  });
}
