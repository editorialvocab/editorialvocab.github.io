# Editorial Vocabulary App — Master Project Reference
> Last updated: April 2026 | Owner: Mahadi | Location: Tangail, Dhaka, BD

---

## 1. App Overview

**Tagline:** "Don't just read editorials — master them."

**Goal:** Build the #1 editorial learning app for competitive exam aspirants in India and Bangladesh.

**App Store Listings:**
- India listing name: **Hindu Vocab & Editorials**
- Bangladesh listing name: **Daily Star Vocab & Editorials**
- In-app display name: **Editorial Vocab**
- Play Store ID: `megaminds.dailyeditorialword`
- App download short URL: `https://cutt.ly/lnSnI0A`
- Play Store full URL: `https://play.google.com/store/apps/details?id=megaminds.dailyeditorialword`

**Current Stats (April 2026):**
- Total installs: ~106,000
- Monthly active users: ~3,700
- Weekly active users: ~1,300
- Daily active users: ~296
- In-app purchase revenue: ~$9/month
- AdMob revenue: ~$5/month
- Total monthly revenue: ~$14/month
- Target monthly revenue: $50/month

---

## 2. Target Audiences

### 🇮🇳 India
- UPSC aspirants
- SSC (CGL, CHSL, MTS)
- Banking (IBPS PO, Clerk, SBI)
- Railway & Defence exams

**Content source:** The Hindu editorial + Times of India

### 🇧🇩 Bangladesh
- BCS candidates
- Bangladesh Bank job aspirants
- PSC & Govt job candidates
- NTRCA candidates
- IELTS learners

**Content source:** The Daily Star editorial + Financial Express

---

## 3. Core Features

| Feature | Description |
|---|---|
| Editorial Feed | Daily Star, Financial Express, The Hindu, Times of India |
| Daily Vocabulary | 10 words/day with Bengali or Hindi meaning |
| Word of the Day | Single featured word with full definition, synonyms, antonyms, example |
| Daily Quiz | 10 MCQs, English-to-English format |
| XP & Gamification | +2 XP/word, +10 XP/quiz, +20 XP daily mission |
| Leaderboard | Global + country-wise, written to GitLab via API key |
| Premium | Ad-free, past editorials, full history, advanced analytics |
| Rewarded Ads | Non-premium unlock via AdMob rewarded video |

---

## 4. Tech Stack

### Android App
- Language: Kotlin / Jetpack Compose
- Database: Firestore + local cache
- Auth: Firebase Auth
- Notifications: FCM (Firebase Cloud Messaging)
- Ads: Google AdMob
- In-app purchases: Google Play Billing

### Backend / Data Pipeline
- Platform: GitLab (namespace: `mahadi07/rtejhs`)
- CI/CD: GitLab CI with pre-built Docker image
- Data storage: GitLab repo (`EdData/` folder) — Android app reads via GitLab API
- Language: Python 3.12
- Key libraries: BeautifulSoup4, Playwright, MoviePy, gTTS, PIL, firebase-admin

### Infrastructure
- GitLab Shared Runners (400 min/month free tier)
- GitLab Container Registry (pre-built Docker image)
- Firebase (FCM notifications)
- Cloudinary (video hosting for Instagram)
- Google Play (app distribution)

---

## 5. Pipeline Architecture

### GitLab CI Schedules (3 active)

| Schedule | Cron (Dhaka time) | Variables | What runs |
|---|---|---|---|
| Morning | 12:00 PM daily | `SCHEDULE_TYPE=morning` | Scrape → Vocab → WOTD → FB text post → FCM → Quiz |
| BD Reel | 7:00 PM Sunday | `SCHEDULE_TYPE=bd_reel` | BD Bengali 10-vocab reel → Facebook |
| Indian | 8:00 PM Thursday | `MARKETING_TYPE=indian` | WOTD reel → YouTube + Facebook + Instagram |

### Local Runner (Windows laptop — Task Scheduler)
Runs on: Mon, Thu, Fri, Sat, Sun (7 days but split between two tasks)

| Task | Script | Time | Type |
|---|---|---|---|
| BD Facebook Reel | `local_runner.py --pipeline bd_reel` | 8:00 PM | Bengali 10-vocab reel → FB only |
| Hindi Reel | `local_runner.py --pipeline hindi_reel` | 10:00 PM | Hindi 10-vocab reel → FB + YT + IG |

**Local credentials:** `E:\EditorialGitlabServer\rtejhs\local.env`
**Repo path:** `E:\EditorialGitlabServer\rtejhs`

### Pipeline Files
```
main.py                    Morning pipeline orchestrator (includes quiz)
quiz_pipeline_SEPARATE.py  Quiz generation (called from main.py)
scrapers.py                Article scraping (Daily Star, Hindu, TOI, FE)
vocabulary.py              Vocab extraction with anti-repetition
word_of_day.py             WOTD generation
facebook.py                Facebook text post
facebook_reel.py           BD + Hindi vocab reel generation + FB posting
reel_pipeline.py           BD/Hindi reel pipeline entry (DICTIONARY_TYPE=1/2)
hindi_reel_pipeline.py     Hindi reel multi-platform (FB+YT+IG)
indian_pipeline.py         Indian WOTD reel multi-platform
indian_reel.py             Indian reel video generator (Hinglish hook)
marketing_coordinator.py   Multi-platform publisher
comment_poster.py          First-comment app link poster
firebase_campaign.py       FCM push notifications
article_storage.py         Article JSON storage (partitioned + legacy)
local_runner.py            Windows popup GUI runner
```

### Data Folder Structure (EdData/)
```
EdData/data/
├── articles/bangladesh/YYYY/MM/DD-MM-YYYY.json
├── articles/india/YYYY/MM/DD-MM-YYYY.json
├── article/                    (legacy — Android app backward compat)
├── EnToBnWord/DD-MM-YYYY.json  (10 Bengali vocab words)
├── EnToHnWord/DD-MM-YYYY.json  (10 Hindi vocab words)
├── WordOfTheDayEnToBn/MM-YYYY.json
├── WordOfTheDayEnToHn/MM-YYYY.json
├── DayOfTheQuizEnToBn/DD-MM-YYYY.json
├── DayOfTheQuizEnToHn/DD-MM-YYYY.json
├── facebook_reels/             (BD + Hindi reel mp4 + captions)
├── indian_reels/               (WOTD reel mp4)
├── facebook_posts/             (text post captions)
└── article_index.json
```

---

## 6. Social Media Channels

### Current (all under one account: @editorialvocabapp)

| Platform | Handle | Followers | Content | Audience |
|---|---|---|---|---|
| Facebook Page | editorialvocabapp | 19,000 | Bengali + Hindi | Mixed (BD history, India recent) |
| YouTube | @editorialvocabapp | 559 | WOTD + Hindi 10-vocab Shorts | India (UPSC/SSC) |
| Instagram | @editorialvocabapp | 7 | Hindi 10-vocab Reels | India |

### ⚠️ Critical Issue: Content-Audience Mismatch
The FB page built 19K followers over 10 years with Bengali/BD content.
Posting Hindi content to them causes near-zero engagement (avg 5–6 views).
**This is the root cause of low engagement — not content quality.**

---

## 7. Content Types Published

| Pipeline | Content | Language | Platform | Audience |
|---|---|---|---|---|
| Morning (GitLab) | 10 vocab text post + image | English + Bengali | Facebook | BD |
| BD Reel (local/GitLab Sun) | 10-word reel (hook→words→CTA) | Bengali Unicode hook + English words | Facebook | BD |
| Hindi Reel (local daily) | 10-word reel (Hinglish hook→words→CTA) | Hinglish hook + English words | FB + YT + IG | India |
| Indian Marketing (local Thu) | WOTD reel (Hinglish narration) | English + Hinglish | FB + YT + IG | India |
| FCM Morning | Bengali push notification | Bengali | Android app | BD users |
| FCM Evening | Hindi push notification | Hindi | Android app | India users |

### Content Hooks (date-seeded, reproducible)
**Banglish (Bengali Unicode for gTTS lang="bn"):**
- Even dates: "স্ক্রল করো না"
- Odd dates: "স্ক্রল করো না — এই দশটা শব্দ এখন শেখো"
- + 9 more hooks in Bengali Unicode

**Hinglish (gTTS lang="en", tld="co.in"):**
- "Scroll mat karo. Yeh 10 words tumhe aaj kaam aayenge."
- "Ruko! 10 powerful words. In just one minute."
- + 8 more hooks

---

## 8. Credentials & Secrets

### GitLab CI Variables (set in GitLab → Settings → CI/CD)
```
PAT_TOKEN                  GitLab Personal Access Token
FIREBASE_SERVICE_ACCOUNT   Firebase service account JSON (string)
```

### credentials.env (local only — never commit)
```
FACEBOOK_ENABLED=true
FACEBOOK_PAGE_ID=
FACEBOOK_PAGE_TOKEN=        ← key name (not FACEBOOK_PAGE_ACCESS_TOKEN)
FACEBOOK_API_VERSION=v19.0

CLOUDINARY_CLOUD_NAME=djlqdhnwh
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=

INSTAGRAM_ACCOUNT_ID=       ← IG Business account ID
```

### local.env (local only — never commit)
```
GITLAB_PAT=
FACEBOOK_PAGE_ID=
FACEBOOK_PAGE_ACCESS_TOKEN=
CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=
INSTAGRAM_ACCOUNT_ID=
```

### OAuth Files (local only)
```
client_secrets.json           YouTube OAuth client secrets
client_secrets_token.json     YouTube OAuth token (auto-generated)
firebase-service-account.json Firebase admin SDK key
```

### ⚠️ YouTube Comment Fix Needed
YouTube comments fail with 403 insufficientPermissions because the token was
created without youtube.force-ssl scope. To fix:
1. Delete `client_secrets_token.json`
2. Run `local_runner.py --pipeline hindi_reel --force`
3. Authorize in browser when prompted
4. New token will include youtube.force-ssl scope

---

## 9. Docker / GitLab CI Image
```
Registry: registry.gitlab.com/mahadi07/rtejhs/editorial-ci:latest
Rebuild:  Push Dockerfile or requirements.txt to main branch
```

**Build_ci_image rule fix:** Uses `$CI_PIPELINE_SOURCE == "push"` to prevent
running on scheduled pipelines (GitLab bug: `changes:` always true on schedules).

### Monthly Minute Budget
| Pipeline | Min/run | Runs/month | Total |
|---|---|---|---|
| Morning (main+quiz) | ~10 min | 30 | 300 min |
| BD Reel (GitLab Sun) | ~10 min | 4 | 40 min |
| Indian Marketing (GitLab Thu) | ~12 min | 4 | 48 min |
| **Total** | | | **~388 min** ✅ |

---

## 10. Separate BD Channel — Decision Framework

### Option A: Keep Everything on One Page (@editorialvocabapp)
**Pros:**
- 19K followers = massive head start for BD reach
- No effort to build new audience from zero
- One place to manage
- BD reels posted here already reach your core existing audience

**Cons:**
- Hindi content confuses BD followers → kills engagement on both content types
- Facebook algorithm penalises mixed-audience pages (reduces reach for both)
- Can't properly target India audience with a page known as BD

**Verdict:** Works for BD content only. Permanently hurts Hindi content reach.

### Option B: Create Separate BD Page + Keep @editorialvocabapp for India
**Pros:**
- Clean audience targeting — Facebook knows your page = India audience
- Existing 19K BD followers migrate to new BD page (invite them)
- Hindi content finally reaches the right algorithm audience
- Each page's engagement signals are clean → better organic reach

**Cons:**
- New BD page starts at 0 — need to invite/migrate 19K followers (many won't move)
- Two pages to manage
- Takes 3–6 months for new page to gain algorithm trust

**Verdict:** Best long-term strategy. Painful transition but fixes the root problem.

### Option C: Two YouTube Channels (BD + India)
**Pros:**
- YouTube is keyword/topic-based not follower-based for discovery
- Bengali content + Bengali title/description → YouTube finds BD viewers
- Hindi content + Hindi title → YouTube finds India viewers
- Both can grow independently without hurting each other

**Cons:**
- Two channels to manage
- Current 559 subscribers stay on India channel — BD starts at 0
- Can schedule via separate Task Scheduler tasks (no extra code needed)

**Verdict:** Strongly recommended for YouTube. Low cost, high benefit.

### ✅ Recommended Action Plan (priority order)
1. **Immediately:** Create separate YouTube channel for BD Bengali content (Handle: @EditorialVocabAppBD)
2. **Month 2:** Create new FB page for BD (invite 19K followers via post)
3. **Month 3:** Move all BD content to new page, use @editorialvocabapp purely for India
4. **Keep:** One Instagram @editorialvocabapp for India (Instagram is India-heavy anyway)

---

## 11. Engagement Strategy (Getting Likes & Shares)

### Why Current Reels Get No Engagement
1. **Audience mismatch** (main cause — see Section 7)
2. **No call-to-action for engagement** — reels don't ask viewers to like/share
3. **No trending audio** — reels use custom TTS, algorithm doesn't boost them
4. **No community interaction** — not replying to comments, not commenting on others

### What To Do
1. Add verbal CTA in last 2 seconds: "Like karo agar helpful laga!" (Hindi) / "Helpful hole like deo!" (Bengali)
2. Post at peak times: India → 7–9 AM, 8–10 PM IST / BD → 8–10 PM BST
3. Reply to every comment within 1 hour — signals engagement to algorithm
4. Follow and comment on similar accounts (UPSC/BCS prep pages)
5. Use 3–5 specific hashtags not 20 generic ones

---

## 12. Monetization — Path to $50/Month

### Current: ~$14/month
- In-app purchases: ~$9/month
- AdMob: ~$5/month

### Realistic $50/Month Roadmap

| Source | Current | Target | How |
|---|---|---|---|
| AdMob | $5 | $20 | Increase DAU from 296 → 1,000 via push notifications + better onboarding |
| In-app purchase | $9 | $15 | Add ₹99 monthly subscription (cheap for India) |
| eBook sales | $0 | $10 | Monthly vocab eBook PDF (see Section 13) |
| YouTube AdSense | $0 | $5 | 1,000 subscribers needed for monetization |
| **Total** | **$14** | **$50** | |

### Quick Win: Push Notification Optimization
Your app has FCM but 296 DAU from 106K installs = 0.28% daily open rate.
Most users have notifications disabled or ignore them.
Fix: Send Bengali/Hindi hooks as notification text (not generic "New word available").
Example: "স্ক্রল করো না — আজকের ১০টা শব্দ দেখো 👆" instead of "New vocabulary available"

---

## 13. eBook Strategy

### Product
**Monthly Vocabulary eBook (auto-generated)**
- Format: PDF, 7–10 pages
- Content: All 30 Word of the Day entries from one month
- Two versions: Bengali (from WordOfTheDayEnToBn/) + Hindi (from WordOfTheDayEnToHn/)
- Auto-generated by Python from existing GitLab JSON data
- Price: ₹29 India / ৳99 Bangladesh

### Generation Pipeline (to build)
```python
# Reads: EdData/data/WordOfTheDayEnToBn/MM-YYYY.json
# Generates: Monthly_Vocabulary_Bengali_MM_YYYY.pdf
# Tool: existing PDF generation code + ReportLab/fpdf2
```

### Selling Channels
| Channel | India | Bangladesh |
|---|---|---|
| Direct | Razorpay payment link | bKash / Nagad QR |
| Gumroad | ✅ accepts international cards | ✅ |
| In-app | Google Play Books (future) | |
| Facebook | Pin post with payment link | Pin post |
| YouTube | Pinned comment + description | |

### Marketing the eBook
- Post 3 sample pages as carousel on Facebook/Instagram
- "This month's 30 words in one PDF — ₹29 only"
- Pin the post and update every month automatically

---

## 14. Web App Recommendation

**Should you build one?**

For now: **No.** Your 106K installs are Android users. A web app costs weeks of
development for unclear ROI. Better to:
1. Add a simple landing page (free on GitLab Pages or GitHub Pages)
2. Page should show: app features, download button, sample vocabulary
3. This improves Play Store conversion from search traffic

**Build order:** Landing page → iPhone app (after Mac) → Web app (only if needed)

**iPhone:** Wait until you have Mac. TestFlight + App Store costs $99/year.
Focus on growing Android revenue to $50/month first — that pays for the Apple developer account.

---

## 15. Known Issues & Fixes Applied

| Issue | Status | Fix |
|---|---|---|
| build_ci_image ran on every schedule | ✅ Fixed | Added `$CI_PIPELINE_SOURCE == "push"` rule |
| Quiz push failed (non-fast-forward) | ✅ Fixed | Moved quiz into main.py (single push) |
| Bengali boxes in reel (Windows) | ✅ Fixed | Playwright HTML renderer when RAQM=False |
| CTA screen ★ boxes | ✅ Fixed | PIL circles replace Unicode star |
| BD reel no FB credentials | ✅ Fixed | Reads FACEBOOK_PAGE_TOKEN (matches credentials.env) |
| Hindi reel 403 YouTube comment | ✅ Fixed (partial) | Silent skip; re-auth needed (delete token file) |
| Instagram comment not hyperlink | ✅ Fixed | "Link in bio 👆" + plain URL for copy-paste |
| YouTube comment not hyperlink | ✅ Fixed | URL on own blank line (auto-detected by YouTube) |
| Timing mismatch (word 4 → screen 6) | ✅ Fixed | Character-count proportional timing |
| git pull rebase on unstaged files | ✅ Fixed | Stash → pull → pop pattern |
| RUN_DAYS ran every day locally | ✅ Fixed | Changed `{0,1,2,3,4,5,6}` → `{0,3,4,5,6}` |
| Cloudinary wrong public_id | ✅ Fixed | `daily-vocab-hn-DD-MM-YYYY` date-based id |
