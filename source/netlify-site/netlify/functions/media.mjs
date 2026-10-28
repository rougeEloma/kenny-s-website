// Photo upload (signed-in users) and public photo serving.
//   POST /api/admin/upload   raw image body (JPEG, PNG or WebP, max 4 MB) -> { url }
//   GET  /media/<key>        serves the image, cached for a year
import crypto from "node:crypto";
import { getStore } from "@netlify/blobs";
import { requireUser, json, cleanPath, safe } from "./_lib/auth.mjs";

const TYPES = { "image/jpeg": "jpg", "image/png": "png", "image/webp": "webp" };
const MAX = 4 * 1024 * 1024;
const store = () => getStore({ name: "kp-media", consistency: "strong" });

function sniff(buf) {
  if (buf[0] === 0xff && buf[1] === 0xd8 && buf[2] === 0xff) return "image/jpeg";
  if (buf[0] === 0x89 && buf[1] === 0x50 && buf[2] === 0x4e && buf[3] === 0x47) return "image/png";
  if (buf.slice(0, 4).toString() === "RIFF" && buf.slice(8, 12).toString() === "WEBP") return "image/webp";
  return null;
}

export default safe(async (req) => {
  const url = new URL(req.url);

  if (cleanPath(req) === "/api/admin/upload") {
    if (req.method !== "POST") return json({ error: "Not found" }, 404);
    const { user, error } = await requireUser(req);
    if (error) return error;
    const buf = Buffer.from(await req.arrayBuffer());
    if (!buf.length) return json({ error: "No file received." }, 400);
    if (buf.length > MAX) return json({ error: "This photo is too large (max 4 MB)." }, 413);
    const type = sniff(buf);
    if (!type) return json({ error: "Please upload a JPEG, PNG or WebP photo." }, 415);
    const key = `${new Date().toISOString().slice(0, 7)}/${crypto.randomUUID()}.${TYPES[type]}`;
    await store().set(key, buf, { metadata: { type, by: user.email, at: new Date().toISOString() } });
    return json({ url: `/media/${key}` }, 201);
  }

  if (req.method !== "GET" && req.method !== "HEAD") return new Response("Not found", { status: 404 });
  const key = decodeURIComponent(url.pathname.replace(/^\/media\//, ""));
  if (!/^\d{4}-\d{2}\/[a-f0-9-]{36}\.(jpg|png|webp)$/.test(key)) return new Response("Not found", { status: 404 });
  const hit = await store().getWithMetadata(key, { type: "arrayBuffer" });
  if (!hit) return new Response("Not found", { status: 404 });
  return new Response(hit.data, {
    headers: {
      "content-type": hit.metadata?.type || "application/octet-stream",
      "cache-control": "public, max-age=31536000, immutable",
      "x-content-type-options": "nosniff",
    },
  });
});

export const config = { path: ["/api/admin/upload", "/media/*"] };
