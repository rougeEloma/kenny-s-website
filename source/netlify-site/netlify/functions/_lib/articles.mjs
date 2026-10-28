// Article storage (Netlify Blobs) and validation.
import crypto from "node:crypto";
import { getStore } from "@netlify/blobs";
import sanitizeHtml from "sanitize-html";

export const CATEGORIES = ["Events", "Store openings", "Brands", "News"];
const store = () => getStore({ name: "kp-articles", consistency: "strong" });
const INDEX = "_index";

export function slugify(s) {
  return String(s || "").normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/['\u2019]/g, "").toLowerCase()
    .replace(/&/g, " and ").replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 90) || "article";
}

// Allowed article formatting; everything else is stripped on save.
export function cleanBody(html) {
  return sanitizeHtml(String(html || ""), {
    allowedTags: ["p", "h2", "h3", "strong", "b", "em", "i", "u", "a", "ul", "ol", "li", "blockquote", "br", "hr", "figure", "figcaption", "img"],
    allowedAttributes: { a: ["href", "target", "rel"], img: ["src", "alt", "width", "height", "loading"] },
    allowedSchemes: ["https", "mailto", "tel"],
    allowedSchemesByTag: { img: [] },
    allowProtocolRelative: false,
    exclusiveFilter: (f) => f.tag === "img" && !/^\/media\/[A-Za-z0-9/_.-]+$/.test(f.attribs.src || ""),
    transformTags: {
      b: "strong", i: "em",
      a: (tag, attribs) => {
        const href = attribs.href || "";
        const external = /^https?:\/\//i.test(href) && !/kennysinternational/i.test(href);
        return { tagName: "a", attribs: external ? { href, target: "_blank", rel: "noopener" } : { href } };
      },
      img: (tag, attribs) => ({ tagName: "img", attribs: { src: attribs.src, alt: attribs.alt || "", loading: "lazy" } }),
    },
  }).replace(/<p>\s*(<br \/>)?\s*<\/p>/g, "").trim();
}

const text = (v, max) => String(v ?? "").replace(/\s+/g, " ").trim().slice(0, max);
const mediaUrl = (v) => (/^\/media\/[A-Za-z0-9/_.-]+$/.test(String(v || "")) ? String(v) : "");

// Validates and normalises input from the editor. Returns { data } or { error }.
export function validate(input, { publishing }) {
  const title = text(input.title, 160);
  const status = input.status === "published" ? "published" : "draft";
  const date = /^\d{4}-\d{2}-\d{2}$/.test(input.date || "") ? input.date : new Date().toISOString().slice(0, 10);
  const category = CATEGORIES.includes(input.category) ? input.category : CATEGORIES[0];
  const excerpt = text(input.excerpt, 320);
  const body = cleanBody(input.body);
  const cover = { url: mediaUrl(input.cover?.url), alt: text(input.cover?.alt, 200) };
  const slug = slugify(input.slug || title);
  if (!title) return { error: "Please add a title." };
  if (status === "published" || publishing) {
    if (!excerpt) return { error: "Please add a short summary before publishing." };
    if (!cover.url) return { error: "Please add a cover photo before publishing." };
    if (sanitizeHtml(body, { allowedTags: [] }).trim().length < 40) return { error: "The article text is too short to publish." };
  }
  return { data: { title, slug, status, date, category, excerpt, body, cover } };
}

export async function getArticle(id) {
  if (!/^[a-f0-9-]{36}$/.test(id || "")) return null;
  return store().get(`a/${id}`, { type: "json" });
}

export async function listIndex() {
  return (await store().get(INDEX, { type: "json" })) || [];
}

// Rebuilds the summary index from every article (self-healing; writes are rare).
export async function rebuildIndex() {
  const s = store();
  const { blobs } = await s.list({ prefix: "a/" });
  const all = (await Promise.all(blobs.map((b) => s.get(b.key, { type: "json" })))).filter(Boolean);
  const index = all.map(summary).sort(byDateDesc);
  await s.setJSON(INDEX, index);
  return index;
}

export const summary = (a) => ({
  id: a.id, slug: a.slug, title: a.title, category: a.category, date: a.date, excerpt: a.excerpt,
  cover: a.cover, status: a.status, author: a.author, authorName: a.authorName, updatedAt: a.updatedAt,
});
export const byDateDesc = (a, b) => (b.date || "").localeCompare(a.date || "") || (b.updatedAt || "").localeCompare(a.updatedAt || "");

async function uniqueSlug(slug, id) {
  const index = await listIndex();
  let s = slug, n = 2;
  while (index.some((a) => a.slug === s && a.id !== id)) s = `${slug}-${n++}`;
  return s;
}

export async function saveArticle(existing, data, user) {
  const now = new Date().toISOString();
  const id = existing?.id || crypto.randomUUID();
  const article = {
    ...(existing || {}),
    ...data,
    id,
    slug: await uniqueSlug(data.slug, id),
    author: existing?.author || user.email,
    authorName: existing?.authorName || user.name,
    createdAt: existing?.createdAt || now,
    updatedAt: now,
    updatedBy: user.email,
    publishedAt: data.status === "published" ? (existing?.publishedAt || now) : null,
  };
  await store().setJSON(`a/${id}`, article);
  await rebuildIndex();
  return article;
}

export async function deleteArticle(id) {
  await store().delete(`a/${id}`);
  await rebuildIndex();
}

export async function publishedList() {
  return (await listIndex()).filter((a) => a.status === "published").sort(byDateDesc);
}

export async function findBySlug(slug) {
  const hit = (await listIndex()).find((a) => a.slug === slug);
  return hit ? getArticle(hit.id) : null;
}
