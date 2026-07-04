"""
generate_10vocab.py
───────────────────
Generate a premium vocabulary eBook PDF from the master word JSON files.

JSON structure expected:
    { "wordMeaning": [ "english phrase : meaning", … ] }

The English and meaning are split on the FIRST " : " (space-colon-space).
Some entries also carry inline synonyms in parentheses, e.g.:
    "abdicate : পরিত্যাগ করা (cede, relinquish, renounce)"
Those are extracted and shown as a small hint on the card.

Usage
──────
# Full A–Z (EnToBn)
python generate_10vocab.py -t EnToBn

# Letters A–D only  (Vol 1 bundle)
python generate_10vocab.py -t EnToBn --letter A B C D

# Exact word-number range  (Part 1 of 4)
python generate_10vocab.py -t EnToBn --start 1 --end 2500

# Hindi edition, custom output name
python generate_10vocab.py -t EnToHn --letter M N --out "Hindu_M-N.pdf"

# Point at repo root when running offline
python generate_10vocab.py -t EnToBn --repo-root "E:\\EditorialGitlabServer\\rtejhs"
"""

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from playwright.sync_api import sync_playwright

# Force UTF-8 encoding for console output to prevent crashes on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# ─── CLI ──────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(
    description="Master Vocabulary eBook PDF generator",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog=__doc__,
)
parser.add_argument("-t", "--type", choices=["EnToBn", "EnToHn"], required=True)
parser.add_argument("--letter", nargs="+", metavar="A",
                    help="Filter by starting letter(s), e.g. --letter A B C")
parser.add_argument("--start",  type=int, default=None,
                    help="First serial number (1-based)")
parser.add_argument("--end",    type=int, default=None,
                    help="Last serial number (1-based, inclusive)")
parser.add_argument("--out",    default=None, help="Output PDF filename")
parser.add_argument("--repo-root", default=None,
                    help=r'Local repo root, e.g. "E:\EditorialGitlabServer\rtejhs"')
parser.add_argument("--cards-per-page", type=int, choices=[12,16,18,20], default=12,
                    help="Cards per page (default 12 = 2 cols x 6 rows)")
parser.add_argument("--no-cover",    action="store_true")
parser.add_argument("--no-chapters", action="store_true",
                    help="Skip alphabetical chapter divider pages")
args = parser.parse_args()

# ─── Config ───────────────────────────────────────────────────────────────────
CONFIGS = {
    "EnToBn": {
        "emoji":     "⭐",
        "lang":      "Bengali",
        "lang_flag": "🇧🇩",
        "handle":    "editorialvocabappbd",
        "cta_label": "Download Daily Star Vocab App",
        "title":     "The Daily Star Editorial",
        "subtitle":  "Master Vocabulary eBook",
        "json_file": "master_words.json",
        "primary":   "#B71C1C",
        "accent":    "#FFC107",
        "secondary": "#FF7043",
    },
    "EnToHn": {
        "emoji":     "🌟",
        "lang":      "Hindi",
        "lang_flag": "🇮🇳",
        "handle":    "editorialvocabapp",
        "cta_label": "Download Hindu Vocab App",
        "title":     "The Hindu Editorial",
        "subtitle":  "Master Vocabulary eBook",
        "json_file": "master_words_hn.json",
        "primary":   "#1A237E",
        "accent":    "#FF9800",
        "secondary": "#29B6F6",
    },
}
cfg    = CONFIGS[args.type]
P      = cfg["primary"]
AC     = cfg["accent"]
SEC    = cfg["secondary"]
EMJ    = cfg["emoji"]
CTA    = "https://cutt.ly/lnSnI0A"
HANDLE = cfg["handle"]
CPP    = args.cards_per_page
COLS   = 2   # always 2 columns; rows = CPP // 2

# ─── Data Loading ─────────────────────────────────────────────────────────────
script_dir = Path(__file__).resolve().parent

roots = []
if args.repo_root:
    roots.append(Path(args.repo_root))
roots += [
    Path(r"E:\EditorialGitlabServer\rtejhs"),
    Path(r"D:\EditorialGitlabServer\rtejhs"),
    script_dir.parent,
    script_dir.parent.parent,
    script_dir,
]

raw_data = None
searched = []
for root in roots:
    for p in [
        root / "EdData" / "data" / cfg["json_file"],
        root / "EdData" / cfg["json_file"],
        root / cfg["json_file"],
        script_dir / cfg["json_file"],
    ]:
        searched.append(str(p))
        if p.exists():
            print(f"📂 Loading: {p}  ({p.stat().st_size / 1024:.1f} KiB)")
            with open(p, encoding="utf-8") as f:
                raw_data = json.load(f)
            break
    if raw_data is not None:
        break

if raw_data is None:
    print("❌  JSON not found. Searched:")
    for s in searched:
        print(f"     {s}")
    print(
        f'\n💡  TIP: python generate_10vocab.py -t {args.type} '
        r'--repo-root "E:\EditorialGitlabServer\rtejhs"'
    )
    sys.exit(1)

# ─── Parse raw list from JSON ─────────────────────────────────────────────────
# Expected: { "wordMeaning": ["english : meaning", ...] }
if isinstance(raw_data, dict):
    for key in ("wordMeaning", "word_meaning", "words", "data"):
        if key in raw_data and isinstance(raw_data[key], list):
            raw_list = raw_data[key]
            break
    else:
        raw_list = next((v for v in raw_data.values() if isinstance(v, list)), [])
elif isinstance(raw_data, list):
    raw_list = raw_data
else:
    print("❌  Unexpected JSON root type.")
    sys.exit(1)

print(f"✓  Found {len(raw_list):,} raw entries")

# ─── Parse each "english : meaning" string ────────────────────────────────────
PARENS_RE = re.compile(r'\(([^)]+)\)\s*$')

def parse_entry(raw: str):
    raw = raw.strip()
    sep = " : " if " : " in raw else (":" if ":" in raw else None)
    if sep is None:
        return None
    parts = raw.split(sep, 1)
    en    = parts[0].strip()
    rest  = parts[1].strip()

    hint = ""
    m = PARENS_RE.search(rest)
    if m:
        hint = m.group(1).strip()
        rest = rest[:m.start()].strip()

    mn = re.sub(r'\s*,\s*', ', ', rest).strip().rstrip(',').strip()
    if not en or not mn:
        return None
    return {"en": en, "mn": mn, "hint": hint}

entries = [r for raw in raw_list
           if isinstance(raw, str) and (r := parse_entry(raw)) is not None]

TOTAL = len(entries)
print(f"✓  Parsed {TOTAL:,} valid entries")

# ─── Filter ───────────────────────────────────────────────────────────────────
filtered = [(i + 1, e) for i, e in enumerate(entries)]

if args.letter:
    letters = {l.upper() for l in args.letter}
    filtered = [(s, e) for s, e in filtered if e["en"][:1].upper() in letters]

if args.start is not None or args.end is not None:
    lo = args.start or 1
    hi = args.end   or TOTAL
    filtered = [(s, e) for s, e in filtered if lo <= s <= hi]

if not filtered:
    print("❌  No entries matched the given filters.")
    sys.exit(1)

print(f"✓  After filtering: {len(filtered):,} entries  "
      f"(#{filtered[0][0]}–#{filtered[-1][0]})")

# ─── Volume label ─────────────────────────────────────────────────────────────
if args.letter:
    letts = sorted({e["en"][:1].upper() for _, e in filtered})
    vol_title   = f"Words {letts[0]}–{letts[-1]}"
    range_label = "-".join(letts)
elif args.start or args.end:
    vol_title   = f"Words #{filtered[0][0]:,}–#{filtered[-1][0]:,}"
    range_label = f"{filtered[0][0]}-{filtered[-1][0]}"
else:
    vol_title   = "Complete A–Z Edition"
    range_label = "Complete"

out_path = (
    Path(args.out) if args.out
    else Path(f"MasterVocab_{'Hindu' if args.type == 'EnToHn' else 'Star'}"
              f"_{re.sub(r'[^\\w\\-]', '_', range_label)}.pdf")
)

# ─── Chapter grouping ─────────────────────────────────────────────────────────
chapters: dict[str, list] = defaultdict(list)
chapter_order = []
for serial, e in filtered:
    letter = e["en"][:1].upper() or "#"
    if letter not in chapters:
        chapter_order.append(letter)
    chapters[letter].append((serial, e))

# ─── CSS ──────────────────────────────────────────────────────────────────────
CSS = f"""
@page {{ size: A4; margin: 0; }}
*, *::before, *::after {{ box-sizing: border-box; }}
body {{ margin: 0; padding: 0; font-family: Arial, sans-serif; background: #fff; }}

.page {{
    width: 210mm; height: 297mm;
    padding: 6mm 8mm;
    overflow: hidden;
    page-break-after: always; break-after: page;
    display: flex; flex-direction: column;
}}
.page:last-child {{ page-break-after: avoid; break-after: avoid; }}

/* ━━━━━ COVER ━━━━━ */
.cover {{
    background: linear-gradient(155deg, {P}15 0%, {AC}20 100%);
    border: 5px double {P}; border-radius: 10px;
    padding: 11mm 13mm;
    align-items: center; text-align: center;
    justify-content: space-between;
}}
.cov-logo  {{ font-size: 52px; margin-bottom: 4px; }}
.cov-pub   {{ font-size: 12px; font-weight: 700; color: {SEC};
               letter-spacing: 2px; text-transform: uppercase; margin-bottom: 4px; }}
.cov-title {{ font-size: 24px; font-weight: 900; color: {P}; line-height: 1.25; margin: 4px 0; }}
.cov-sub   {{ font-size: 15px; font-weight: 700; color: #555; margin-bottom: 6px; }}
.cov-divider {{ width: 60px; height: 4px; background: {AC};
                 border-radius: 3px; margin: 5px auto 10px; }}
.cov-vol   {{ display: inline-block; background: {P}; color: #fff;
               padding: 7px 28px; border-radius: 28px;
               font-size: 14px; font-weight: 800; margin-bottom: 8px; }}
.cov-stats {{ display: flex; justify-content: center; gap: 38px; margin: 8px 0 12px; }}
.stat-n    {{ font-size: 34px; font-weight: 900; color: {P}; }}
.stat-l    {{ font-size: 11px; color: #999; text-transform: uppercase; letter-spacing: 1px; }}
.cov-pills {{ display: flex; flex-wrap: wrap; justify-content: center;
               gap: 4px; margin: 4px 0 10px; }}
.ch-pill   {{ width: 24px; height: 24px; line-height: 24px; text-align: center;
               background: {P}15; border: 1px solid {P}40; border-radius: 5px;
               font-size: 12px; font-weight: 900; color: {P}; }}
.cov-note  {{ max-width: 320px; margin: 0 auto 8px; text-align: left;
               background: #fff9; border: 1px solid {P}30; border-radius: 8px;
               padding: 9px 13px; font-size: 13px; color: #444; line-height: 1.7; }}
.cov-note strong {{ color: {P}; }}

.social-strip {{
    width: 100%; margin-top: 10px;
    background: linear-gradient(135deg, #1a1a2e, #16213e);
    border-radius: 10px; padding: 9px 13px;
    display: flex; flex-direction: column; align-items: center; gap: 5px;
}}
.soc-title {{ font-size: 11px; font-weight: 800; color: #fff;
               letter-spacing: 1.5px; text-transform: uppercase; opacity: 0.75; }}
.soc-pills {{ display: flex; gap: 7px; flex-wrap: wrap; justify-content: center; }}
.soc-pill  {{ display: flex; align-items: center; gap: 5px; padding: 5px 12px;
               border-radius: 18px; font-size: 12px; font-weight: 800; color: #fff; }}
.yt {{ background: #FF0000; }}
.fb {{ background: #1877F2; }}
.ig {{ background: linear-gradient(45deg,#f09433,#e6683c,#dc2743,#cc2366,#bc1888); }}
.soc-note  {{ font-size: 10px; color: #999; }}
.cov-footer {{ font-size: 10px; color: #bbb; margin-top: auto; padding-top: 5px; }}

/* ━━━━━ CHAPTER DIVIDER ━━━━━ */
.chapter-div {{
    flex-grow: 1; display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    background: linear-gradient(150deg, {P}10 0%, {AC}18 100%);
    border: 3px solid {P}; border-radius: 10px;
    text-align: center; gap: 10px; padding: 18mm;
}}
.ch-letter {{ font-size: 110px; font-weight: 900; color: {P}; line-height: 1; opacity:.9; }}
.ch-label  {{ font-size: 15px; font-weight: 700; color: #666; }}
.ch-count  {{ display: inline-block; background: {P}; color: #fff;
               padding: 5px 20px; border-radius: 20px; font-size: 14px; font-weight: 800; }}
.ch-range  {{ font-size: 11px; color: #999; }}

/* ━━━━━ CARD PAGE ━━━━━ */
.pg-hdr {{
    font-size: 13px; font-weight: 900; color: {P};
    padding: 4px 0 5px; border-bottom: 2px dashed {AC};
    margin-bottom: 5px; flex-shrink: 0;
    display: flex; justify-content: space-between; align-items: baseline;
}}
.pg-hdr-page {{ font-size: 11px; color: #aaa; font-weight: 600; }}

.cards-grid {{
    display: grid;
    grid-template-columns: repeat({COLS}, 1fr);
    gap: 7px;
    flex-grow: 1;
    align-content: start;
}}

.card {{
    border: 1.5px solid #e8e8e8;
    border-left: 4px solid {P};
    border-radius: 7px;
    padding: 7px 10px; background: #fff;
    box-shadow: 0 2px 6px rgba(0,0,0,0.06);
    display: flex; flex-direction: column; gap: 3px;
    min-width: 0; word-wrap: break-word;
    position: relative;
}}
.card-serial {{
    position: absolute; top: 5px; right: 7px;
    font-size: 9px; color: #ccc; font-weight: 700;
}}
.en   {{ font-size: 14px; font-weight: 900; color: #3F51B5;
          line-height: 1.2; padding-right: 30px; }}
.mn   {{ font-size: 15px; font-weight: 800; color: #111;
          background: #fffde7; border-radius: 5px;
          padding: 4px 8px; line-height: 1.35;
          box-shadow: 0 1px 3px #f5e9b545; }}
.hint {{ font-size: 11px; color: #388E3C; font-weight: 700;
          line-height: 1.25; padding-left: 2px; }}

.pg-footer {{
    flex-shrink: 0; margin-top: 5px;
    display: flex; align-items: center; justify-content: space-between;
    border-top: 1px solid #eee; padding-top: 3px;
}}
.pg-cta    {{ font-size: 9px; color: #aaa; }}
.pg-socs   {{ display: flex; gap: 5px; }}
.pg-soc    {{ font-size: 9px; font-weight: 800; color: #fff;
               padding: 2px 7px; border-radius: 9px; }}
.pg-handle {{ font-size: 9px; color: #ccc; font-weight: 700; }}
"""

# ─── Page builders ────────────────────────────────────────────────────────────

def build_cover():
    n      = len(filtered)
    n_ch   = len(chapter_order)
    pills  = "".join(f'<span class="ch-pill">{l}</span>' for l in chapter_order)
    s0, s1 = filtered[0][0], filtered[-1][0]
    return f'''<div class="page cover">
  <div class="cov-logo">{EMJ * 4}</div>
  <div class="cov-pub">{cfg["lang_flag"]} {cfg["lang"]} Edition</div>
  <div class="cov-title">{cfg["title"]}</div>
  <div class="cov-sub">{cfg["subtitle"]}</div>
  <div class="cov-divider"></div>
  <div class="cov-vol">📚 {vol_title} &nbsp;·&nbsp; {n:,} Words &amp; Phrases</div>
  <div class="cov-stats">
    <div><div class="stat-n">{n:,}</div><div class="stat-l">Entries</div></div>
    <div><div class="stat-n">{n_ch}</div><div class="stat-l">Chapters</div></div>
    <div><div class="stat-n">{TOTAL:,}</div><div class="stat-l">Master DB</div></div>
  </div>
  <div class="cov-pills">{pills}</div>
  <div class="cov-note">
    <strong>How to use this eBook:</strong><br>
    📖 Each card: English word/phrase &amp; {cfg["lang"]} meaning<br>
    🔢 Serial number tracks progress out of {TOTAL:,} total entries<br>
    🔤 Words grouped A–Z by chapter for easy lookup<br>
    💡 Inline synonym hints shown where available<br>
    📌 This volume: <strong>#{s0:,} – #{s1:,}</strong>
  </div>
  <div class="social-strip">
    <div class="soc-title">🌐 Follow for Daily Vocabulary Updates</div>
    <div class="soc-pills">
      <span class="soc-pill yt">▶ @{HANDLE}</span>
      <span class="soc-pill fb">f {HANDLE}</span>
      <span class="soc-pill ig">◈ {HANDLE}</span>
    </div>
    <div class="soc-note">Daily vocab drops · PDF eBooks · Free quizzes · Editorial tips</div>
  </div>
  <div class="cov-footer">
    © Editorial Vocab App &nbsp;·&nbsp; {vol_title} &nbsp;·&nbsp;
    All platforms: <strong>{HANDLE}</strong>
  </div>
</div>'''


def build_chapter_divider(letter, words_in_ch):
    s0 = words_in_ch[0][0]
    s1 = words_in_ch[-1][0]
    return f'''<div class="page">
  <div class="chapter-div">
    <div class="ch-letter">{letter}</div>
    <div class="ch-label">Chapter · Letter {letter}</div>
    <div class="ch-count">{len(words_in_ch):,} Entries</div>
    <div class="ch-range">Serial #{s0:,} — #{s1:,} &nbsp;·&nbsp; of {TOTAL:,} total</div>
  </div>
</div>'''


def build_card_page(batch, page_num, total_pages, chapter_letter=""):
    cards = ""
    for serial, e in batch:
        hint_html = (
            f'<div class="hint">≈ {e["hint"][:80]}{"…" if len(e["hint"]) > 80 else ""}</div>'
            if e["hint"] else ""
        )
        cards += f'''<div class="card">
  <div class="card-serial">#{serial:05d}</div>
  <div class="en">{EMJ}&nbsp;{e["en"]}</div>
  <div class="mn">{e["mn"]}</div>
  {hint_html}
</div>'''

    hdr = (
        f'{cfg["title"]} · {cfg["lang"]} · {vol_title}'
        + (f' · [{chapter_letter}]' if chapter_letter else '')
    )
    return f'''<div class="page">
  <div class="pg-hdr">
    <span>{hdr}</span>
    <span class="pg-hdr-page">Page {page_num} / {total_pages}</span>
  </div>
  <div class="cards-grid">{cards}</div>
  <div class="pg-footer">
    <div class="pg-cta">{cfg["cta_label"]}: <a href="{CTA}">{CTA}</a></div>
    <div class="pg-socs">
      <span class="pg-soc yt">▶ YT</span>
      <span class="pg-soc fb">f FB</span>
      <span class="pg-soc ig">◈ IG</span>
    </div>
    <div class="pg-handle">@{HANDLE}</div>
  </div>
</div>'''


# ─── Total page count ─────────────────────────────────────────────────────────
total_card_pages = sum(-(-len(chapters[l]) // CPP) for l in chapter_order)
total_pages = (
    (1 if not args.no_cover else 0)
    + (len(chapter_order) if not args.no_chapters else 0)
    + total_card_pages
)

# ─── Assemble HTML ────────────────────────────────────────────────────────────
parts = [f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{cfg["title"]} {cfg["subtitle"]} · {vol_title}</title>
<style>{CSS}</style>
</head>
<body>''']

if not args.no_cover:
    parts.append(build_cover())

page_num = (2 if not args.no_cover else 1)

for letter in chapter_order:
    ch_words = chapters[letter]
    if not args.no_chapters:
        parts.append(build_chapter_divider(letter, ch_words))
        page_num += 1
    for i in range(0, len(ch_words), CPP):
        parts.append(build_card_page(ch_words[i:i + CPP], page_num, total_pages, letter))
        page_num += 1

parts.append("</body>\n</html>")

# ─── Render PDF ───────────────────────────────────────────────────────────────
html_content = "\n".join(parts)
print(f"\n🖨  Rendering → {out_path}")
print(f"    Entries : {len(filtered):,}  |  Card pages : {total_card_pages}"
      f"  |  Total pages : {total_pages}")

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True)
    pg      = browser.new_page(viewport={"width": 1400, "height": 1900})
    pg.set_content(html_content, wait_until="networkidle")
    pg.pdf(
        path=str(out_path),
        format="A4",
        print_background=True,
        margin={"top": "0mm", "bottom": "0mm", "left": "0mm", "right": "0mm"},
    )
    browser.close()

print(f"\n✅  Done!  →  {out_path}")
print(f"📊  {len(filtered):,} entries · {total_card_pages} card pages"
      f" · {total_pages} total pages")
print(f"    Range : #{filtered[0][0]:,} – #{filtered[-1][0]:,} of {TOTAL:,}")
