// Pre-hydration language detection.
// Runs synchronously BEFORE React mounts so <html lang> and <html data-lang>
// reflect the user's preferred language from the very first paint.
// Detection order matches src/lib/i18n.tsx:
//   1. localStorage('puente.lang')
//   2. Cookie 'puente.lang'
//   3. navigator.languages / navigator.language
//   4. Fallback to 'en'
//
// Externalized from index.html so the production CSP can use script-src 'self'
// (no 'unsafe-inline'). See nginx.conf.template + ultrareview bug_001 on PR #52.

(function () {
  var SUPPORTED = ["en", "es"];
  var KEY = "puente.lang";
  var lang = null;

  try {
    var ls = window.localStorage.getItem(KEY);
    if (ls && SUPPORTED.indexOf(ls) !== -1) lang = ls;
  } catch (e) {}

  if (!lang) {
    try {
      var match = document.cookie
        .split("; ")
        .find(function (r) { return r.indexOf(KEY + "=") === 0; });
      if (match) {
        var val = decodeURIComponent(match.slice(KEY.length + 1));
        if (SUPPORTED.indexOf(val) !== -1) lang = val;
      }
    } catch (e) {}
  }

  if (!lang) {
    var cands = (navigator.languages && navigator.languages.length)
      ? navigator.languages
      : [navigator.language || "en"];
    for (var i = 0; i < cands.length; i++) {
      var base = String(cands[i] || "").toLowerCase().split("-")[0];
      if (SUPPORTED.indexOf(base) !== -1) { lang = base; break; }
    }
  }

  if (!lang) lang = "en";
  document.documentElement.lang = lang;
  document.documentElement.setAttribute("data-lang", lang);
})();
