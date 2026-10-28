// /api/auth/login, /api/auth/logout, /api/auth/me, /api/auth/password
import { login, clearCookie, sessionUser, requireUser, sameOrigin, json, findUser, verifyPassword, setPassword, cleanPath, safe } from "./_lib/auth.mjs";
import { getStore } from "@netlify/blobs";

export default safe(async (req, context) => {
  const action = cleanPath(req).split("/").pop();

  if (action === "login" && req.method === "POST") {
    if (!sameOrigin(req)) return json({ error: "Forbidden" }, 403);
    let body = {};
    try { body = await req.json(); } catch {}
    const r = await login(body.email, body.password);
    if (!r.ok) return json({ error: r.error }, r.status);
    return json({ user: { email: r.user.email, role: r.user.role, name: r.user.name } }, 200, { "set-cookie": r.cookie });
  }

  if (action === "logout" && req.method === "POST") {
    return json({ ok: true }, 200, { "set-cookie": clearCookie() });
  }

  if (action === "me" && req.method === "GET") {
    const user = await sessionUser(req);
    return user ? json({ user }) : json({ user: null }, 401);
  }

  if (action === "password" && req.method === "POST") {
    const { user, error } = await requireUser(req);
    if (error) return error;
    let body = {};
    try { body = await req.json(); } catch {}
    const full = findUser(user.email);
    const override = await getStore({ name: "kp-users", consistency: "strong" }).get(`pw/${user.email}`, { type: "json" });
    if (!verifyPassword(body.current, override?.h || full.defaultHash)) return json({ error: "Your current password is incorrect." }, 400);
    const next = String(body.next || "");
    if (next.length < 10) return json({ error: "The new password must be at least 10 characters long." }, 400);
    if (!/[A-Za-z]/.test(next) || !/[0-9]/.test(next)) return json({ error: "Use at least one letter and one number." }, 400);
    if (next === body.current) return json({ error: "The new password must be different." }, 400);
    await setPassword(full, next);
    return json({ ok: true }, 200, { "set-cookie": clearCookie() });
  }

  return json({ error: "Not found" }, 404);
});

export const config = { path: "/api/auth/:action" };
