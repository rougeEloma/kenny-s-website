// Public Press pages and the public article list used by the homepage.
//   GET /press                  list (?category=, ?page=)
//   GET /press/:slug            one article (?preview=1 shows drafts to signed-in team members)
//   GET /api/articles?limit=3   latest published articles as JSON
import { publishedList, findBySlug, CATEGORIES } from "./_lib/articles.mjs";
import { sessionUser, safe } from "./_lib/auth.mjs";
import { renderPressList, renderArticle, renderNotFound } from "./_lib/render.mjs";

const PER_PAGE = 13; // 1 featured + 12 on the first page
const CACHED = {
  "cache-control": "public, max-age=0, must-revalidate",
  "netlify-cdn-cache-control": "public, durable, max-age=600, stale-while-revalidate=86400",
  "cache-tag": "press",
};
const html = (body, status = 200, headers = CACHED) => new Response(body, { status, headers: { "content-type": "text/html; charset=utf-8", ...headers } });

export default safe(async (req, context) => {
  const url = new URL(req.url);
  const origin = url.origin;

  if (url.pathname === "/api/articles") {
    const limit = Math.min(Math.max(parseInt(url.searchParams.get("limit") || "3", 10) || 3, 1), 24);
    const items = (await publishedList()).slice(0, limit).map((a) => ({ slug: a.slug, title: a.title, category: a.category, date: a.date, excerpt: a.excerpt, cover: a.cover }));
    return new Response(JSON.stringify({ items }), { headers: { "content-type": "application/json; charset=utf-8", ...CACHED } });
  }

  const path = url.pathname.replace(/\/index\.html?$/, "").replace(/\.html?$/, "");
  const m = /^\/press\/([^/]+)\/?$/.exec(path);
  const slug = m ? decodeURIComponent(m[1]).toLowerCase() : "";
  if (!slug) {
    const category = CATEGORIES.includes(url.searchParams.get("category")) ? url.searchParams.get("category") : "";
    const all = (await publishedList()).filter((a) => !category || a.category === category);
    const pages = Math.max(1, Math.ceil(all.length / PER_PAGE));
    const page = Math.min(Math.max(parseInt(url.searchParams.get("page") || "1", 10) || 1, 1), pages);
    const items = all.slice((page - 1) * PER_PAGE, page * PER_PAGE);
    return html(renderPressList({ items, page, pages, category, categories: CATEGORIES, origin }));
  }

  const a = await findBySlug(slug);
  const wantsPreview = url.searchParams.get("preview") === "1";
  if (a && (a.status === "published" || wantsPreview)) {
    if (wantsPreview) {
      const user = await sessionUser(req);
      if (!user) return html(renderNotFound({ origin }), 404, { "cache-control": "no-store" });
      const related = (await publishedList()).filter((r) => r.id !== a.id).slice(0, 3);
      return html(renderArticle({ a, related, origin, preview: true }), 200, { "cache-control": "private, no-store" });
    }
    const related = (await publishedList()).filter((r) => r.id !== a.id).slice(0, 3);
    return html(renderArticle({ a, related, origin, preview: false }));
  }
  return html(renderNotFound({ origin }), 404, { "cache-control": "public, max-age=0", "netlify-cdn-cache-control": "public, max-age=60", "cache-tag": "press" });
});

export const config = { path: ["/press", "/press/", "/press/:slug", "/api/articles"] };
