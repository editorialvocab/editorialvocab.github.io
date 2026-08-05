"""
web_generator.py  v2
════════════════════
Generates static HTML pages pushed to editorialvocab.github.io/docs/

PAGES GENERATED
───────────────
  docs/words/DD-MM-YYYY/bn/index.html      Bengali WOTD + vocab
  docs/words/DD-MM-YYYY/hn/index.html      Hindi WOTD + vocab
  docs/quiz/DD-MM-YYYY/bn/index.html       Bengali quiz (10 MCQ, answers in <details>)
  docs/quiz/DD-MM-YYYY/hn/index.html       Hindi quiz
  docs/bcs-vocabulary/index.html           Incremental BCS/PSC archive
  docs/upsc-vocabulary/index.html          Incremental UPSC/SSC archive
  docs/words/index.html                    JS redirect → BCS or UPSC archive
  docs/words/MM-YYYY/bn/index.html         Monthly BCS word list (SEO landing page)
  docs/words/MM-YYYY/hn/index.html         Monthly UPSC word list (SEO landing page)
  docs/sitemap.xml                         Auto-regenerated
  docs/.nojekyll                           Disables GitHub Jekyll

BUGS FIXED vs original generate_web_vocab_page() in main.py
─────────────────────────────────────────────────────────────
1. meaning_key: "bengali_meaning" → tries bangla_meaning/bengali_meaning/meaning
2. Bare HTML → full meta tags, Open Graph, schema.org, CSS, definition/synonyms/
   antonyms/example, vocab list, app CTA, day navigation
3. No .nojekyll → ensure_nojekyll() creates it
4. No sitemap update → update_sitemap() walks docs/ and rebuilds each run
5. No internal links → every page has ← Yesterday | All Words | Tomorrow → nav
6. DOCS_URL constant added — matches BASE_URL since GitHub Pages publishes
   directly from the docs/ folder (no /docs/ prefix in live URLs)
7. Nav is lang-aware: bn → BCS Vocabulary, hn → UPSC Vocabulary
8. words/index.html uses localStorage redirect (region saved by app.js)

USAGE IN main.py — see main_integration_patch.py
"""

from __future__ import annotations

import html
import json
import logging
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

log = logging.getLogger(__name__)

# ── Constants ─────────────────────────────────────────────────────────────────
DOCS_ROOT = Path("docs")
BASE_URL  = "https://editorialvocab.github.io"
# REVERTED: live testing confirmed GitHub Pages actually serves from the
# REPO ROOT, not from a /docs publish-source folder (despite what the
# Pages settings screen text suggested). docs/words/... on disk correctly
# maps to https://editorialvocab.github.io/docs/words/... live — this was
# the original, correct behavior. Do not remove "/docs" from this constant.
DOCS_URL  = f"{BASE_URL}/docs"
APP_URL   = "https://play.google.com/store/apps/details?id=megaminds.dailyeditorialword"
SITE_NAME = "Editorial Vocabulary"

_EXAM_LOG = {
    "bcs":  DOCS_ROOT / "bcs-vocabulary"  / "_entries.json",
    "upsc": DOCS_ROOT / "upsc-vocabulary" / "_entries.json",
}

# ── Shared CSS (inline — zero external dependencies, fast load) ───────────────
_CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
  font-size:16px;line-height:1.7;background:#0a0f1e;color:#d4d8e8;padding-bottom:48px}
a{color:#c9a84c;text-decoration:none}a:hover{text-decoration:underline}
.top-nav{position:sticky;top:0;z-index:100;background:rgba(10,15,30,.95);
  border-bottom:1px solid #1e2840;padding:12px 20px;display:flex;
  align-items:center;justify-content:space-between;backdrop-filter:blur(8px)}
.nav-logo{font-weight:700;color:#c9a84c;font-size:.95rem}
.nav-logo span{color:#d4d8e8}
.nav-links{display:flex;gap:16px;font-size:.82rem;flex-wrap:wrap}
.nav-links a{color:#94a3b8}.nav-links a:hover,.nav-active{color:#c9a84c!important;text-decoration:none}
.container{max-width:720px;margin:0 auto;padding:32px 20px}
.breadcrumb{font-size:.75rem;color:#6b7280;margin-bottom:20px}
.breadcrumb a{color:#6b7280}.breadcrumb a:hover{color:#c9a84c}
.breadcrumb span{margin:0 6px}
.source-badge{display:inline-block;font-size:.65rem;font-weight:700;
  padding:3px 10px;border-radius:100px;letter-spacing:.06em;
  text-transform:uppercase;font-family:monospace;margin-bottom:12px}
.badge-pyq{background:rgba(201,168,76,.18);color:#c9a84c;border:1px solid rgba(201,168,76,.3)}
.badge-edit{background:rgba(100,116,139,.18);color:#94a3b8;border:1px solid #1e2840}
.word-title{font-size:clamp(2rem,5vw,3rem);font-weight:800;color:#f0ece2;
  line-height:1.15;margin-bottom:6px;font-family:Georgia,serif}
.page-title{font-family:Georgia,serif;font-size:1.8rem;font-weight:800;
  color:#f0ece2;margin-bottom:8px}
.page-sub{font-size:.85rem;color:#6b7280;margin-bottom:24px}
.word-phonetic{font-size:1rem;color:#94a3b8;margin-bottom:4px;font-style:italic}
.word-pos{display:inline-block;font-size:.72rem;font-weight:600;padding:2px 10px;
  border-radius:100px;background:rgba(79,142,247,.12);color:#4f8ef7;
  border:1px solid rgba(79,142,247,.2);margin-bottom:14px}
.word-divider{height:1px;background:#1e2840;margin:20px 0}
.section{margin-bottom:24px}
.section-label{font-size:.65rem;font-weight:700;letter-spacing:.14em;
  text-transform:uppercase;color:#4b5563;margin-bottom:8px}
.native-meaning{font-size:1.3rem;font-weight:600;color:#c9a84c;
  font-family:Georgia,serif;margin-bottom:8px}
.definition{font-size:.95rem;color:#b8bdd4;line-height:1.75}
.example{font-size:.9rem;color:#94a3b8;font-style:italic;line-height:1.7;
  padding:12px 16px;border-left:3px solid #1e2840;
  background:rgba(255,255,255,.02);border-radius:0 8px 8px 0}
.chip-row{display:flex;flex-wrap:wrap;gap:8px}
.chip{font-size:.78rem;padding:4px 12px;border-radius:100px;
  border:1px solid #1e2840;background:rgba(255,255,255,.03);color:#94a3b8}
.chip:hover{border-color:#c9a84c;color:#c9a84c}
.vocab-section{background:#111827;border:1px solid #1e2840;
  border-radius:12px;padding:20px;margin:28px 0}
.vocab-section h2{font-size:.8rem;font-weight:700;color:#6b7280;
  letter-spacing:.1em;text-transform:uppercase;margin-bottom:14px}
.vocab-row{display:flex;gap:10px;padding:9px 0;
  border-bottom:1px solid #1a2035;align-items:baseline}
.vocab-row:last-child{border-bottom:none}
.vocab-num{font-family:monospace;font-size:.7rem;color:#374151;min-width:22px}
.vocab-word{font-weight:600;color:#d4d8e8;font-size:.88rem;min-width:120px}
.vocab-meaning{font-size:.85rem;color:#6b7280;flex:1}
.exam-chip{font-size:.58rem;padding:1px 6px;border-radius:100px;
  background:rgba(201,168,76,.12);color:#c9a84c;white-space:nowrap}
.quiz-card{background:#0d1220;border:1px solid #1e2840;border-radius:12px;
  padding:20px;margin-bottom:16px}
.quiz-card:hover{border-color:#2d3a5a}
.q-header{display:flex;align-items:center;gap:10px;margin-bottom:12px}
.q-num{font-family:monospace;font-size:.72rem;color:#4b5563;
  background:#111827;border:1px solid #1e2840;border-radius:100px;padding:2px 9px}
.q-text{font-size:1rem;color:#e2e8f0;font-weight:500;line-height:1.5;margin-bottom:14px}
.q-options{display:flex;flex-direction:column;gap:6px;margin-bottom:14px}
.opt{font-size:.85rem;color:#94a3b8;padding:8px 12px;
  background:rgba(255,255,255,.02);border-radius:8px;border:1px solid #1e2840}
details.q-reveal summary{display:inline-flex;align-items:center;gap:6px;
  font-size:.78rem;color:#4b5563;cursor:pointer;padding:6px 12px;
  border-radius:8px;border:1px solid #1e2840;background:rgba(255,255,255,.02);
  list-style:none;transition:all .15s;user-select:none}
details.q-reveal summary:hover{border-color:#c9a84c;color:#c9a84c}
details.q-reveal summary::after{content:'↓';font-size:.7rem}
details.q-reveal[open] summary::after{content:'↑'}
details.q-reveal[open] summary{border-color:#3ecf8e;color:#3ecf8e}
.q-answer{margin-top:12px;padding:12px 14px;border-radius:8px;
  background:rgba(62,207,142,.06);border:1px solid rgba(62,207,142,.2)}
.answer-correct{font-size:.88rem;font-weight:600;color:#3ecf8e;
  display:block;margin-bottom:4px}
.answer-source{font-size:.72rem;color:#4b5563;font-family:monospace}
.app-cta{background:linear-gradient(135deg,#111827,#0d1525);
  border:1px solid #1e2840;border-radius:14px;padding:22px 20px;
  margin:28px 0;text-align:center}
.app-cta p{font-size:.85rem;color:#6b7280;margin-bottom:12px}
.app-cta-btn{display:inline-block;background:#c9a84c;color:#0a0f1e;
  font-weight:700;font-size:.82rem;padding:10px 22px;border-radius:8px}
.app-cta-btn:hover{background:#d4b96a;text-decoration:none}
.day-nav{display:flex;justify-content:space-between;align-items:center;
  margin:32px 0;padding:14px 18px;background:#0d1220;
  border:1px solid #1e2840;border-radius:10px;font-size:.82rem}
.day-nav a{color:#6b7280}.day-nav a:hover{color:#c9a84c;text-decoration:none}
.day-nav .center-link{color:#4b5563;font-size:.75rem}
.cross-link{text-align:center;margin:16px 0;font-size:.82rem;color:#4b5563}
.cross-link a{color:#94a3b8}.cross-link a:hover{color:#c9a84c}
.archive-grid{display:flex;flex-direction:column;gap:10px;margin-top:16px}
.archive-item{display:flex;align-items:baseline;gap:10px;padding:12px 16px;
  background:#111827;border:1px solid #1e2840;border-radius:10px;
  transition:border-color .15s;text-decoration:none;color:inherit}
.archive-item:hover{border-color:#c9a84c;text-decoration:none}
.archive-date{font-size:.68rem;color:#4b5563;min-width:76px;font-family:monospace}
.archive-word{font-weight:600;color:#d4d8e8}
.archive-meaning{font-size:.8rem;color:#6b7280;flex:1}
.archive-badge{font-size:.6rem;padding:1px 7px;border-radius:100px;
  background:rgba(201,168,76,.12);color:#c9a84c;flex-shrink:0}
.redirect-buttons{display:flex;gap:16px;justify-content:center;
  flex-wrap:wrap;margin-top:32px}
.redirect-btn{padding:12px 28px;border-radius:10px;font-weight:600;
  font-size:.9rem;border:1px solid #1e2840;background:#111827;
  color:#d4d8e8;transition:all .15s;text-decoration:none}
.redirect-btn:hover{border-color:#c9a84c;color:#c9a84c;text-decoration:none}
.redirect-btn.primary{background:#c9a84c;color:#0a0f1e;border-color:#c9a84c}
.redirect-btn.primary:hover{background:#d4b96a;color:#0a0f1e}
.site-footer{border-top:1px solid #1e2840;padding:24px 20px;
  text-align:center;font-size:.75rem;color:#374151;margin-top:48px}
.site-footer a{color:#4b5563}
@media(max-width:600px){
  .nav-links{gap:10px}
  .day-nav{flex-direction:column;gap:10px;text-align:center}
  .vocab-word{min-width:90px}
  .archive-meaning{display:none}
  .redirect-buttons{flex-direction:column;align-items:center}
}
"""

# ── HTML helpers ──────────────────────────────────────────────────────────────
def _e(s) -> str:
    return html.escape(str(s)) if s is not None else ""

def _footer() -> str:
    yr = datetime.now().year
    return f"""
<footer class="site-footer">
  <p>
    <a href="{BASE_URL}/">Home</a> ·
    <a href="{DOCS_URL}/words/">All Words</a> ·
    <a href="{DOCS_URL}/bcs-vocabulary/">BCS</a> ·
    <a href="{DOCS_URL}/upsc-vocabulary/">UPSC</a> ·
    <a href="{APP_URL}" target="_blank" rel="noopener">App</a>
  </p>
  <p style="margin-top:6px">© {yr} Editorial Vocabulary · Mahadi Hasan · Tangail, Bangladesh</p>
</footer>"""

def _nav(lang: str, active: str = "") -> str:
    """
    Lang-aware nav — India users see UPSC Vocabulary, BD users see BCS Vocabulary.
    active: "words" | "bcs" | "upsc" | "quiz" | ""
    """
    if lang == "bn":
        archive_href  = f"{DOCS_URL}/bcs-vocabulary/"
        archive_label = "BCS Vocabulary"
    elif lang == "hn":
        archive_href  = f"{DOCS_URL}/upsc-vocabulary/"
        archive_label = "UPSC Vocabulary"
    else:
        archive_href  = f"{DOCS_URL}/words/"
        archive_label = "Word Archive"

    def _a(href: str, label: str, key: str) -> str:
        cls = ' class="nav-active"' if active == key else ""
        return f'<a href="{href}"{cls}>{label}</a>'

    return f"""
<nav class="top-nav">
  <a class="nav-logo" href="{BASE_URL}/">{SITE_NAME} <span>| Editorial</span></a>
  <div class="nav-links">
    <a href="{BASE_URL}/">Home</a>
    {_a(archive_href, archive_label, "archive")}
    {_a(f"{DOCS_URL}/words/", "All Words", "words")}
    <a href="{APP_URL}" target="_blank" rel="noopener">App ↗</a>
  </div>
</nav>"""

# ── Date helpers ──────────────────────────────────────────────────────────────
def _dt(s: str) -> datetime:
    return datetime.strptime(s, "%d-%m-%Y")

def _disp(s: str) -> str:
    return _dt(s).strftime("%d %B %Y")

def _adj(s: str) -> tuple[str, str]:
    d = _dt(s)
    f = "%d-%m-%Y"
    return (d - timedelta(days=1)).strftime(f), (d + timedelta(days=1)).strftime(f)

def _wurl(date: str, lang: str) -> str:
    return f"{DOCS_URL}/words/{date}/{lang}/"

def _qurl(date: str, lang: str) -> str:
    return f"{DOCS_URL}/quiz/{date}/{lang}/"

# ── Meaning resolution (BUG FIX #1) ─────────────────────────────────────────
def _meaning(entry: dict, lang: str) -> str:
    keys = (
        ["bangla_meaning", "bengali_meaning", "bn_meaning", "meaning"]
        if lang == "bn"
        else ["hindi_meaning", "hn_meaning", "hi_meaning", "meaning"]
    )
    for k in keys:
        v = entry.get(k)
        if v and str(v).strip():
            return str(v).strip()
    return ""

def _badge(source: str) -> tuple[str, str]:
    if not source or source == "editorial":
        return "Editorial", "badge-edit"
    if source.startswith("editorial+"):
        return source.replace("editorial+", "Also in "), "badge-pyq"
    return f"PYQ · {source}", "badge-pyq"

# ═══════════════════════════════════════════════════════════════════════════════
# 1. WOTD PAGE
# ═══════════════════════════════════════════════════════════════════════════════
def generate_wotd_page(
    lang: str,
    wotd_entry: dict,
    vocab_list: List[str],
    current_date: str,
) -> Optional[Path]:
    """Generate docs/words/DD-MM-YYYY/{lang}/index.html"""
    word = wotd_entry.get("word", "")
    if not word:
        log.warning("⚠️  No 'word' in WOTD entry for %s/%s", current_date, lang)
        return None

    lang_lbl  = "Bengali" if lang == "bn" else "Hindi"
    exam_lbl  = "BCS PSC Bangladesh" if lang == "bn" else "UPSC SSC India"
    src       = wotd_entry.get("source", "editorial")
    bt, bc    = _badge(src)
    m         = _meaning(wotd_entry, lang)
    defn      = wotd_entry.get("definition", "")
    phon      = wotd_entry.get("phonetic", "") or wotd_entry.get("ipa", "")
    pos       = wotd_entry.get("part_of_speech", "") or wotd_entry.get("pos", "")
    ex        = wotd_entry.get("example", "") or wotd_entry.get("example_sentence", "")
    syns      = wotd_entry.get("synonyms") or []
    ants      = wotd_entry.get("antonyms") or []
    prev_d, next_d = _adj(current_date)
    page_url  = _wurl(current_date, lang)
    arch_url  = f"{DOCS_URL}/{'bcs' if lang=='bn' else 'upsc'}-vocabulary/"
    arch_lbl  = "BCS Vocabulary" if lang == "bn" else "UPSC Vocabulary"

    schema = {
        "@context": "https://schema.org", "@type": "DefinedTerm",
        "name": word, "description": defn,
        "inDefinedTermSet": {
            "@type": "DefinedTermSet",
            "name": f"Editorial Vocabulary — {lang_lbl} Word of the Day",
            "url": f"{DOCS_URL}/words/"
        },
        "url": page_url, "termCode": current_date,
    }

    vocab_rows = ""
    for i, ent in enumerate(vocab_list, 1):
        parts = ent.split(" : ", 1)
        w = parts[0].strip(); mv = parts[1].strip() if len(parts) > 1 else ""
        tag = '<span class="exam-chip">Exam</span>' if i == 1 else ""
        vocab_rows += (
            f'<div class="vocab-row">'
            f'<span class="vocab-num">{i:02d}</span>'
            f'<span class="vocab-word">{_e(w)}</span>'
            f'<span class="vocab-meaning">{_e(mv)}</span>{tag}</div>'
        )

    syn_h = "".join(f'<span class="chip">{_e(s)}</span>' for s in syns[:7])
    ant_h = "".join(f'<span class="chip">{_e(a)}</span>' for a in ants[:7])
    meta_d = f"{_e(word)}: {_e(defn[:110])}. Word of the Day {_disp(current_date)} — {lang_lbl} meaning for {exam_lbl}."

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{_e(word)} meaning in {lang_lbl} — {_disp(current_date)} | {SITE_NAME}</title>
<meta name="description" content="{meta_d}">
<meta name="keywords" content="{_e(word)}, {_e(word)} meaning in {lang_lbl}, {exam_lbl} vocabulary, editorial word of the day">
<link rel="canonical" href="{page_url}">
<meta property="og:title" content="{_e(word)} — {lang_lbl} Word of the Day">
<meta property="og:description" content="{_e(defn[:160])}">
<meta property="og:url" content="{page_url}">
<meta property="og:type" content="article">
<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>
<style>{_CSS}</style>
</head>
<body>
{_nav(lang, "archive")}
<div class="container">
  <div class="breadcrumb">
    <a href="{BASE_URL}/">Home</a><span>›</span>
    <a href="{arch_url}">{arch_lbl}</a><span>›</span>
    {_e(_disp(current_date))} · {lang_lbl}
  </div>
  <div style="margin-bottom:16px"><span class="source-badge {bc}">{_e(bt)}</span></div>
  <h1 class="word-title">{_e(word)}</h1>
  {f'<div class="word-phonetic">{_e(phon)}</div>' if phon else ""}
  {f'<div class="word-pos">{_e(pos)}</div>' if pos else ""}
  <div class="word-divider"></div>
  <div class="section">
    <div class="section-label">{lang_lbl} Meaning</div>
    {f'<div class="native-meaning">{_e(m)}</div>' if m else ""}
    {f'<p class="definition">{_e(defn)}</p>' if defn else ""}
  </div>
  {f'<div class="section"><div class="section-label">Example</div><div class="example">&ldquo;{_e(ex)}&rdquo;</div></div>' if ex else ""}
  {f'<div class="section"><div class="section-label">Synonyms</div><div class="chip-row">{syn_h}</div></div>' if syn_h else ""}
  {f'<div class="section"><div class="section-label">Antonyms</div><div class="chip-row">{ant_h}</div></div>' if ant_h else ""}
  <div class="word-divider"></div>
  {f'<div class="vocab-section"><h2>📚 All 10 Words — {_disp(current_date)}</h2>{vocab_rows}</div>' if vocab_rows else ""}
  <div class="cross-link">📝 <a href="{_qurl(current_date, lang)}">Take today&rsquo;s quiz →</a></div>
  <div class="app-cta">
    <p>Streaks · XP · Spaced Repetition · Leaderboard</p>
    <a class="app-cta-btn" href="{APP_URL}" target="_blank" rel="noopener">📱 Free on Google Play</a>
  </div>
  <nav class="day-nav">
    <a href="{_wurl(prev_d, lang)}">← {_disp(prev_d)}</a>
    <a class="center-link" href="{DOCS_URL}/words/">All Words</a>
    <a href="{_wurl(next_d, lang)}">{_disp(next_d)} →</a>
  </nav>
</div>
{_footer()}
</body></html>"""

    out = DOCS_ROOT / "words" / current_date / lang / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")
    log.info("🌐  WOTD page → %s", out)
    return out

# ═══════════════════════════════════════════════════════════════════════════════
# 2. QUIZ PAGE
# ═══════════════════════════════════════════════════════════════════════════════
def generate_quiz_page(
    lang: str,
    quiz_data: dict,
    current_date: str,
) -> Optional[Path]:
    """Generate docs/quiz/DD-MM-YYYY/{lang}/index.html"""
    questions = quiz_data.get("questions", [])
    if not questions:
        log.warning("⚠️  No questions in quiz_data for %s/%s", current_date, lang)
        return None

    lang_lbl = "Bengali" if lang == "bn" else "Hindi"
    exam_lbl = "BCS PSC" if lang == "bn" else "UPSC SSC"
    page_url = _qurl(current_date, lang)
    arch_url = f"{DOCS_URL}/{'bcs' if lang=='bn' else 'upsc'}-vocabulary/"
    arch_lbl = "BCS Vocabulary" if lang == "bn" else "UPSC Vocabulary"
    prev_d, next_d = _adj(current_date)

    # schema.org Quiz
    schema_qs = []
    for i, q in enumerate(questions, 1):
        opts = q.get("options", [])
        ans  = q.get("answer", "")
        ltr  = next((chr(65 + j) + ") " for j, o in enumerate(opts) if o == ans), "")
        schema_qs.append({
            "@type": "Question", "position": i,
            "text": q.get("question", ""),
            "acceptedAnswer": {"@type": "Answer", "text": f"{ltr}{ans}"}
        })
    schema = {
        "@context": "https://schema.org", "@type": "Quiz",
        "name": f"{exam_lbl} Vocabulary Quiz — {_disp(current_date)}",
        "url": page_url,
        "datePublished": _dt(current_date).strftime("%Y-%m-%d"),
        "hasPart": schema_qs,
    }

    cards = ""
    for i, q in enumerate(questions, 1):
        q_txt = q.get("question", "")
        opts  = q.get("options", [])
        ans   = q.get("answer", "")
        src   = q.get("source", "editorial")
        bt, bc = _badge(src)
        is_pyq = src != "editorial"

        opts_h = "".join(
            f'<div class="opt">{chr(65+j)}) {_e(o)}</div>'
            for j, o in enumerate(opts)
        )
        ltr = next((chr(65 + j) + ") " for j, o in enumerate(opts) if o == ans), "")
        src_note = f'<span class="answer-source">{_e(bt)}</span>' if is_pyq else ""

        cards += f"""
  <div class="quiz-card">
    <div class="q-header">
      <span class="q-num">Q{i} / {len(questions)}</span>
      {'<span class="source-badge ' + bc + '">' + _e(bt) + '</span>' if is_pyq else ""}
    </div>
    <p class="q-text">{_e(q_txt)}</p>
    <div class="q-options">{opts_h}</div>
    <details class="q-reveal">
      <summary>Show Answer</summary>
      <div class="q-answer">
        <span class="answer-correct">✅ {_e(ltr)}{_e(ans)}</span>
        {src_note}
      </div>
    </details>
  </div>"""

    meta_d = (
        f"{exam_lbl} vocabulary quiz for {_disp(current_date)}. "
        f"10 MCQ questions — Q1 is a real Previous Year Question. "
        f"Click Show Answer to reveal. Free, no signup."
    )

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{exam_lbl} Quiz — {_disp(current_date)} | 10 MCQ | {SITE_NAME}</title>
<meta name="description" content="{meta_d}">
<meta name="keywords" content="{exam_lbl} vocabulary quiz, editorial MCQ, {_disp(current_date)} quiz, {lang_lbl} competitive exam English">
<link rel="canonical" href="{page_url}">
<meta property="og:title" content="{exam_lbl} Quiz — {_disp(current_date)} | 10 MCQ">
<meta property="og:description" content="{meta_d}">
<meta property="og:url" content="{page_url}">
<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>
<style>{_CSS}</style>
</head>
<body>
{_nav(lang, "archive")}
<div class="container">
  <div class="breadcrumb">
    <a href="{BASE_URL}/">Home</a><span>›</span>
    <a href="{arch_url}">{arch_lbl}</a><span>›</span>
    Quiz · {_disp(current_date)}
  </div>
  <h1 class="page-title">{exam_lbl} Quiz</h1>
  <p class="page-sub">
    {_disp(current_date)} · {len(questions)} questions ·
    Q1 is a real PYQ · click "Show Answer" to reveal
  </p>
  {cards}
  <div class="cross-link" style="margin-top:24px">
    📖 <a href="{_wurl(current_date, lang)}">See today&rsquo;s full vocabulary →</a>
  </div>
  <div class="app-cta">
    <p>Get XP, streaks and full explanations in the app</p>
    <a class="app-cta-btn" href="{APP_URL}" target="_blank" rel="noopener">📱 Free on Google Play</a>
  </div>
  <nav class="day-nav">
    <a href="{_qurl(prev_d, lang)}">← {_disp(prev_d)}</a>
    <a class="center-link" href="{DOCS_URL}/words/">All Words</a>
    <a href="{_qurl(next_d, lang)}">{_disp(next_d)} →</a>
  </nav>
</div>
{_footer()}
</body></html>"""

    out = DOCS_ROOT / "quiz" / current_date / lang / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")
    log.info("🌐  Quiz page → %s", out)
    return out

# ═══════════════════════════════════════════════════════════════════════════════
# 3. .nojekyll
# ═══════════════════════════════════════════════════════════════════════════════
def ensure_nojekyll() -> None:
    f = DOCS_ROOT / ".nojekyll"
    f.parent.mkdir(parents=True, exist_ok=True)
    if not f.exists():
        f.write_text("", encoding="utf-8")
        log.info("🌐  Created .nojekyll")

# ═══════════════════════════════════════════════════════════════════════════════
# 4. WORDS INDEX (JS redirect + noscript fallback)
# ═══════════════════════════════════════════════════════════════════════════════
def generate_words_index() -> None:
    """
    docs/words/index.html — reads localStorage 'editorial_region' (saved by
    app.js setRegion()) and redirects:
      BD → /docs/bcs-vocabulary/
      IN → /docs/upsc-vocabulary/
    """
    words_dir = DOCS_ROOT / "words"
    words_dir.mkdir(parents=True, exist_ok=True)

    entries: list[tuple[str, list[str]]] = []
    for d in sorted(words_dir.iterdir(), reverse=True):
        if not d.is_dir():
            continue
        langs = sorted(l.name for l in d.iterdir() if l.is_dir() and l.name in ("bn", "hn"))
        if langs:
            entries.append((d.name, langs))

    rows = ""
    for date_str, langs in entries[:30]:
        try: disp = _disp(date_str)
        except Exception: disp = date_str
        lnks = " · ".join(
            f'<a href="{_wurl(date_str, lg)}">{"Bengali" if lg=="bn" else "Hindi"}</a>'
            for lg in langs
        )
        rows += (
            f'<div class="archive-item">'
            f'<span class="archive-date">{_e(date_str)}</span>'
            f'<span class="archive-word">{_e(disp)}</span>'
            f'<span class="archive-meaning">{lnks}</span></div>'
        )

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Word Archive — {SITE_NAME}</title>
<meta name="description" content="Daily editorial vocabulary archive for UPSC SSC (India) and BCS PSC (Bangladesh).">
<link rel="canonical" href="{DOCS_URL}/words/">
<script>
(function(){{
  try{{
    var r=localStorage.getItem('editorial_region');
    window.location.replace(r==='BD'?'{DOCS_URL}/bcs-vocabulary/':'{DOCS_URL}/upsc-vocabulary/');
  }}catch(e){{}}
}})();
</script>
<style>{_CSS}
.redir{{text-align:center;padding:60px 20px;color:#6b7280;font-size:.9rem}}
</style>
</head>
<body>
{_nav("", "words")}
<div class="container">
  <div class="redir"><p>Redirecting to your vocabulary archive…</p></div>
  <noscript>
    <h1 class="page-title" style="margin-top:32px">Choose Your Exam</h1>
    <div class="redirect-buttons">
      <a class="redirect-btn primary" href="{DOCS_URL}/bcs-vocabulary/">🇧🇩 BCS &amp; PSC</a>
      <a class="redirect-btn"         href="{DOCS_URL}/upsc-vocabulary/">🇮🇳 UPSC &amp; SSC</a>
    </div>
  </noscript>
  <div style="margin-top:48px">
    <h2 class="page-title" style="font-size:1.4rem;margin-bottom:6px">Recent Daily Words</h2>
    <p class="page-sub">{len(entries)} days archived</p>
    <div class="archive-grid">{rows}</div>
  </div>
</div>
{_footer()}
</body></html>"""

    out = words_dir / "index.html"
    out.write_text(page, encoding="utf-8")
    log.info("🌐  Words index → %d entries", len(entries))

# ═══════════════════════════════════════════════════════════════════════════════
# 5. EXAM ARCHIVE
# ═══════════════════════════════════════════════════════════════════════════════
def append_to_exam_archive(lang: str, wotd_entry: dict, current_date: str) -> None:
    src  = wotd_entry.get("source", "") or ""
    word = wotd_entry.get("word", "")
    if not word or not src or src == "editorial":
        return
    tags = []
    if lang == "bn" and any(t in src for t in ("BCS", "PSC")):
        tags.append("bcs")
    if lang == "hn" and any(t in src for t in ("UPSC", "SSC", "IAS")):
        tags.append("upsc")
    if not tags:
        return

    m = _meaning(wotd_entry, lang)
    d = wotd_entry.get("definition", "")
    for tag in tags:
        lp = _EXAM_LOG[tag]
        lp.parent.mkdir(parents=True, exist_ok=True)
        entries = []
        if lp.exists():
            try: entries = json.loads(lp.read_text(encoding="utf-8"))
            except Exception: entries = []
        if word.lower() not in {e["word"].lower() for e in entries}:
            entries.append({"word": word, "meaning": m, "definition": d,
                            "source": src, "date": current_date, "lang": lang})
            lp.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")
            log.info("📋  %s → %s archive (%d)", word, tag.upper(), len(entries))
        _build_exam_html(tag, entries)

def _available_months(lang: str) -> list:
    """
    Scan docs/words/ for MM-YYYY/{lang}/index.html directories — i.e.
    monthly index pages already generated by generate_monthly_index() —
    and return them newest-first as (mm_yyyy, month_num, year) tuples.

    Used to build a "Browse by Month" strip on the BCS/UPSC archive
    pages, since otherwise those monthly pages have no inbound link
    from anywhere on the site at all.
    """
    words_dir = DOCS_ROOT / "words"
    if not words_dir.exists():
        return []
    out = []
    for d in words_dir.iterdir():
        if not d.is_dir():
            continue
        m = re.match(r"^(\d{2})-(\d{4})$", d.name)
        if not m:
            continue
        if not (d / lang / "index.html").exists():
            continue
        out.append((d.name, int(m.group(1)), int(m.group(2))))
    out.sort(key=lambda t: (t[2], t[1]), reverse=True)
    return out


def _build_exam_html(tag: str, entries: list) -> None:
    meta = {
        "bcs":  ("BCS & PSC Vocabulary", "Bangladesh Civil Service · PSC", "🇧🇩", "Daily Star", "bn"),
        "upsc": ("UPSC & SSC Vocabulary", "Union Public Service Commission · SSC", "🇮🇳", "The Hindu", "hn"),
    }
    title, sub, flag, paper, lang = meta[tag]
    slug = f"{tag}-vocabulary"

    months = _available_months(lang)
    monthly_nav = ""
    if months:
        pills = "".join(
            f'<a href="{DOCS_URL}/words/{mm_yyyy}/{lang}/" '
            f'style="display:inline-block;font-size:0.78rem;color:#c9a84c;'
            f'border:1px solid rgba(201,168,76,0.35);border-radius:16px;'
            f'padding:5px 14px;margin:3px 4px 3px 0;text-decoration:none;white-space:nowrap;">'
            f'{_MONTH_NAMES[mm]} {yyyy}</a>'
            for mm_yyyy, mm, yyyy in months[:12]
        )
        monthly_nav = f"""
  <div style="margin:18px 0 26px">
    <div style="font-size:0.75rem;color:#8892a6;margin-bottom:8px">📅 Browse by Month</div>
    {pills}
  </div>"""

    rows = "".join(
        f'<a class="archive-item" href="{_wurl(e["date"], e["lang"])}" style="text-decoration:none">'
        f'<span class="archive-date">{_e(e["date"])}</span>'
        f'<span class="archive-word">{_e(e["word"])}</span>'
        f'<span class="archive-meaning">{_e(e["meaning"])}</span>'
        f'<span class="archive-badge {_badge(e.get("source",""))[1]}">{_e(_badge(e.get("source",""))[0])}</span>'
        f'</a>'
        for e in reversed(entries)
    ) or '<p style="color:#6b7280">No entries yet — check back tomorrow.</p>'

    schema = json.dumps({
        "@context": "https://schema.org", "@type": "ItemList",
        "name": f"{title} — Previous Year Questions",
        "url": f"{DOCS_URL}/{slug}/",
        "numberOfItems": len(entries),
    }, ensure_ascii=False)

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{flag} {title} — PYQ | {SITE_NAME}</title>
<meta name="description" content="{len(entries)} vocabulary words from {sub}. Real PYQs from {paper}. Updated daily.">
<link rel="canonical" href="{DOCS_URL}/{slug}/">
<script type="application/ld+json">{schema}</script>
<style>{_CSS}</style>
</head>
<body>
{_nav(lang, "archive")}
<div class="container">
  <div class="breadcrumb"><a href="{BASE_URL}/">Home</a><span>›</span>{title}</div>
  <h1 class="page-title">{flag} {title}</h1>
  <p class="page-sub">{sub} · {len(entries)} words · Updated daily from {paper}</p>
  {monthly_nav}
  <div class="archive-grid">{rows}</div>
  <div class="app-cta" style="margin-top:32px">
    <p>Practice with spaced repetition and real exam quizzes</p>
    <a class="app-cta-btn" href="{APP_URL}" target="_blank" rel="noopener">📱 Free on Google Play</a>
  </div>
</div>
{_footer()}
</body></html>"""

    out = DOCS_ROOT / slug / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")
    log.info("🌐  %s archive → %d words", tag.upper(), len(entries))

# ═══════════════════════════════════════════════════════════════════════════════
# 6. MONTHLY INDEX (SEO — "<Month> <Year> <Exam> vocabulary words")
# ═══════════════════════════════════════════════════════════════════════════════
_MONTH_NAMES = ["", "January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"]

def _month_entries(year: int, month: int, lang: str) -> list[tuple[str, str, str]]:
    """
    Walk docs/words/ and collect (date, word, meaning) for every day in the
    given year/month that has a generated page for `lang`.

    Reads the already-generated daily HTML rather than _EXAM_LOG, because
    _EXAM_LOG only records PYQ-sourced words (see append_to_exam_archive) —
    it's a subset, not the full month. The daily HTML is the one source
    guaranteed to match what's actually live on each page.
    """
    words_dir = DOCS_ROOT / "words"
    if not words_dir.exists():
        return []

    out: list[tuple[str, str, str]] = []
    for d in sorted(words_dir.iterdir()):
        if not d.is_dir():
            continue
        try:
            dt = _dt(d.name)  # only matches DD-MM-YYYY dirs; MM-YYYY dirs raise and are skipped
        except ValueError:
            continue
        if dt.year != year or dt.month != month:
            continue

        page = d / lang / "index.html"
        if not page.exists():
            continue

        text = page.read_text(encoding="utf-8")
        wm = re.search(r'<h1 class="word-title">(.*?)</h1>', text, re.S)
        mm = re.search(r'<div class="native-meaning">(.*?)</div>', text, re.S)
        word    = html.unescape(wm.group(1).strip()) if wm else d.name
        meaning = html.unescape(mm.group(1).strip()) if mm else ""
        out.append((d.name, word, meaning))

    out.sort(key=lambda e: _dt(e[0]))
    return out

def generate_monthly_index(year: int, month: int) -> None:
    """
    docs/words/MM-YYYY/{lang}/index.html — one SEO landing page per language
    listing every Word of the Day published that month, each linking to its
    daily page. Targets high-volume pre-exam searches like
    "June 2026 BCS vocabulary words" / "June 2026 UPSC vocabulary words".

    Safe to call multiple times (idempotent overwrite). Call near the end of
    the month (day 28+) once most/all daily pages already exist — see
    main.py's end-of-month hook. Re-running early next month as a backfill
    catches any words published on the last 1-3 days after the last run.
    """
    month_name = _MONTH_NAMES[month]
    mm_yyyy    = f"{month:02d}-{year}"

    for lang in ("bn", "hn"):
        entries = _month_entries(year, month, lang)
        if not entries:
            log.warning("⚠️  No %s entries for %s %d — skipping monthly index", lang, month_name, year)
            continue

        exam_lbl   = "BCS & PSC" if lang == "bn" else "UPSC & SSC"
        exam_short = "BCS" if lang == "bn" else "UPSC"
        flag       = "🇧🇩" if lang == "bn" else "🇮🇳"
        arch_url   = f"{DOCS_URL}/{'bcs' if lang == 'bn' else 'upsc'}-vocabulary/"
        arch_lbl   = "BCS Vocabulary" if lang == "bn" else "UPSC Vocabulary"
        page_url   = f"{DOCS_URL}/words/{mm_yyyy}/{lang}/"

        rows = "".join(
            f'<a class="archive-item" href="{_wurl(date, lang)}" style="text-decoration:none">'
            f'<span class="archive-date">{_e(date)}</span>'
            f'<span class="archive-word">{_e(word)}</span>'
            f'<span class="archive-meaning">{_e(meaning)}</span></a>'
            for date, word, meaning in entries
        )

        schema = json.dumps({
            "@context": "https://schema.org", "@type": "ItemList",
            "name": f"{month_name} {year} {exam_short} Vocabulary Words",
            "url": page_url,
            "numberOfItems": len(entries),
            "itemListElement": [
                {"@type": "ListItem", "position": i, "name": w, "url": _wurl(d, lang)}
                for i, (d, w, m) in enumerate(entries, 1)
            ],
        }, ensure_ascii=False)

        meta_d = (
            f"{len(entries)} {exam_lbl} vocabulary words from {month_name} {year} editorials. "
            f"Free daily Word of the Day archive for {exam_lbl} exam prep."
        )

        page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{month_name} {year} {exam_short} Vocabulary Words — {len(entries)} Words | {SITE_NAME}</title>
<meta name="description" content="{meta_d}">
<meta name="keywords" content="{month_name} {year} {exam_short} vocabulary, {exam_lbl} vocabulary words, editorial vocabulary {month_name} {year}">
<link rel="canonical" href="{page_url}">
<meta property="og:title" content="{month_name} {year} {exam_short} Vocabulary Words">
<meta property="og:description" content="{meta_d}">
<meta property="og:url" content="{page_url}">
<script type="application/ld+json">{schema}</script>
<style>{_CSS}</style>
</head>
<body>
{_nav(lang, "archive")}
<div class="container">
  <div class="breadcrumb">
    <a href="{BASE_URL}/">Home</a><span>›</span>
    <a href="{arch_url}">{arch_lbl}</a><span>›</span>
    {month_name} {year}
  </div>
  <h1 class="page-title">{flag} {month_name} {year} {exam_short} Vocabulary Words</h1>
  <p class="page-sub">{len(entries)} words · every daily Word of the Day published in {month_name} {year} · {exam_lbl}</p>
  <div class="archive-grid">{rows}</div>
  <div class="app-cta" style="margin-top:32px">
    <p>Practice all {len(entries)} words with spaced repetition and quizzes in the app</p>
    <a class="app-cta-btn" href="{APP_URL}" target="_blank" rel="noopener">📱 Free on Google Play</a>
  </div>
  <div class="app-cta" style="margin-top:14px">
    <p>Prefer a printable PDF? Get {month_name} {year}'s complete word list as an eBook</p>
    <a class="app-cta-btn" style="background:#25D366;color:#062b13"
       href="{BASE_URL}/ebooks/?lang={lang}&amp;month={mm_yyyy}">📖 Get {month_name} {year} eBook</a>
  </div>
  <div class="cross-link" style="margin-top:16px">📚 <a href="{arch_url}">See the full {arch_lbl} archive →</a></div>
</div>
{_footer()}
</body></html>"""

        out = DOCS_ROOT / "words" / mm_yyyy / lang / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page, encoding="utf-8")
        log.info("🌐  Monthly index → %s (%d words)", out, len(entries))

# ═══════════════════════════════════════════════════════════════════════════════
# 7. SITEMAP
# ═══════════════════════════════════════════════════════════════════════════════
def update_sitemap() -> None:
    today = datetime.now().strftime("%Y-%m-%d")
    urls  = [(f"{BASE_URL}/", today, "daily", "1.0")]

    for sub in ("words", "quiz"):
        d = DOCS_ROOT / sub
        if not d.exists():
            continue
        for idx in sorted(d.rglob("index.html")):
            rel  = idx.parent.relative_to(DOCS_ROOT)
            # BUG FIX: a path component can carry a stray \r (carriage return)
            # artifact from CRLF-related path handling on the Windows runner.
            # That \r can land in the MIDDLE of the joined path (e.g. between
            # a folder name and the trailing slash), so a single .strip() on
            # the final string is not enough — it only trims the two ends.
            # Stripping each part individually before joining removes any
            # such stray whitespace wherever it occurs. This was the exact
            # cause of "Sitemap could not be read" / 0 discovered pages in
            # Google Search Console, even though the XML was technically
            # well-formed overall.
            clean_parts = [part.strip() for part in rel.parts]
            url  = f"{DOCS_URL}/{'/'.join(clean_parts)}/"
            lm   = today
            for p in rel.parts:
                try: lm = _dt(p).strftime("%Y-%m-%d"); break
                except ValueError: pass
            pri = "0.9" if sub == "words" else "0.85"
            urls.append((url, lm, "monthly", pri))

    for slug in ("bcs-vocabulary", "upsc-vocabulary"):
        if (DOCS_ROOT / slug / "index.html").exists():
            urls.append((f"{DOCS_URL}/{slug}/", today, "daily", "0.9"))
    if (DOCS_ROOT / "words" / "index.html").exists():
        urls.append((f"{DOCS_URL}/words/", today, "daily", "0.8"))

    body = "".join(
        f"\n  <url><loc>{u.strip()}</loc><lastmod>{lm}</lastmod>"
        f"<changefreq>{cf}</changefreq><priority>{p}</priority></url>"
        for u, lm, cf, p in urls
    )
    out = DOCS_ROOT / "sitemap.xml"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{body}\n</urlset>',
        encoding="utf-8"
    )
    log.info("🗺️   Sitemap → %d URLs", len(urls))
# ═══════════════════════════════════════════════════════════════════════════════
# 8. FORCE-REGENERATE ALL STATIC PAGES
# ═══════════════════════════════════════════════════════════════════════════════
def regenerate_static_pages() -> None:
    """Re-generate every shared static page from existing _entries.json data.

    Call this from main.py on every pipeline run (after WOTD generation) to
    ensure the words index, both archive pages, sitemap, and .nojekyll are
    always up-to-date — not stale from a previous web_generator version.

    Safe to call multiple times: all outputs are idempotent writes.
    """
    ensure_nojekyll()

    # Re-build BCS archive if data exists
    bcs_log = _EXAM_LOG["bcs"]
    if bcs_log.exists():
        try:
            entries = json.loads(bcs_log.read_text(encoding="utf-8"))
            _build_exam_html("bcs", entries)
            log.info("🔄  Regenerated BCS archive (%d entries)", len(entries))
        except Exception as exc:
            log.warning("⚠️  BCS archive regeneration failed: %s", exc)

    # Re-build UPSC archive if data exists
    upsc_log = _EXAM_LOG["upsc"]
    if upsc_log.exists():
        try:
            entries = json.loads(upsc_log.read_text(encoding="utf-8"))
            _build_exam_html("upsc", entries)
            log.info("🔄  Regenerated UPSC archive (%d entries)", len(entries))
        except Exception as exc:
            log.warning("⚠️  UPSC archive regeneration failed: %s", exc)

    # Re-build words index
    generate_words_index()

    # Re-build sitemap last (needs all pages to exist)
    update_sitemap()