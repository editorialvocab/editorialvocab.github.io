/**
 * footer.js — Editorial Vocabulary site footer
 * Usage: <script src="/footer.js"></script>  (place at bottom of <body>)
 *
 * Renders a clean 3-column footer matching the main site's dark theme.
 * Also injects a scroll-to-top button.
 */
(function () {
    var BASE  = "https://editorialvocab.github.io";
    var DOCS  = BASE + "/docs";
    var APP   = "https://play.google.com/store/apps/details?id=megaminds.dailyeditorialword";
    var YEAR  = new Date().getFullYear();

    // ── Styles ───────────────────────────────────────────────────────
    var css = `
.ev-footer {
    border-top: 1px solid #1e2840;
    background: #060b18;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    padding: 48px 20px 24px;
    margin-top: 64px;
}
.ev-footer-inner {
    max-width: 1100px;
    margin: 0 auto;
    display: grid;
    grid-template-columns: 1.6fr 1fr 1fr 1fr;
    gap: 40px;
}
.ev-footer-brand .ev-footer-logo {
    font-size: 1.05rem;
    font-weight: 700;
    color: #f0ece2;
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    margin-bottom: 10px;
}
.ev-footer-brand .ev-footer-logo span { color: #c9a84c; }
.ev-footer-tagline {
    font-size: 0.78rem;
    color: #4b5563;
    font-style: italic;
    margin-bottom: 14px;
    line-height: 1.5;
}
.ev-footer-apps {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    margin-bottom: 14px;
}
.ev-footer-apps a {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-size: 0.72rem;
    color: #6b7280;
    border: 1px solid #1e2840;
    border-radius: 6px;
    padding: 4px 10px;
    text-decoration: none;
    transition: border-color .15s, color .15s;
}
.ev-footer-apps a:hover { border-color: #c9a84c; color: #c9a84c; }
.ev-footer-social {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
}
.ev-footer-social a {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    font-size: 0.7rem;
    color: #4b5563;
    text-decoration: none;
    transition: color .15s;
}
.ev-footer-social a:hover { color: #c9a84c; }

.ev-footer-col h4 {
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #6b7280;
    margin-bottom: 14px;
}
.ev-footer-col a {
    display: block;
    font-size: 0.8rem;
    color: #4b5563;
    text-decoration: none;
    margin-bottom: 8px;
    transition: color .15s;
}
.ev-footer-col a:hover { color: #c9a84c; }

.ev-footer-bottom {
    max-width: 1100px;
    margin: 32px auto 0;
    padding-top: 20px;
    border-top: 1px solid #1e2840;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 8px;
    font-size: 0.72rem;
    color: #374151;
}
.ev-footer-bottom a { color: #4b5563; text-decoration: none; }
.ev-footer-bottom a:hover { color: #c9a84c; }

/* Scroll-to-top button */
#ev-back-top {
    position: fixed;
    bottom: 28px;
    right: 24px;
    width: 40px;
    height: 40px;
    background: #c9a84c;
    color: #0a0f1e;
    border: none;
    border-radius: 50%;
    font-size: 1.1rem;
    font-weight: 700;
    cursor: pointer;
    display: none;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 14px rgba(0,0,0,0.4);
    transition: background .15s, transform .15s;
    z-index: 999;
}
#ev-back-top.ev-visible { display: flex; }
#ev-back-top:hover { background: #d4b96a; transform: translateY(-2px); }

@media (max-width: 768px) {
    .ev-footer-inner { grid-template-columns: 1fr 1fr; gap: 28px; }
}
@media (max-width: 480px) {
    .ev-footer-inner { grid-template-columns: 1fr; }
}
`;

    // ── Build HTML ───────────────────────────────────────────────────
    var html = `
<footer class="ev-footer">
  <div class="ev-footer-inner">

    <!-- Brand column -->
    <div class="ev-footer-brand">
      <a class="ev-footer-logo" href="${BASE}/">
        📖 Editorial <span>Vocab</span>
      </a>
      <p class="ev-footer-tagline">"Don't just read editorials — master them."</p>
      <div class="ev-footer-apps">
        <a href="${APP}" target="_blank" rel="noopener">📱 Google Play</a>
        <a href="https://muslimsday.com/" target="_blank" rel="noopener">🕌 Muslims Day</a>
      </div>
      <div class="ev-footer-social">
        <a href="https://github.com/editorialvocab" target="_blank" rel="noopener">⌥ GitHub</a>
        <a href="https://linkedin.com/in/promahadihasan" target="_blank" rel="noopener">in LinkedIn</a>
        <a href="https://twitter.com/promahadihasan" target="_blank" rel="noopener">𝕏 Twitter</a>
        <a href="https://instagram.com/promahadihasan" target="_blank" rel="noopener">◎ Instagram</a>
      </div>
    </div>

    <!-- Vocabulary column -->
    <div class="ev-footer-col">
      <h4>Vocabulary</h4>
      <a href="${DOCS}/words/">All Words</a>
      <a href="${DOCS}/bcs-vocabulary/">BCS Archive</a>
      <a href="${DOCS}/upsc-vocabulary/">UPSC Archive</a>
    </div>

    <!-- Links column -->
    <div class="ev-footer-col">
      <h4>Links</h4>
      <a href="${BASE}/">Home</a>
      <a href="${BASE}/profile/">About Mahadi</a>
      <a href="${BASE}/blog/">Blog</a>
      <a href="${BASE}/privacy-policy/">Privacy Policy</a>
      <a href="${BASE}/terms-conditions/">Terms</a>
    </div>

    <!-- Contact column -->
    <div class="ev-footer-col" id="contract">
      <h4>Contact</h4>
      <a href="mailto:mahadi129727@gmail.com">mahadi129727@gmail.com</a>
      <a href="tel:+8801713819046">+880 1713 819046</a>
      <a href="${BASE}/profile/" style="color:#4b5563;font-size:0.72rem;margin-top:4px;">
        Akur Takur Para, Tangail Sadar,<br>Tangail, Bangladesh
      </a>
    </div>

  </div>

  <div class="ev-footer-bottom">
    <span>© ${YEAR} Editorial Vocabulary · Mahadi Hasan · Tangail, Bangladesh</span>
    <span>
      <a href="${BASE}/privacy-policy/">Privacy</a> ·
      <a href="${BASE}/terms-conditions/">Terms</a> ·
      <a href="${APP}" target="_blank" rel="noopener">App</a>
    </span>
  </div>
</footer>

<button id="ev-back-top" aria-label="Back to top" title="Back to top">↑</button>`;

    // ── Inject styles + markup ───────────────────────────────────────
    var styleEl = document.createElement("style");
    styleEl.textContent = css;
    document.head.appendChild(styleEl);

    document.write(html);

    // ── Scroll-to-top logic ──────────────────────────────────────────
    window.addEventListener("load", function () {
        var btn = document.getElementById("ev-back-top");
        if (!btn) return;
        window.addEventListener("scroll", function () {
            btn.classList.toggle("ev-visible", window.scrollY > 300);
        }, { passive: true });
        btn.addEventListener("click", function () {
            window.scrollTo({ top: 0, behavior: "smooth" });
        });
    });
})();
