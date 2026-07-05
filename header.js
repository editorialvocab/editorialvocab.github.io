/**
 * header.js — Editorial Vocabulary site header
 * Usage: <script src="/header.js"></script>  (place at top of <body>)
 *
 * Renders a sticky top-nav matching the main site's dark theme.
 * The "Today's Word" link auto-updates via updateHeaderWordLink(date, lang).
 */
(function () {
    var BASE   = "https://editorialvocab.github.io";
    var DOCS   = BASE + "/docs";
    var APP    = "https://play.google.com/store/apps/details?id=megaminds.dailyeditorialword";
    var EBOOKS = BASE + "/ebooks/";

    // ── Styles ───────────────────────────────────────────────────────
    var css = `
.ev-header {
    position: sticky;
    top: 0;
    z-index: 200;
    background: rgba(10,15,30,0.97);
    border-bottom: 1px solid #1e2840;
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}
.ev-header-inner {
    max-width: 1100px;
    margin: 0 auto;
    padding: 0 20px;
    height: 56px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
}
.ev-logo {
    display: flex;
    align-items: center;
    gap: 8px;
    text-decoration: none;
    flex-shrink: 0;
}
.ev-logo-icon { font-size: 1.2rem; }
.ev-logo-text {
    font-size: 0.95rem;
    font-weight: 700;
    color: #f0ece2;
    white-space: nowrap;
}
.ev-logo-text span { color: #c9a84c; }
.ev-nav-links {
    display: flex;
    align-items: center;
    gap: 4px;
    flex: 1;
    justify-content: center;
    flex-wrap: nowrap;
    overflow: hidden;
}
.ev-nav-links a {
    font-size: 0.8rem;
    color: #94a3b8;
    text-decoration: none;
    padding: 5px 10px;
    border-radius: 6px;
    white-space: nowrap;
    transition: color .15s, background .15s;
}
.ev-nav-links a:hover,
.ev-nav-links a.ev-active {
    color: #c9a84c;
    background: rgba(201,168,76,0.08);
}
.ev-nav-right {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-shrink: 0;
}
.ev-word-btn {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-size: 0.75rem;
    font-weight: 600;
    color: #c9a84c;
    border: 1px solid rgba(201,168,76,0.35);
    border-radius: 6px;
    padding: 5px 12px;
    text-decoration: none;
    transition: background .15s, border-color .15s;
    white-space: nowrap;
}
.ev-word-btn:hover {
    background: rgba(201,168,76,0.1);
    border-color: #c9a84c;
    text-decoration: none;
}
.ev-app-btn {
    display: inline-flex;
    align-items: center;
    font-size: 0.75rem;
    font-weight: 700;
    color: #0a0f1e;
    background: #c9a84c;
    border-radius: 6px;
    padding: 5px 12px;
    text-decoration: none;
    transition: background .15s;
    white-space: nowrap;
}
.ev-app-btn:hover { background: #d4b96a; text-decoration: none; }

.ev-ebook-btn {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    font-size: 0.75rem;
    font-weight: 700;
    color: #25D366;
    border: 1px solid rgba(37,211,102,0.4);
    border-radius: 6px;
    padding: 5px 12px;
    text-decoration: none;
    transition: background .15s, border-color .15s;
    white-space: nowrap;
}
.ev-ebook-btn:hover {
    background: rgba(37,211,102,0.1);
    border-color: #25D366;
    text-decoration: none;
}

/* Mobile: hide middle nav links, keep logo + right buttons */
@media (max-width: 600px) {
    .ev-nav-links { display: none; }
    .ev-logo-text { font-size: 0.85rem; }
}

/* Narrow phones: 3 right-side buttons + logo needs tighter spacing */
@media (max-width: 400px) {
    .ev-header-inner { padding: 0 12px; gap: 6px; }
    .ev-nav-right { gap: 4px; }
    .ev-word-btn, .ev-ebook-btn, .ev-app-btn {
        padding: 5px 8px;
        font-size: 0.68rem;
    }
    /* Icon-only Today's Word button to save space; eBooks + App keep labels */
    #ev-todays-word span.ev-label { display: none; }
}
`;

    // ── Determine active page link ───────────────────────────────────
    var path = window.location.pathname;
    function isActive(href) {
        var url = href.replace(BASE, "");
        return path === url || path.startsWith(url.replace(/\/$/, "") + "/");
    }
    function navLink(href, label) {
        var cls = isActive(href) ? ' class="ev-active"' : '';
        return '<a href="' + href + '"' + cls + '>' + label + '</a>';
    }

    // ── Detect bn/hn from the current page path, so the eBooks link
    // lands the visitor on the matching language edition instead of
    // whatever they last had saved (or the bn default). ─────────────
    function detectLang() {
        if (path.indexOf("/bn/") !== -1) return "bn";
        if (path.indexOf("/hn/") !== -1) return "hn";
        return null;
    }
    var pageLang    = detectLang();
    var ebooksHref  = EBOOKS + (pageLang ? ("?lang=" + pageLang) : "");

    // ── Build HTML ───────────────────────────────────────────────────
    var todayBtn = '<a id="ev-todays-word" class="ev-word-btn" href="' + DOCS + '/words/" target="_blank" rel="noopener">📖 <span class="ev-label">Today\'s Word</span></a>';

    var html = `
<header class="ev-header">
  <div class="ev-header-inner">
    <a class="ev-logo" href="${BASE}/">
      <span class="ev-logo-icon">📖</span>
      <span class="ev-logo-text">Editorial <span>Vocab</span></span>
    </a>
    <nav class="ev-nav-links" aria-label="Site navigation">
      ${navLink(BASE + "/", "Home")}
      ${navLink(DOCS + "/words/", "All Words")}
      ${navLink(DOCS + "/bcs-vocabulary/", "BCS Vocab")}
      ${navLink(DOCS + "/upsc-vocabulary/", "UPSC Vocab")}
      ${navLink(BASE + "/profile/", "About")}
    </nav>
    <div class="ev-nav-right">
      ${todayBtn}
      <a class="ev-ebook-btn" href="${ebooksHref}">📖 eBooks</a>
      <a class="ev-app-btn" href="${APP}" target="_blank" rel="noopener">↓ App</a>
    </div>
  </div>
</header>`;

    // ── Inject styles + markup ───────────────────────────────────────
    var styleEl = document.createElement("style");
    styleEl.textContent = css;
    document.head.appendChild(styleEl);

    document.write(html);
})();

/**
 * Call this from app.js / page JS to keep the "Today's Word" link
 * pointing at the correct date and language after region detection.
 *
 * Example:
 *   updateHeaderWordLink("10-06-2026", "hn");
 */
function updateHeaderWordLink(date, lang) {
    var url = "https://editorialvocab.github.io/docs/words/" + date + "/" + lang + "/";
    var el  = document.getElementById("ev-todays-word");
    if (el) el.href = url;
}
