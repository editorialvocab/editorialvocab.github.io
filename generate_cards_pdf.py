import argparse
import json
import sys
import unicodedata
import urllib.error
import urllib.request
import urllib.parse
import calendar
import random
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

# Force UTF-8 encoding for console output to prevent crashes on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# ─── Argument Parsing ─────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Generate Monthly Vocabulary eBook PDF")
parser.add_argument("-t", "--type", choices=["EnToBn", "EnToHn"], required=True,
                    help="Vocabulary type (EnToBn or EnToHn)")
parser.add_argument("date", help="Month in MM-YYYY format")
parser.add_argument("--no-cover",    action="store_true", help="Skip cover page")
parser.add_argument("--no-index",    action="store_true", help="Skip index page")
parser.add_argument("--no-revision", action="store_true", help="Skip weekly revision pages")
parser.add_argument("--no-mcq",      action="store_true", help="Skip MCQ test page")
parser.add_argument(
    "--repo-root",
    default=None,
    help=(
        "Absolute path to your local rtejhs repo root (e.g. E:\\EditorialGitlabServer\\rtejhs). "
        "Used as local fallback when GitLab is unreachable. "
        "If not set, the script auto-detects common locations."
    ),
)
args = parser.parse_args()

month, year = args.date.split("-")
month_name  = calendar.month_name[int(month)]
month_abbr  = month_name[:3]

# ─── Config ───────────────────────────────────────────────────────────────────
CONFIGS = {
    "EnToBn": {
        "emoji":        "⭐",
        "lang":         "Bengali",
        "handle":       "editorialvocabappbd",
        "cta_label":    "Download Daily Star Vocab App",
        "header":       "The Daily Star Editorial Vocabulary",
        "data_dir":     "WordOfTheDayEnToBn",
        "meaning_keys": ["bengali_meaning", "meaning"],
        "primary":      "#E91E63",
        "accent":       "#FFC107",
    },
    "EnToHn": {
        "emoji":        "🌟",
        "lang":         "Hindi",
        "handle":       "editorialvocabapp",
        "cta_label":    "Download Hindu Vocab App",
        "header":       "The Hindu Editorial Vocabulary",
        "data_dir":     "WordOfTheDayEnToHn",
        "meaning_keys": ["hindi_meaning", "meaning"],
        "primary":      "#1565C0",
        "accent":       "#FF9800",
    },
}
cfg         = CONFIGS[args.type]
CTA_URL     = "https://cutt.ly/lnSnI0A"
PAGE_HEADER = f"{cfg['header']} — {month_name} {year}"
P           = cfg["primary"]
AC          = cfg["accent"]
EMJ         = cfg["emoji"]
HANDLE      = cfg["handle"]
EMOJI_BAR   = (EMJ + "🌟✨") * 6 + EMJ

# ─── Data Loading ─────────────────────────────────────────────────────────────
FILENAME   = f"{args.date}.json"
REMOTE_URL = (
    f"https://gitlab.com/Mahadi07/rtejhs/-/raw/main/EdData/data/"
    f"{cfg['data_dir']}/{FILENAME}?ref_type=heads"
)

# --- Remote fetch with 3 retries ---
raw_data   = None
RETRIES    = 3
RETRY_WAIT = 3   # seconds between retries

print(f"Fetching: {REMOTE_URL}")
for attempt in range(1, RETRIES + 1):
    try:
        req = urllib.request.Request(REMOTE_URL, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            raw_data = json.loads(r.read().decode("utf-8"))
        print(f"  ✓ Remote fetch succeeded (attempt {attempt})")
        break
    except Exception as e:
        print(f"  ✗ Attempt {attempt}/{RETRIES} failed: {e}")
        if attempt < RETRIES:
            print(f"    Retrying in {RETRY_WAIT}s…")
            time.sleep(RETRY_WAIT)

# --- Local fallback ---
if raw_data is None:
    print("\nAll remote attempts failed. Searching local fallback paths…")

    # Build candidate roots:
    #   1. --repo-root argument (highest priority)
    #   2. Default repo location from project_reference.md
    #   3. Parent of this script's directory (original behaviour — rarely correct)
    #   4. Parent-of-parent (one more level up)
    script_dir = Path(__file__).resolve().parent

    candidate_roots = []
    if args.repo_root:
        candidate_roots.append(Path(args.repo_root))

    # Known default Windows repo path from project_reference.md
    candidate_roots += [
        Path(r"E:\EditorialGitlabServer\rtejhs"),
        Path(r"D:\EditorialGitlabServer\rtejhs"),
        script_dir.parent,
        script_dir.parent.parent,
        script_dir,          # in case script lives inside the repo
    ]

    searched = []
    for root in candidate_roots:
        for subpath in [
            root / "EdData" / "data" / cfg["data_dir"] / FILENAME,
            root / "EdData" / cfg["data_dir"] / FILENAME,
        ]:
            searched.append(str(subpath))
            if subpath.exists():
                print(f"  ✓ Found local file: {subpath}")
                with open(subpath, encoding="utf-8") as f:
                    raw_data = json.load(f)
                break
        if raw_data is not None:
            break

    if raw_data is None:
        print("\n❌  ERROR: Could not load data — searched all paths:")
        for p in searched:
            print(f"       {p}")
        print(
            "\n💡  TIP: Run with --repo-root to point directly at your local repo:\n"
            f'       python generate_cards_pdf.py -t {args.type} {args.date} '
            r'--repo-root "E:\EditorialGitlabServer\rtejhs"'
        )
        exit(1)

vocab_list, day_labels = [], []
if isinstance(raw_data, dict):
    for dk in sorted(raw_data.keys(), key=lambda x: int(x.split("-")[0])):
        vocab_list.append(raw_data[dk])
        day_labels.append(dk.split("-")[0])
else:
    vocab_list = raw_data
    day_labels = [str(i + 1) for i in range(len(vocab_list))]

def get_meaning(v):
    for k in cfg["meaning_keys"]:
        val = v.get(k)
        if val:
            return unicodedata.normalize("NFC", str(val))
    return ""

# ─── Shared CSS ───────────────────────────────────────────────────────────────
# KEY FIX for blank first page:
#   @page { margin: 0 }  +  PDF margin="0mm"  +  .page { height:297mm; padding:10mm }
#   Each .page div is EXACTLY one A4 sheet — no overflow, no phantom first page.
#   .page:last-child { break-after: avoid } prevents a trailing blank page.

CSS = f"""
@page {{ size: A4; margin: 0; }}
*, *::before, *::after {{ box-sizing: border-box; }}
body {{ margin: 0; padding: 0; font-family: Arial, sans-serif; background: #fff; }}

/* ── Base page: 210×297mm, zero-margin, handles its own padding ── */
.page {{
    width: 210mm;
    height: 297mm;
    padding: 8mm 9mm;
    overflow: hidden;
    page-break-after: always;
    break-after: page;
    display: flex;
    flex-direction: column;
}}
/* Prevents the trailing blank page that page-break-after:always would add */
.page:last-child {{
    page-break-after: avoid;
    break-after: avoid;
}}

/* ━━━━━ COVER ━━━━━ */
.cover {{
    background: linear-gradient(155deg, {P}14 0%, {AC}20 100%);
    align-items: center;
    text-align: center;
    justify-content: space-between;
    border: 5px solid {P};
    border-radius: 6px;
    padding: 12mm 14mm;
}}
.cov-logo  {{ font-size: 52px; line-height: 1; margin-bottom: 6px; }}
.cov-title {{ font-size: 25px; font-weight: 900; color: {P}; line-height: 1.3; margin: 6px 0 4px; }}
.cov-sub   {{ font-size: 15px; color: #555; margin-bottom: 12px; }}
.cov-badge {{
    display: inline-block; background: {P}; color: #fff;
    padding: 8px 26px; border-radius: 26px; font-size: 15px; font-weight: 700;
}}
.cov-stats {{
    display: flex; justify-content: center; gap: 36px; margin: 16px 0;
}}
.cov-stat-n {{ font-size: 34px; font-weight: 900; color: {P}; }}
.cov-stat-l {{ font-size: 12px; color: #888; }}
.cov-howto {{
    margin: 10px auto; max-width: 320px; text-align: left;
    background: #fff8; border: 1px solid {P}40; border-radius: 8px; padding: 10px 14px;
    font-size: 13px; color: #444; line-height: 1.7;
}}
.cov-howto strong {{ color: {P}; }}
.cov-features {{
    display: inline-flex; flex-direction: column; align-items: flex-start;
    gap: 4px; font-size: 14px; color: #333; margin: 8px 0;
}}
.cov-cta {{
    margin-top: 12px; padding: 10px 16px; border-radius: 8px;
    background: {AC}30; font-size: 13px; color: #333; width: 100%;
}}
.cov-footer {{ font-size: 11px; color: #aaa; margin-top: auto; padding-top: 8px; }}

/* ━━━━━ SOCIAL MEDIA STRIP ━━━━━ */
.social-strip {{
    width: 100%; margin-top: 10px;
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    border-radius: 10px; padding: 10px 14px;
    display: flex; flex-direction: column; align-items: center; gap: 6px;
}}
.social-strip-title {{
    font-size: 12px; font-weight: 800; color: #fff; letter-spacing: 1.5px;
    text-transform: uppercase; opacity: 0.8;
}}
.social-pills {{
    display: flex; gap: 8px; flex-wrap: wrap; justify-content: center;
}}
.social-pill {{
    display: flex; align-items: center; gap: 6px;
    padding: 5px 13px; border-radius: 20px;
    font-size: 12px; font-weight: 800; color: #fff; text-decoration: none;
    letter-spacing: 0.3px;
}}
.yt  {{ background: #FF0000; }}
.fb  {{ background: #1877F2; }}
.ig  {{ background: linear-gradient(45deg,#f09433,#e6683c,#dc2743,#cc2366,#bc1888); }}
.social-pill-icon {{ font-size: 14px; }}
.social-note {{
    font-size: 10px; color: #aaa; text-align: center; margin-top: 1px;
}}

/* index social bar */
.idx-social {{
    margin-top: 8px; padding: 8px 12px;
    background: linear-gradient(135deg, #1a1a2e, #16213e);
    border-radius: 8px; display: flex; align-items: center;
    justify-content: space-between; flex-shrink: 0;
}}
.idx-social-label {{
    font-size: 11px; color: #aaa; font-weight: 700;
    text-transform: uppercase; letter-spacing: 1px;
}}
.idx-social-pills {{ display: flex; gap: 6px; }}
.idx-pill {{
    display: flex; align-items: center; gap: 4px;
    padding: 3px 10px; border-radius: 14px;
    font-size: 11px; font-weight: 800; color: #fff;
}}


/* ━━━━━ INDEX ━━━━━ */
.pg-title {{
    font-size: 20px; font-weight: 900; color: {P};
    text-align: center; margin-bottom: 10px;
    padding-bottom: 7px; border-bottom: 2px solid {AC};
}}
.idx-grid {{
    display: grid; grid-template-columns: repeat(3, 1fr);
    gap: 5px; flex-grow: 1; align-content: start;
}}
.idx-item {{
    display: flex; align-items: flex-start; gap: 7px;
    padding: 5px 7px; border-left: 3px solid {P};
    background: #fafafa; border-radius: 0 5px 5px 0;
}}
.idx-day  {{ font-size: 11px; font-weight: 700; color: {AC}; min-width: 36px; }}
.idx-word {{ font-size: 13px; font-weight: 800; color: {P}; }}
.idx-mn   {{ font-size: 11px; color: #666; }}

/* ━━━━━ CARD PAGE ━━━━━ */
.frame {{
    border: 2px solid {AC}; border-radius: 6px; padding: 8px;
    flex-grow: 1; display: flex; flex-direction: column;
}}
.ebar {{
    text-align: center; font-size: 14px; letter-spacing: 3px;
    padding: 3px 0; background: {AC}22; border-radius: 4px; margin-bottom: 7px;
}}
.pg-hdr {{
    text-align: center; font-size: 19px; font-weight: 900; color: {P};
    margin-bottom: 8px; padding-bottom: 7px; border-bottom: 2px dashed {AC};
}}
.cards-grid {{
    display: grid; grid-template-columns: repeat(3, 1fr);
    gap: 10px; flex-grow: 1;
}}

/* Each card fills its grid cell vertically */
.card {{
    border: 1px solid #ddd; border-radius: 8px;
    padding: 10px 11px; background: #fff;
    box-shadow: 0 2px 7px rgba(0,0,0,0.07);
    word-wrap: break-word; min-width: 0;
    display: flex; flex-direction: column; gap: 2px;
}}
.w-title {{
    font-size: 18px; font-weight: 900; color: #3F51B5;
    display: flex; align-items: baseline; gap: 5px;
    flex-wrap: wrap; margin-bottom: 4px;
}}
.pos {{ font-size: 12px; color: #2196F3; font-weight: 700; text-transform: uppercase; }}

/* ★ Slightly larger labels for breathing room */
.lbl {{ font-size: 13px; font-weight: 800; color: {AC}; margin-top: 5px; }}

/* ★ FONT SIZE FIX — bumped from 15→17px to fill vertical space */
.mn {{
    font-size: 17px; font-weight: 700; color: #111; line-height: 1.35;
    background: #fffde7; border-radius: 5px; padding: 5px 7px;
    box-shadow: 0 1px 4px #f5e9b550;
}}
/* ★ definition 14→15px */
.def {{ font-size: 15px; color: #333; line-height: 1.4; font-weight: 600; }}
/* ★ synonyms/antonyms 13→14px */
.syn {{ font-size: 14px; color: #388E3C; font-weight: 700; }}
.ant {{ font-size: 14px; color: #C62828; font-weight: 700; }}
/* ★ example 13→14px */
.ex {{
    font-size: 14px; color: #1565C0; font-style: italic; line-height: 1.4;
    background: #E3F2FD; border-radius: 4px; padding: 5px 7px;
    font-weight: 600; margin-top: 4px;
}}
.ex-bn {{
    font-size: 13px; color: #6d4c41; background: #fbe9e7;
    border-radius: 4px; padding: 3px 6px; font-weight: 600; margin-top: 2px;
}}
.pg-cta {{
    text-align: center; font-size: 12px; color: #555;
    font-weight: 600; margin-top: 7px;
}}

/* ━━━━━ WEEKLY REVISION ━━━━━ */
.wk-title {{
    font-size: 21px; font-weight: 900; color: {P};
    text-align: center; margin-bottom: 2px;
}}
.wk-sub   {{ font-size: 13px; color: #777; text-align: center; margin-bottom: 6px; }}
.wk-badge {{
    display: block; width: fit-content; margin: 0 auto 10px;
    background: {P}; color: #fff; padding: 4px 20px;
    border-radius: 20px; font-size: 13px; font-weight: 700;
}}
.wk-grid  {{
    display: grid; grid-template-columns: 1fr 1fr;
    gap: 8px; flex-grow: 1; align-content: start;
}}
.wk-card  {{
    border: 1px solid {P}40; border-radius: 8px; padding: 9px 11px;
    background: linear-gradient(135deg, #fff, {P}06);
    display: flex; flex-direction: column; gap: 3px;
}}
.wk-word  {{ font-size: 19px; font-weight: 900; color: #3F51B5; }}
.wk-pos   {{ font-size: 11px; color: #999; text-transform: uppercase; font-weight: 700; }}
.wk-mn    {{
    font-size: 14px; font-weight: 700; color: #111;
    background: #fffde7; padding: 3px 7px; border-radius: 4px;
}}
.wk-def   {{ font-size: 13px; color: #444; line-height: 1.35; }}
.wk-syn   {{ font-size: 12px; color: #388E3C; font-weight: 700; }}
.wk-ant   {{ font-size: 12px; color: #C62828; font-weight: 700; }}
.wk-ex    {{
    font-size: 12px; color: #1565C0; font-style: italic;
    background: #E3F2FD; padding: 3px 6px; border-radius: 3px;
}}
.wk-stars {{ font-size: 12px; color: {AC}; letter-spacing: 1px; }}

/* ━━━━━ MCQ ━━━━━ */
.mcq-title {{ font-size: 21px; font-weight: 900; color: {P}; text-align: center; margin-bottom: 2px; }}
.mcq-sub   {{ font-size: 13px; color: #777; text-align: center; margin-bottom: 10px; }}
.mcq-list  {{ display: flex; flex-direction: column; gap: 8px; flex-grow: 1; }}
.mcq-item  {{ border: 1px solid #ddd; border-radius: 6px; padding: 7px 11px; }}
.mcq-q     {{ font-size: 14px; font-weight: 700; color: #222; margin-bottom: 5px; }}
.mcq-opts  {{ display: grid; grid-template-columns: 1fr 1fr; gap: 3px; }}
.mcq-opt   {{ font-size: 13px; color: #333; padding: 1px 4px; }}
.mcq-opt b {{ color: {P}; }}
.ans-key   {{
    margin-top: 10px; padding: 8px 14px; background: #f5f5f5;
    border-radius: 6px; font-size: 12px; color: #555; text-align: center;
}}
"""

# ─── Page Builders ────────────────────────────────────────────────────────────

def build_cover():
    n = len(vocab_list)
    features = []
    if not args.no_index:    features.append("📋 Word Index (all words at a glance)")
    if not args.no_revision: features.append("📖 4 Weekly Revision Pages")
    if not args.no_mcq:      features.append("📝 10-Question Final MCQ Test")
    feats_html = "".join(f'<div>✅ {f}</div>' for f in features)

    return f'''<div class="page cover">
  <div class="cov-logo">{EMJ * 3}</div>
  <div class="cov-title">{cfg["header"]}</div>
  <div class="cov-sub">{month_name} {year} · Complete Monthly Vocabulary eBook</div>
  <div class="cov-badge">📚 {n} Words · {cfg["lang"]} Meanings</div>

  <div class="cov-stats">
    <div><div class="cov-stat-n">{n}</div><div class="cov-stat-l">Words</div></div>
    <div><div class="cov-stat-n">4</div><div class="cov-stat-l">Weeks</div></div>
    <div><div class="cov-stat-n">10</div><div class="cov-stat-l">MCQ</div></div>
  </div>

  <div class="cov-howto">
    <strong>How to use this eBook:</strong><br>
    1️⃣ Study 6 cards/day — read word, meaning & definition<br>
    2️⃣ After every 7 days → complete the Revision page<br>
    3️⃣ At the end → attempt the 10-MCQ Final Test<br>
    4️⃣ Check answers in the key at the bottom of the test page
  </div>

  <div class="cov-features">{feats_html}</div>

  <div class="cov-cta">
    📱 {cfg["cta_label"]} — get daily updates on your phone<br>
    <a href="{CTA_URL}" style="color:{P}; font-weight:800;">{CTA_URL}</a>
  </div>

  <!-- ── Social Media Strip ── -->
  <div class="social-strip">
    <div class="social-strip-title">🌐 Follow Us &amp; Stay Updated</div>
    <div class="social-pills">
      <span class="social-pill yt">
        <span class="social-pill-icon">▶</span> @{HANDLE}
      </span>
      <span class="social-pill fb">
        <span class="social-pill-icon">f</span> {HANDLE}
      </span>
      <span class="social-pill ig">
        <span class="social-pill-icon">◈</span> {HANDLE}
      </span>
    </div>
    <div class="social-note">
      Daily vocab drops · PDF eBooks · Editorial word tips · Free quizzes
    </div>
  </div>

  <div class="cov-footer">© {year} Editorial Vocab App &nbsp;·&nbsp; {month_name} {year} Edition &nbsp;·&nbsp; All platforms: <strong>{HANDLE}</strong></div>
</div>'''


def build_index():
    items = "".join(
        f'''<div class="idx-item">
  <span class="idx-day">Day&nbsp;{day_labels[i]}</span>
  <div>
    <div class="idx-word">{v["word"].capitalize()}</div>
    <div class="idx-mn">{get_meaning(v)[:24]}{"…" if len(get_meaning(v)) > 24 else ""}</div>
  </div>
</div>'''
        for i, v in enumerate(vocab_list)
    )
    return f'''<div class="page">
  <div class="pg-title">📋 Word Index — {month_name} {year}</div>
  <div class="idx-grid">{items}</div>
  <div class="idx-social">
    <div class="idx-social-label">📲 Follow for daily vocab</div>
    <div class="idx-social-pills">
      <span class="idx-pill yt">▶ YouTube</span>
      <span class="idx-pill fb">f Facebook</span>
      <span class="idx-pill ig">◈ Instagram</span>
    </div>
    <div style="font-size:11px; color:#ddd; font-weight:700;">@{HANDLE}</div>
  </div>
</div>'''


def build_card_page(words):
    cards = ""
    for v in words:
        word = v["word"].capitalize()
        pos  = v.get("part_of_speech", "").lower()
        mn   = get_meaning(v)
        defn = v.get("definition", "")
        syns = " · ".join(v.get("synonyms", [])[:3])
        ants = " · ".join(v.get("antonyms", [])[:3])
        ex   = str(v.get("example", "")).strip()
        exbn = str(v.get("example_bn", "") or "").strip()

        ex_html = ""
        if ex:
            ex_html = f'<div class="lbl">Example:</div><div class="ex">{ex}</div>'
            if exbn:
                ex_html += f'<div class="ex-bn">({exbn})</div>'

        cards += f'''<div class="card">
  <div class="w-title">{EMJ}&nbsp;{word}&nbsp;<span class="pos">{pos}</span></div>
  <div class="lbl">Meaning:</div>
  <div class="mn">{mn}</div>
  <div class="lbl">Definition:</div>
  <div class="def">{defn}</div>
  <div class="lbl">Synonyms:</div>
  <div class="syn">{syns}</div>
  <div class="lbl">Antonyms:</div>
  <div class="ant">{ants}</div>
  {ex_html}
</div>'''

    return f'''<div class="page">
  <div class="frame">
    <div class="ebar">{EMOJI_BAR}</div>
    <div class="pg-hdr">{PAGE_HEADER}</div>
    <div class="cards-grid">{cards}</div>
    <div class="pg-cta">{cfg["cta_label"]}: <a href="{CTA_URL}">{CTA_URL}</a></div>
    <div class="ebar" style="margin-top:6px;">{EMOJI_BAR}</div>
  </div>
</div>'''


def build_revision(week_words, week_num, day_start, day_end):
    """Weekly revision page — 2-column grid, one card per word."""

    def strength_stars(v):
        """Visual difficulty indicator based on synonym count."""
        count = len(v.get("synonyms", []))
        if count >= 4: return "★★★ Advanced"
        if count >= 2: return "★★ Intermediate"
        return "★ Basic"

    cards = ""
    for v in week_words:
        word = v["word"].capitalize()
        pos  = v.get("part_of_speech", "").lower()
        mn   = get_meaning(v)
        defn = v.get("definition", "")
        syns = " · ".join(v.get("synonyms", [])[:3])
        ants = " · ".join(v.get("antonyms", [])[:3])
        ex   = str(v.get("example", "")).strip()

        ex_html = (
            f'<div class="wk-ex">{ex[:115]}{"…" if len(ex) > 115 else ""}</div>'
            if ex else ""
        )

        cards += f'''<div class="wk-card">
  <div>
    <span class="wk-word">{word}</span>&nbsp;
    <span class="wk-pos">— {pos}</span>
  </div>
  <div class="wk-stars">{strength_stars(v)}</div>
  <div class="wk-mn">{mn}</div>
  <div class="wk-def">{defn[:130]}{"…" if len(defn) > 130 else ""}</div>
  <div class="wk-syn">≈ Syn: {syns}</div>
  <div class="wk-ant">≠ Ant: {ants}</div>
  {ex_html}
</div>'''

    return f'''<div class="page">
  <div class="wk-title">📖 Weekly Revision — Week {week_num}</div>
  <div class="wk-sub">Day {day_start}–{day_end} &nbsp;·&nbsp; {len(week_words)} Words</div>
  <span class="wk-badge">Week {week_num} Quick Review</span>
  <div class="wk-grid">{cards}</div>
</div>'''


def build_mcq():
    """10-question MCQ page with answer key. Seed is deterministic per month."""
    rng = random.Random(int(month) * 97 + int(year))
    test_words = rng.sample(vocab_list, min(10, len(vocab_list)))
    q_types    = ["meaning", "synonym", "definition"]

    items, answers = "", []

    for i, v in enumerate(test_words):
        word = v["word"].capitalize()
        mn   = get_meaning(v)
        defn = v.get("definition", "")[:85]
        syns = v.get("synonyms", [])

        wrong_pool = [w for w in vocab_list if w["word"] != v["word"]]
        wrong3     = rng.sample(wrong_pool, min(3, len(wrong_pool)))

        qt = q_types[i % 3]

        if qt == "meaning":
            q       = f'What is the {cfg["lang"]} meaning of "<strong>{word}</strong>"?'
            correct = mn[:48] + ("…" if len(mn) > 48 else "")
            wrongs  = [
                (get_meaning(w)[:48] + ("…" if len(get_meaning(w)) > 48 else ""))
                for w in wrong3
            ]
        elif qt == "synonym":
            q       = f'Choose the best synonym for "<strong>{word}</strong>":'
            correct = syns[0] if syns else mn[:20]
            wrongs  = [
                (w.get("synonyms", ["—"])[0] if w.get("synonyms") else w["word"])
                for w in wrong3
            ]
        else:  # definition → identify the word
            q       = f'Which word fits this definition?<br><em>"{defn}…"</em>'
            correct = word
            wrongs  = [w["word"].capitalize() for w in wrong3]

        options = [correct] + wrongs
        rng.shuffle(options)
        letter = "ABCD"[options.index(correct)]
        answers.append(f"Q{i + 1}:{letter}")

        opts_html = "".join(
            f'<div class="mcq-opt"><b>{chr(65 + j)}.</b> {o}</div>'
            for j, o in enumerate(options)
        )

        items += f'''<div class="mcq-item">
  <div class="mcq-q">Q{i + 1}. {q}</div>
  <div class="mcq-opts">{opts_html}</div>
</div>'''

    ans_str = " &nbsp;|&nbsp; ".join(answers)

    return f'''<div class="page">
  <div class="mcq-title">📝 Final Mini Test</div>
  <div class="mcq-sub">
    {month_name} {year} &nbsp;·&nbsp; 10 Questions &nbsp;·&nbsp; Choose the best answer
  </div>
  <div class="mcq-list">{items}</div>
  <div class="ans-key">🔑 Answer Key: &nbsp; {ans_str}</div>
</div>'''


# ─── Build Weekly-Revision Lookup ─────────────────────────────────────────────
# Divide vocab into weeks of 7. After the card-page that contains week N's LAST
# word, insert the weekly revision page for that week.

WEEK_SIZE = 7
weeks     = [vocab_list[i:i + WEEK_SIZE] for i in range(0, len(vocab_list), WEEK_SIZE)]

# week_at_page[page_idx] = (week_num, week_words, day_start, day_end)
week_at_page = {}
cursor = 0
for wk_i, wk_words in enumerate(weeks):
    if not wk_words:
        continue
    day_start          = cursor + 1
    day_end            = cursor + len(wk_words)
    last_word_page_idx = (cursor + len(wk_words) - 1) // 6
    week_at_page[last_word_page_idx] = (wk_i + 1, wk_words, day_start, day_end)
    cursor += len(wk_words)

# ─── Assemble Full HTML ───────────────────────────────────────────────────────
parts = [f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{PAGE_HEADER}</title>
<style>{CSS}</style>
</head>
<body>''']

if not args.no_cover:
    parts.append(build_cover())

if not args.no_index:
    parts.append(build_index())

pages_of_cards = [vocab_list[i:i + 6] for i in range(0, len(vocab_list), 6)]

for p_idx, words in enumerate(pages_of_cards):
    if not words:
        continue
    parts.append(build_card_page(words))
    # Insert weekly revision immediately after the card page that finishes a week
    if not args.no_revision and p_idx in week_at_page:
        wn, ww, ds, de = week_at_page[p_idx]
        parts.append(build_revision(ww, wn, ds, de))

if not args.no_mcq:
    parts.append(build_mcq())

parts.append("</body>\n</html>")
html_content = "\n".join(parts)

# ─── Render PDF via Playwright ────────────────────────────────────────────────
prefix   = "Hindu" if args.type == "EnToHn" else "Star"
out_name = f"Editorial_Vocab_{prefix}_{month_abbr}_{year[-2:]}.pdf"
out_path = Path(out_name)

print(f"Rendering PDF → {out_path} …")
with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True)
    pg      = browser.new_page(viewport={"width": 1400, "height": 1900})
    pg.set_content(html_content, wait_until="networkidle")
    pg.pdf(
        path=str(out_path),
        format="A4",
        print_background=True,
        # ★ FIX: margins handled entirely by CSS (@page + .page padding)
        #         Setting PDF margins to 0 prevents the double-margin that
        #         caused the blank first page in the original script.
        margin={"top": "0mm", "bottom": "0mm", "left": "0mm", "right": "0mm"},
    )
    browser.close()

total_pages = (
    (1 if not args.no_cover else 0)
    + (1 if not args.no_index else 0)
    + len(pages_of_cards)
    + (len(weeks) if not args.no_revision else 0)
    + (1 if not args.no_mcq else 0)
)
print(f"✅  PDF saved:  {out_path}")
print(f"📊  {len(vocab_list)} words · {len(pages_of_cards)} card pages · "
      f"{len(weeks)} revision pages · ~{total_pages} total pages")
