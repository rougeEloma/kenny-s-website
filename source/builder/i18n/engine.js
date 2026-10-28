/* Kenny's International: FRA | ENG switch. English is written in the pages; this swaps in French. */
(function(){
  var FR = __DICT__;
  var MEN = ["January","February","March","April","May","June","July","August","September","October","November","December"];
  var MFR = ["janvier","février","mars","avril","mai","juin","juillet","août","septembre","octobre","novembre","décembre"];
  var KEY = "kp-lang", ATTRS = ["alt","aria-label","placeholder","title"];
  var SKIP = /^(SCRIPT|STYLE|NOSCRIPT|TEXTAREA|INPUT)$/;
  var doneText = [], doneAttr = [];
  var root = document.documentElement;

  function pick(){
    try { var v = localStorage.getItem(KEY); if (v === "fr" || v === "en") return v; } catch (e) {}
    var l = (navigator.languages && navigator.languages[0]) || navigator.language || "en";
    return /^fr/i.test(l) ? "fr" : "en";
  }
  var lang = pick();

  function norm(s){ return String(s).replace(/\s+/g, " ").trim(); }
  function tr(s){
    var k = norm(s), m;
    if (!k || !/[A-Za-z]/.test(k)) return null;
    if (Object.prototype.hasOwnProperty.call(FR, k)) return FR[k];
    if ((m = /^(\d{1,2}) ([A-Z][a-z]+) (\d{4})$/.exec(k)) && MEN.indexOf(m[2]) >= 0) return m[1] + " " + MFR[MEN.indexOf(m[2])] + " " + m[3];
    if ((m = /^(\d+) (houses|brands|stores)$/.exec(k))) return m[1] + " " + { houses: "maisons", brands: "marques", stores: "magasins" }[m[2]];
    if ((m = /^Page (\d+) of (\d+)$/.exec(k))) return "Page " + m[1] + " sur " + m[2];
    if ((m = /^Store (\d+)$/.exec(k))) return "Magasin " + m[1];
    if ((m = /^(.+), store details$/.exec(k))) return m[1] + ", informations du magasin";
    if (k.indexOf(" · ") > 0) {
      var changed = false, parts = k.split(" · ").map(function(p){ var t = tr(p); if (t != null) { changed = true; return t; } return p; });
      if (changed) return parts.join(" · ");
    }
    return null;
  }
  function skipped(el){
    for (; el && el.nodeType === 1; el = el.parentNode) {
      if (SKIP.test(el.tagName) || el.hasAttribute("data-noi18n")) return true;
    }
    return false;
  }
  function doText(n){
    if (n.__kpEn != null) return;
    var t = tr(n.nodeValue);
    if (t == null) return;
    var src = n.nodeValue;
    n.__kpEn = src;
    n.nodeValue = src.match(/^\s*/)[0] + t + src.match(/\s*$/)[0];
    doneText.push(n);
  }
  function doEl(el){
    for (var i = 0; i < ATTRS.length; i++) {
      var a = ATTRS[i], v = el.getAttribute(a);
      if (v == null) continue;
      var store = el.__kpAttr || (el.__kpAttr = {});
      if (store[a] != null) continue;
      var t = tr(v);
      if (t == null) continue;
      store[a] = v; el.setAttribute(a, t);
      if (doneAttr.indexOf(el) < 0) doneAttr.push(el);
    }
  }
  function walk(node){
    if (node.nodeType === 3) { if (!skipped(node.parentNode)) doText(node); return; }
    if (node.nodeType !== 1 || skipped(node)) return;
    doEl(node);
    var w = document.createTreeWalker(node, NodeFilter.SHOW_ELEMENT | NodeFilter.SHOW_TEXT, {
      acceptNode: function(n){ return n.nodeType === 1 && (SKIP.test(n.tagName) || n.hasAttribute("data-noi18n")) ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT; }
    });
    var n;
    while ((n = w.nextNode())) { if (n.nodeType === 3) doText(n); else doEl(n); }
  }
  var titleEn = document.title, meta = document.querySelector('meta[name="description"]'), metaEn = meta && meta.getAttribute("content");
  function toFr(){
    walk(document.body);
    var t = tr(titleEn); if (t) document.title = t;
    if (meta) { var d = tr(metaEn); if (d) meta.setAttribute("content", d); }
  }
  function toEn(){
    doneText.forEach(function(n){ if (n.__kpEn != null) { n.nodeValue = n.__kpEn; n.__kpEn = null; } });
    doneAttr.forEach(function(el){ var s = el.__kpAttr || {}; Object.keys(s).forEach(function(a){ el.setAttribute(a, s[a]); }); el.__kpAttr = null; });
    doneText = []; doneAttr = [];
    document.title = titleEn; if (meta) meta.setAttribute("content", metaEn);
  }
  function mark(){
    root.lang = lang;
    [].slice.call(document.querySelectorAll("[data-lang]")).forEach(function(b){ b.setAttribute("aria-pressed", b.getAttribute("data-lang") === lang ? "true" : "false"); });
  }
  function set(l){
    if (l === lang) return;
    lang = l;
    try { localStorage.setItem(KEY, l); } catch (e) {}
    if (l === "fr") toFr(); else toEn();
    mark();
  }
  new MutationObserver(function(list){
    if (lang !== "fr") return;
    list.forEach(function(m){ [].forEach.call(m.addedNodes, walk); });
  }).observe(document.body, { childList: true, subtree: true });
  document.addEventListener("click", function(e){
    var b = e.target.closest && e.target.closest("[data-lang]");
    if (b) { e.preventDefault(); set(b.getAttribute("data-lang")); }
  });
  if (lang === "fr") toFr();
  mark();
  root.classList.remove("i18n-wait");
})();
