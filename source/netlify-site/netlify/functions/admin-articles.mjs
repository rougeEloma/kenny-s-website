// Dashboard article API. Admins manage their own articles; the super-admin manages all.
//   GET    /api/admin/articles          list (everyone sees all, with a "canEdit" flag)
//   GET    /api/admin/articles/:id      one article
//   POST   /api/admin/articles          create
//   PUT    /api/admin/articles/:id      update
//   DELETE /api/admin/articles/:id      delete
import { purgeCache } from "@netlify/functions";
import { requireUser, json, canEdit, cleanPath, safe } from "./_lib/auth.mjs";
import { listIndex, getArticle, validate, saveArticle, deleteArticle, CATEGORIES } from "./_lib/articles.mjs";

async function purge() {
  try { await purgeCache({ tags: ["press"] }); } catch (e) { console.log("purge skipped:", e.message); }
}

export default safe(async (req, context) => {
  const { user, error } = await requireUser(req);
  if (error) return error;
  const m = /^\/api\/admin\/articles\/([^/]+)$/.exec(cleanPath(req));
  const id = m ? m[1] : "";

  if (req.method === "GET" && !id) {
    const items = (await listIndex()).map((a) => ({ ...a, canEdit: canEdit(user, a) }));
    return json({ items, user, categories: CATEGORIES });
  }

  if (req.method === "GET" && id) {
    const a = await getArticle(id);
    if (!a) return json({ error: "Article not found." }, 404);
    return json({ article: { ...a, canEdit: canEdit(user, a) } });
  }

  if (req.method === "POST" && !id) {
    let input = {};
    try { input = await req.json(); } catch { return json({ error: "Invalid request." }, 400); }
    const v = validate(input, { publishing: input.status === "published" });
    if (v.error) return json({ error: v.error }, 400);
    const saved = await saveArticle(null, v.data, user);
    if (saved.status === "published") await purge();
    return json({ article: { ...saved, canEdit: true } }, 201);
  }

  if (req.method === "PUT" && id) {
    const existing = await getArticle(id);
    if (!existing) return json({ error: "Article not found." }, 404);
    if (!canEdit(user, existing)) return json({ error: "You can only edit your own articles." }, 403);
    let input = {};
    try { input = await req.json(); } catch { return json({ error: "Invalid request." }, 400); }
    if (input.updatedAt && input.updatedAt !== existing.updatedAt) {
      return json({ error: `This article was changed by ${existing.updatedBy} since you opened it. Reload to see the latest version.` }, 409);
    }
    const v = validate(input, { publishing: input.status === "published" });
    if (v.error) return json({ error: v.error }, 400);
    const saved = await saveArticle(existing, v.data, user);
    if (saved.status === "published" || existing.status === "published") await purge();
    return json({ article: { ...saved, canEdit: true } });
  }

  if (req.method === "DELETE" && id) {
    const existing = await getArticle(id);
    if (!existing) return json({ error: "Article not found." }, 404);
    if (!canEdit(user, existing)) return json({ error: "You can only delete your own articles." }, 403);
    await deleteArticle(id);
    if (existing.status === "published") await purge();
    return json({ ok: true });
  }

  return json({ error: "Not found" }, 404);
});

export const config = { path: ["/api/admin/articles", "/api/admin/articles/:id"] };
