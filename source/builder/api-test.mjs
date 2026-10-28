// End-to-end API test against a running site. Usage: node api-test.mjs <baseUrl> <password> <imagePath> [--keep]
import fs from "node:fs";
const [base, PW, img] = process.argv.slice(2);
const keep = process.argv.includes("--keep");
let pass = 0, fail = 0;
const ok = (c, msg) => { if (c) { pass++; console.log("  ok  ", msg); } else { fail++; console.log("  FAIL", msg); } };

class Client {
  constructor() { this.cookie = ""; }
  async req(method, path, body, { raw, type, headers = {} } = {}) {
    const h = { "x-kp": "1", ...headers };
    if (this.cookie) h.cookie = this.cookie;
    let b;
    if (raw) { b = raw; h["content-type"] = type; } else if (body !== undefined) { b = JSON.stringify(body); h["content-type"] = "application/json"; }
    const r = await fetch(base + path, { method, headers: h, body: b, redirect: "manual" });
    const sc = r.headers.get("set-cookie");
    if (sc) this.cookie = sc.split(";")[0].endsWith("=") ? "" : sc.split(";")[0];
    let j = null; try { j = await r.json(); } catch {}
    return { status: r.status, j, sc };
  }
  login(email, pw = PW) { return this.req("POST", "/api/auth/login", { email, password: pw }); }
}

const SUPER = "refdigital@kennysinternational.com", A1 = "ewurakua@kennysinternational.com", A2 = "ange@kennysinternational.com";
const art = (title, status = "draft") => ({ title, excerpt: "A short summary for testing the dashboard.", body: "<p>This is a test article body that is long enough to publish.</p><script>alert(1)</script><p><img src=\"https://evil.example/x.png\"><a href=\"javascript:alert(1)\">bad</a></p>", category: "Events", date: "2026-10-09", status });

console.log("Auth");
const anon = new Client();
ok((await anon.req("GET", "/api/admin/articles")).status === 401, "anonymous cannot list admin articles");
ok((await anon.login(SUPER, "wrong-password")).status === 401, "wrong password rejected");
ok((await anon.login("stranger@example.com")).status === 401, "unknown email rejected");
const csrf = await fetch(base + "/api/auth/login", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ email: SUPER, password: PW }) });
ok(csrf.status === 403, "login without dashboard header refused (cross-site protection)");
const cross = await fetch(base + "/api/auth/login", { method: "POST", headers: { "content-type": "application/json", "x-kp": "1", origin: "https://evil.example" }, body: JSON.stringify({ email: SUPER, password: PW }) });
ok(cross.status === 403, "login from another website refused");

const sup = new Client(), a1 = new Client(), a2 = new Client();
let r = await sup.login(SUPER);
ok(r.status === 200 && r.j.user.role === "super", "super-admin signs in");
ok(/HttpOnly/.test(r.sc) && /SameSite=Strict/.test(r.sc) && /Secure/.test(r.sc), "session cookie is HttpOnly, Secure, SameSite=Strict");
ok((await a1.login(A1)).status === 200, "admin 1 signs in");
ok((await a2.login(A2)).status === 200, "admin 2 signs in");
ok((await a1.req("GET", "/api/auth/me")).j?.user?.role === "admin", "admin role reported");

console.log("Upload");
const buf = fs.readFileSync(img);
r = await a1.req("POST", "/api/admin/upload", undefined, { raw: buf, type: "image/jpeg" });
ok(r.status === 201 && /^\/media\//.test(r.j.url), "admin uploads a photo");
const photo = r.j.url;
const g = await fetch(base + photo);
ok(g.status === 200 && g.headers.get("content-type") === "image/jpeg", "photo is served publicly");
r = await a1.req("POST", "/api/admin/upload", undefined, { raw: Buffer.from("<svg onload=alert(1)>"), type: "image/png" });
ok(r.status === 415, "non-image upload refused");
r = await anon.req("POST", "/api/admin/upload", undefined, { raw: buf, type: "image/jpeg" });
ok(r.status === 401, "anonymous upload refused");

console.log("Articles");
r = await a1.req("POST", "/api/admin/articles", art("Admin one draft"));
ok(r.status === 201, "admin creates a draft");
const d1 = r.j.article;
ok(!/script|evil|javascript/.test(d1.body), "unsafe HTML stripped from body");
r = await a1.req("POST", "/api/admin/articles", art("Missing cover", "published"));
ok(r.status === 400 && /cover/i.test(r.j.error), "publishing without a cover photo refused");
r = await a1.req("POST", "/api/admin/articles", { ...art("Admin one published", "published"), cover: { url: photo, alt: "Test" } });
ok(r.status === 201 && r.j.article.status === "published", "admin publishes with a cover");
const p1 = r.j.article;
r = await a1.req("POST", "/api/admin/articles", { ...art("Admin one published", "draft") });
ok(r.j.article.slug === "admin-one-published-2", "duplicate title gets a unique web address");
const d1b = r.j.article;

r = await anon.req("GET", "/api/articles?limit=3");
ok(r.j.items.some((x) => x.slug === p1.slug) && !r.j.items.some((x) => x.slug === d1.slug), "public list shows published, hides drafts");
let page = await fetch(base + "/press/" + p1.slug);
ok(page.status === 200, "published article page is public");
page = await fetch(base + "/press/" + d1.slug);
ok(page.status === 404, "draft article page is hidden from the public");
page = await fetch(base + "/press/" + d1.slug + "?preview=1");
ok(page.status === 404, "draft preview hidden when signed out");
page = await fetch(base + "/press/" + d1.slug + "?preview=1", { headers: { cookie: a2.cookie } });
ok(page.status === 200, "draft preview works for a signed-in team member");

console.log("Permissions");
r = await a2.req("PUT", "/api/admin/articles/" + d1.id, { ...art("Hijack"), updatedAt: d1.updatedAt });
ok(r.status === 403, "admin cannot edit another admin's article");
r = await a2.req("DELETE", "/api/admin/articles/" + d1.id);
ok(r.status === 403, "admin cannot delete another admin's article");
r = await a2.req("GET", "/api/admin/articles");
ok(r.j.items.find((x) => x.id === d1.id)?.canEdit === false, "other people's articles are marked view-only for an admin");
r = await sup.req("PUT", "/api/admin/articles/" + d1.id, { ...art("Edited by super-admin"), updatedAt: d1.updatedAt });
ok(r.status === 200 && r.j.article.title === "Edited by super-admin" && r.j.article.author === A1, "super-admin edits any article; author is kept");
r = await a1.req("PUT", "/api/admin/articles/" + d1.id, { ...art("Stale edit"), updatedAt: d1.updatedAt });
ok(r.status === 409, "stale edit is blocked instead of overwriting someone else's changes");
r = await a1.req("PUT", "/api/admin/articles/" + d1.id, { ...art("Own edit"), updatedAt: (await a1.req("GET", "/api/admin/articles/" + d1.id)).j.article.updatedAt });
ok(r.status === 200, "admin edits own article");
r = await sup.req("DELETE", "/api/admin/articles/" + d1b.id);
ok(r.status === 200, "super-admin deletes any article");

console.log("Password");
r = await a2.req("POST", "/api/auth/password", { current: "nope", next: "NewPassword123" });
ok(r.status === 400, "password change needs the current password");
r = await a2.req("POST", "/api/auth/password", { current: PW, next: "short1" });
ok(r.status === 400, "too-short password refused");

console.log("Lockout");
const lk = new Client();
const LOCK = process.argv.includes("--prod") ? "lockout-check@example.com" : "serviceclient@kennysinternational.com";
for (let i = 0; i < 5; i++) await lk.login(LOCK, "bad-" + i);
r = await lk.login(LOCK);
ok(r.status === 429, "account locked for 15 minutes after 5 wrong passwords, even with the right one");

console.log("Sign out");
await a1.req("POST", "/api/auth/logout", {});
ok((await a1.req("GET", "/api/admin/articles")).status === 401, "signed-out session no longer works");

if (!keep) {
  for (const a of [d1, p1]) await sup.req("DELETE", "/api/admin/articles/" + a.id);
  console.log("cleaned up test articles");
}
console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
