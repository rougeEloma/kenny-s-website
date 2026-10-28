// Sign-in, sessions and roles for the /vogin dashboard.
// Users and their default password hashes live in the KP_USERS environment variable;
// a password changed from the dashboard is stored (hashed) in the "kp-users" blob store.
import crypto from "node:crypto";
import { getStore } from "@netlify/blobs";

const COOKIE = "kp_session";
const SESSION_HOURS = 8;
const MAX_FAILS = 5;
const LOCK_MINUTES = 15;

const env = (k) => (globalThis.Netlify ? Netlify.env.get(k) : process.env[k]);
const usersStore = () => getStore({ name: "kp-users", consistency: "strong" });
const authStore = () => getStore({ name: "kp-auth", consistency: "strong" });

function secret() {
  const s = env("KP_SESSION_SECRET");
  if (!s || s.length < 32) throw new Error("KP_SESSION_SECRET is missing");
  return s;
}

export function users() {
  const raw = env("KP_USERS");
  if (!raw) throw new Error("KP_USERS is missing");
  return JSON.parse(raw).map((u) => ({ email: u.e.toLowerCase(), role: u.r, name: u.n, defaultHash: u.h }));
}

export function findUser(email) {
  email = String(email || "").trim().toLowerCase();
  return users().find((u) => u.email === email) || null;
}

// ---------- password hashing (scrypt) ----------
const N = 16384, R = 8, P = 1, LEN = 64;
export function hashPassword(pw) {
  const salt = crypto.randomBytes(16);
  const h = crypto.scryptSync(String(pw), salt, LEN, { N, r: R, p: P });
  return `scrypt$${N}$${R}$${P}$${salt.toString("base64")}$${h.toString("base64")}`;
}
export function verifyPassword(pw, stored) {
  try {
    const [alg, n, r, p, salt, hash] = String(stored).split("$");
    if (alg !== "scrypt") return false;
    const expected = Buffer.from(hash, "base64");
    const got = crypto.scryptSync(String(pw), Buffer.from(salt, "base64"), expected.length, { N: +n, r: +r, p: +p });
    return crypto.timingSafeEqual(got, expected);
  } catch { return false; }
}

async function currentHash(user) {
  const override = await usersStore().get(`pw/${user.email}`, { type: "json" });
  return override?.h || user.defaultHash;
}
const pwVersion = (hash) => crypto.createHash("sha256").update(hash).digest("base64url").slice(0, 12);

export async function setPassword(user, newPw) {
  await usersStore().setJSON(`pw/${user.email}`, { h: hashPassword(newPw), updatedAt: new Date().toISOString() });
}

// ---------- lockout after repeated failures ----------
async function lockState(email) {
  return (await authStore().get(`lock/${email}`, { type: "json" })) || { fails: 0, until: 0 };
}
async function recordFail(email) {
  const s = await lockState(email);
  const fails = (s.until && s.until < Date.now()) ? 1 : s.fails + 1;
  const until = fails >= MAX_FAILS ? Date.now() + LOCK_MINUTES * 60000 : 0;
  await authStore().setJSON(`lock/${email}`, { fails, until });
  return { fails, until };
}
async function clearFails(email) { await authStore().delete(`lock/${email}`); }

export async function login(email, password) {
  const user = findUser(email);
  const key = String(email || "").trim().toLowerCase();
  const lock = await lockState(key);
  if (lock.until && lock.until > Date.now()) {
    return { ok: false, status: 429, error: `Too many attempts. Try again in ${Math.ceil((lock.until - Date.now()) / 60000)} minutes.` };
  }
  const hash = user ? await currentHash(user) : hashPassword("dummy-to-equalise-timing");
  if (!user || !verifyPassword(password, hash)) {
    await recordFail(key);
    return { ok: false, status: 401, error: "Incorrect email or password." };
  }
  await clearFails(key);
  return { ok: true, user, cookie: sessionCookie(user, hash) };
}

// ---------- session cookie ----------
function sign(payload) {
  const body = Buffer.from(JSON.stringify(payload)).toString("base64url");
  const mac = crypto.createHmac("sha256", secret()).update(body).digest("base64url");
  return `${body}.${mac}`;
}
function unsign(token) {
  if (!token || !token.includes(".")) return null;
  const [body, mac] = token.split(".");
  const expected = crypto.createHmac("sha256", secret()).update(body).digest("base64url");
  const a = Buffer.from(mac), b = Buffer.from(expected);
  if (a.length !== b.length || !crypto.timingSafeEqual(a, b)) return null;
  try { return JSON.parse(Buffer.from(body, "base64url").toString()); } catch { return null; }
}
function sessionCookie(user, hash) {
  const exp = Date.now() + SESSION_HOURS * 3600000;
  const token = sign({ e: user.email, exp, pv: pwVersion(hash) });
  return `${COOKIE}=${token}; Path=/; HttpOnly; Secure; SameSite=Strict; Max-Age=${SESSION_HOURS * 3600}`;
}
export const clearCookie = () => `${COOKIE}=; Path=/; HttpOnly; Secure; SameSite=Strict; Max-Age=0`;

function readCookie(req) {
  const raw = req.headers.get("cookie") || "";
  const m = raw.split(/;\s*/).find((c) => c.startsWith(COOKIE + "="));
  return m ? m.slice(COOKIE.length + 1) : null;
}

// Returns the signed-in user or null. Sessions end when the password changes.
export async function sessionUser(req) {
  const p = unsign(readCookie(req));
  if (!p || !p.exp || p.exp < Date.now()) return null;
  const user = findUser(p.e);
  if (!user) return null;
  if (pwVersion(await currentHash(user)) !== p.pv) return null;
  return { email: user.email, role: user.role, name: user.name };
}

// ---------- request guards ----------
// The URL path without "/index.html", ".html" or a trailing slash (local dev probes these variants).
export const cleanPath = (req) => new URL(req.url).pathname.replace(/\/index\.html?$/, "").replace(/\.html?$/, "").replace(/\/+$/, "") || "/";
export const json = (data, status = 200, headers = {}) =>
  new Response(JSON.stringify(data), { status, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store", ...headers } });

// Mutating requests must come from our own pages (custom header + same-origin check).
export function sameOrigin(req) {
  if (req.method === "GET" || req.method === "HEAD") return true;
  if (req.headers.get("x-kp") !== "1") return false;
  const origin = req.headers.get("origin");
  if (origin && origin !== new URL(req.url).origin) return false;
  return true;
}

export async function requireUser(req) {
  if (!sameOrigin(req)) return { error: json({ error: "Forbidden" }, 403) };
  const user = await sessionUser(req);
  if (!user) return { error: json({ error: "Please sign in again." }, 401) };
  return { user };
}

// Wraps a handler so unexpected errors are logged but never shown to visitors.
export const safe = (fn) => async (req, context) => {
  try { return await fn(req, context); }
  catch (e) {
    console.error("Unhandled error:", e && e.stack || e);
    const wantsJson = new URL(req.url).pathname.startsWith("/api/");
    return wantsJson
      ? json({ error: "Something went wrong on our side. Please try again in a moment." }, 500)
      : new Response("<!doctype html><meta charset=utf-8><title>Temporary problem</title><p style=\"font-family:sans-serif;padding:40px\">This page is temporarily unavailable. Please try again in a moment.</p>", { status: 500, headers: { "content-type": "text/html; charset=utf-8", "cache-control": "no-store" } });
  }
};

export const isSuper = (u) => u.role === "super";
export const canEdit = (u, article) => isSuper(u) || article.author === u.email;
