# Editorial Vocabulary App — Master Project Reference
> Last updated: 31 May 2026 | Owner: Mahadi | Location: Tangail, Dhaka, BD

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

**Current Stats (May 2026):**
- Total installs: ~106,000
- Active users (May 3–30, 28 days): 4,295 unique users
- Session starts: 13,345 (28 days)
- Daily active users: ~142–159 (AdMob DAU avg)
- New installs (May 3–30): 1,015 (first_open events)
- In-app purchase revenue: ~$9/month (13 purchases in period)
- AdMob revenue: ~$13/month (last 30 days, declining -1.7%)
- Installed audience: 6,520 (-2.1% vs previous 30 days)
- Total monthly revenue: ~$22/month
- Target monthly revenue: $50/month

---

## 2. Target Audiences

### India
- UPSC aspirants
- SSC (CGL, CHSL, MTS)
- Banking (IBPS PO, Clerk, SBI)
- Railway & Defence exams

**Content source:** The Hindu editorial + Times of India

### Bangladesh
- BCS candidates
- Bangladesh Bank job aspirants
- PSC & Govt job candidates
- NTRCA candidates
- IELTS learners

**Content source:** The Daily Star editorial + Financial Express

---

## 3. Core Features

| Feature | Description | Status |
|---|---|---|
| Editorial Feed | Daily Star, Financial Express, The Hindu, Times of India | ✅ Live |
| Daily Vocabulary | 10 words/day — 1 exam word (position 0) + 9 editorial words | ✅ Live |
| Word of the Day | Full definition, phonetic, synonyms, antonyms, example, source badge | ✅ Live |
| Daily Quiz | 10 MCQs — Q1 authentic PYQ, Q2-Q10 editorial shuffled | ✅ Live |
| Exam Source Badge | Gold chip "Previous Year Question" + "Also in BCS 39" dual badge | ✅ Live |
| XP & Gamification | Daily missions: WOTD+5, Quiz+10, Vocab+10, Bonus+5 = 30 XP max | ✅ Live |
| Leaderboard | Global + country-wise, Firestore-backed | ✅ Live |
| Premium | Ad-free, full history, analytics, offline | ✅ Live |
| Rewarded Ads | Non-premium WOTD month unlock | ✅ Live (broken show rate) |
| eBook Promo | Exit dialog + FCM 9PM campaign | ✅ Live |
| Community Section | Social + eBook store, remote-configured via GitLab JSON | ✅ Live |
| **Streak System** | StreakManager — consecutive days, shield (day 7/14/30), Firestore sync | ✅ Phase 1 |
| **StreakBar + Countdown** | HomeScreen amber/green flame bar + exam countdown banner | ✅ Phase 2 |
| **Firestore Streak Sync** | syncStreak() on every activity — fixed disconnected analytics prefs | ✅ Phase 2 |
| **Onboarding Screen** | 6-step: region → exam → date → notification time → done | ✅ Phase 3 |
| **WorkManager Reminder** | DailyReminderWorker — streak-aware copy, 8PM default | ✅ Phase 3 |
| **ExamGoalPreferences** | Exam name + target date + notification time stored locally | ✅ Phase 3 |
| **Room Database** | AppDatabase — SavedWordEntity + SpacedReviewEntity | ✅ Phase 4 |
| **Spaced Repetition** | SM-2 algorithm — Easy/Good/Hard grades, interval scheduling | ✅ Phase 4 |
| **Saved Words Screen** | List + filter tabs (All/Exam/Due) + card-flip review quiz | ✅ Phase 4 |
| **SpacedReviewWorker** | 10AM daily — fires notification when words are due | ✅ Phase 4 |
| **Weekly Report** | WeeklyReportComputer — 7-day stats, XP delta, streak growth | ✅ Phase 5 |
| **Sunday Notification** | WeeklyReportWorker — Sunday 7PM performance summary push | ✅ Phase 5 |
| **RetentionEventTracker** | Firebase Analytics — Day-1/3/7/30 funnel + 8 feature events | ✅ Phase 5 |
| **MissionMissedDialog v2** | Gamified exit dialog — progress ring, XP cost, streak warning | ✅ Phase 5 |
| **StreakCarousel** | Replaces StreakBar + ExamCountdownBanner — 2-slide auto-carousel, 4s advance, swipe, pill dots | ✅ Shipped |
| **EditorialTeaserCard** | Real headline from local DB surfaced above Daily Mission — drives article ad revenue | ✅ Shipped |
| **Analytics ad preload** | Interstitial loaded in HomeScreen before navigation — fixes 2.3% show rate | ✅ Shipped |
| **Rewarded ad retry** | 10s exponential backoff (max 3), loading toast, no premature Premium dialog | ✅ Shipped |
| **Bookmark + SaveWord wire** | Bookmark icon on WOTD/Quiz → SavedWordRepository.saveWord() | ✅ Live |
| Feature | Description | Status |
|---|---|---|
| **Web WOTD Pages** | Auto-generated `/docs/words/DD-MM-YYYY/bn/` and `/hn/` — full meta, schema.org, definition, synonyms, vocab list, day nav | ✅ Shipped |
| **Web Quiz Pages** | Auto-generated `/docs/quiz/DD-MM-YYYY/bn/` and `/hn/` — 10 MCQ, answers in `<details>`, schema.org/Quiz, Q1 PYQ badge | ✅ Shipped |
| **BCS Archive Page** | `/docs/bcs-vocabulary/` — incremental log of all BCS/PSC tagged words, regenerated daily | ✅ Shipped |
| **UPSC Archive Page** | `/docs/upsc-vocabulary/` — incremental log of all UPSC/SSC tagged words, regenerated daily | ✅ Shipped |
| **Words Index** | `/docs/words/index.html` — JS redirect: BD → BCS archive, India → UPSC archive. Noscript fallback. | ✅ Shipped |

---

## 4. Firebase Analytics — May 3–30 2026 (28-day window)

> First measurement period since RetentionEventTracker deployed (Phase 5).
> Data source: Firebase Console → Events export.

### Retention funnel

| Milestone | Events | Unique users | Rate vs installs | Verdict |
|---|---|---|---|---|
| `first_open` (installs) | 1,015 | 1,015 | baseline | — |
| `day_1_retained` | 1,624 | 1,624 | **160%** ⚠️ | Inflated — old users triggered on first app open after tracker deployed. Not a real D1 rate. |
| `day_3_retained` | 714 | 713 | **70.3%** | Realistic. Strong D3 among users who kept the app. |
| `day_7_retained` | 0 | 0 | **0%** | Tracker deployed 3 weeks ago — 7-day cohort not yet complete. Check again 7 June 2026. |

**Day-1 inflation explained:** `RetentionEventTracker.checkAndFireRetentionMilestone()` fires on every `onCreate()`. When the update shipped, existing users who were already past Day 1 triggered the `day_1_retained` event on their next open — inflating the count above 100%. This resolves itself after the first full cohort cycle (28 days). The D3 rate (70.3%) is the first reliable datapoint.

**Next check date: 7 June 2026** — first clean D7 cohort will be visible.
**Target D7 rate: ≥ 15%** — if below 10%, streak urgency copy needs strengthening.

---

### Notification metrics (May 3–30)

| Metric | Value | Benchmark | Verdict |
|---|---|---|---|
| Notifications received | 155,971 | — | FCM pipeline working well |
| Notifications opened | 509 | — | — |
| **Open rate** | **0.33%** | Industry avg 3–5% | 🚨 Critical — 10× below benchmark |
| Dismiss rate | 43.4% | <30% healthy | 🔴 Users actively swiping away |
| Foreground receives | 110 | — | Small — most arrive when app is closed |

**Root cause of 0.33% open rate:** The FCM pipeline sends 155K notifications/month but only 509 are opened. The copy is generic ("New quiz available") and not personalised. The DailyReminderWorker (Phase 3) now sends streak-aware personalised copy — but it only fires for users who completed onboarding. With 342 onboarding completions so far, the reach of personalised notifications is still small. As the onboarding funnel grows this metric will improve.

**Immediate fix needed:** Review FCM payload copy in `firebase_campaign.py`. Current subject line for BCS/UPSC push notifications is likely not mentioning the streak count or exam days. Add `streak_count` and `days_to_exam` to FCM data payload so Android can render personalised notification titles even for FCM-originated pushes.

---

### Engagement metrics (May 3–30)

| Event | Count | Users | Per-user avg | Note |
|---|---|---|---|---|
| `app_open_retention` | 26,137 | 2,279 | 11.5× | Strong repeat opens — core users are habitual |
| `session_start` | 13,345 | 3,829 | 3.5× | — |
| `user_engagement` | 27,010 | 3,462 | 7.8× | Time-in-app tracking |
| `onboarding_completed` | 342 | 338 | 1.0× | 33.7% of new installs complete onboarding |
| `wotd_viewed` | 320 | 144 | 2.2× | Very low — only 14% of active users view WOTD |
| `weekly_report_generated` | 98 | 56 | 1.75× | 56 users saw the Sunday report notification |
| `app_remove` | 973 | 932 | 1.0× | 91.8% uninstall rate vs installs — high churn |

**Critical finding — onboarding conversion: 33.7%**
Only 342 of 1,015 new installs reach the "Start Learning" button. 66% of new users abandon the 6-step onboarding before completing it. This is the highest-leverage fix available right now — every abandoned onboarding is a user who will never get a personalised notification.

**WOTD viewed: only 144 users**
The Word of the Day screen is the single highest-eCPM ad unit ($1.63) but only 144 unique users opened it in 28 days. This needs a dedicated FCM campaign separate from the quiz campaign.

---

### Ad metrics (May 3–30)

| Metric | Value | Note |
|---|---|---|
| Ad impressions | 3,751 | From `ad_impression` event |
| Ad clicks | 85 | 2.27% CTR |
| **Rewarded ad completions** | **108** | `ad_reward` events — up from near-zero before retry fix |
| In-app purchases | 13 | $13.50 revenue |

**Rewarded ad improvement:** 108 `ad_reward` events vs an estimated near-zero before the retry overhaul. The fix is working. Full impact visible after next 30-day cycle.

**Total 6-month AdMob revenue: $29.39**

| Ad Unit | Revenue | eCPM | Impressions | Show Rate | CTR | Priority |
|---|---|---|---|---|---|---|
| article_reading_activity | $24.77 | $1.48 | 16,753 | 24.5% | 2.63% | 🔴 Protect at all costs |
| word_with_meaning_activity | $1.62 | $1.32 | 1,229 | 22.0% | 2.36% | 🟡 Healthy |
| WORD_OF_DAY interstitial | $0.74 | $1.63 | 453 | 14.0% | 3.31% | 🟡 Grow WOTD DAU |
| default_many_activity | $0.70 | $1.48 | 473 | 10.4% | 2.33% | 🟠 Low show rate |
| exam_activity | $0.61 | $1.02 | 601 | 24.4% | 3.00% | 🟡 Healthy |
| QUIZ_OF_THE_DAY | $0.28 | $1.17 | 237 | 13.8% | **6.33%** | 🔴 Highest CTR, scale up |
| translation_practice | $0.24 | **$1.76** | 139 | 15.0% | 3.60% | 🟠 Best eCPM, few users |
| **Rewarded_WOTD_unlock** | $0.22 | **$5.25** | **42** | **4.1%** | 2.38% | 🚨 EMERGENCY — 96% fail rate |
| analytics_leaderboard | $0.21 | $1.36 | 152 | **2.3%** | 2.63% | 🚨 EMERGENCY — ad not loading |

### Critical findings

**1. Article reading = 84% of all revenue ($24.77/$29.39)**
Every engineering decision must protect this ad unit. Never remove or reduce article reading friction.

**2. Rewarded ad eCPM = $5.25 — 3.5× higher than any interstitial**
1,020 ad requests in 6 months but only 42 impressions = **96% of users who try to unlock fail**.
Fix this one unit alone could add $5–8/month. This is the #1 revenue emergency.

**3. Quiz ad has 6.33% CTR — highest of all units**
Only 237 impressions because quiz DAU is very low. Every new daily quiz user = more ad revenue. Phases 1–5 retention improvements directly grow this.

**4. Analytics/Leaderboard show rate = 2.29%**
6,747 requests, only 152 impressions. The ad is not loading or the screen is closing too fast. Debug ad lifecycle in AnalyticsScreen/LeaderboardScreen.

**5. WOTD interstitial eCPM = $1.63 — highest among interstitials**
Low impressions because WOTD DAU is low. Growing daily WOTD completion (now tracked as a streak activity) will grow this.

---

## 5. Retention System (Phases 1–5) — Implementation Summary

### Phase 1 — Streak System ✅
**Files:** `StreakManager.kt`, `NotificationHelper.kt`, `DailyReminderWorker.kt`, `ExamGoalPreferences.kt`

- `StreakManager` — singleton, SM-2-style consecutive day detection
- Shield earned at day 7, 14, 21, 30 (max 2 shields held)
- `StreakStatus` enum: `NEVER_STARTED / ACTIVE_TODAY / AT_RISK / SHIELD_PROTECTING / BROKEN`
- `recordActivityToday()` called from `XpPreferences.markWordOfDayComplete()`, `markQuizCompleted()`, `markVocabQuizComplete()`
- `toFirestoreMap()` returns `{streak, longestStreak, lastActive}` for sync
- `WorkScheduler.scheduleDailyReminder()` — `ExistingPeriodicWorkPolicy.UPDATE`, fires at user's chosen hour
- Streak-aware notification copy: AT_RISK → urgent amber, BROKEN → motivational, ACTIVE → standard

### Phase 2 — Firestore Sync + HomeScreen UI ✅
**Files:** `StreakBannerComponents.kt`, `HomeScreen_PATCH`, `LeaderboardRepository_PATCH`

- `StreakBar` composable — pulse animation on AT_RISK, shield pill count, exam countdown right-aligned
- `ExamCountdownBanner` — appears only when daysToExam ≤ 30, urgency color escalates (blue→amber→orange→red)
- `ShieldEarnedDialog` — triggered by `StreakUpdateResult.shieldEarned == true`
- `LeaderboardRepository.syncStreak()` — lightweight Firestore merge write, separate from rate-limited `submitScore()`
- **Bug fixed:** Leaderboard `streak` field was reading from disconnected analytics SharedPreferences — now reads from `StreakManager`

### Phase 3 — Onboarding ✅
**Files:** `OnboardingScreen.kt`, `MainActivity_EXACT_PATCH`

- 6 steps: Welcome → Region → Exam Goal → Exam Date (DatePickerDialog) → Notification Time → Done
- Region selection sets `dictionaryType` (1=Hindi, 2=Bengali) via `Preferences.setOfflineDictionary()`
- Exam list is region-filtered (`EXAMS_BD` vs `EXAMS_IN` from `ExamGoalPreferences`)
- Notification time: 4 presets (Morning/Afternoon/Evening/Night) → calls `WorkScheduler.scheduleDailyReminder()`
- `completeOnboarding()` persists all choices atomically
- **Existing user migration:** if `valueForOfflineDictionary > 0 && !isOnboardingDone` → mark done, skip flow

### Phase 4 — Spaced Repetition ✅
**Files:** `AppDatabase.kt`, `SpacedRepetitionEngine.kt`, `SpacedReviewWorker.kt`, `SavedWordsViewModel.kt`, `SavedWordsScreen.kt`

- Room DB: `saved_words` table + `spaced_reviews` table, singleton `AppDatabase`
- SM-2 algorithm: grades EASY(q=5)/GOOD(q=3)/HARD(q=1), EF starts 2.5 min 1.3, intervals 1→6→EF×prev
- `SavedWordRepository.saveWord()` — saves word AND schedules for review immediately
- `SavedWordsScreen` — filter tabs (All/Exam/Due), blue banner for due count, card-flip review, session results
- `SpacedReviewWorker` — 10AM daily, fires notification only when dueCount > 0
- Bookmark integration: call `repository.saveWord(word, meaning, source, lang)` from WOTD and Quiz screens
- **Dependencies added to build.gradle:** Room 2.6.1 + KSP 1.9.22-1.0.17

### Phase 5 — Weekly Analytics Report ✅
**Files:** `WeeklyReportComputer.kt`, `WeeklyReportWorker.kt`, `RetentionEventTracker.kt`, `AnalyticsScreen_Phase5_PATCH`

- `WeeklyReportComputer.compute()` — reads analytics prefs + StreakManager, builds `WeeklyReport` data class
- `WeeklyReport` fields: daysStudied, avgAccuracy, quizzesCompleted, currentStreak, xpEarnedThisWeek, examName, daysToExam, motivationLine, notificationBody
- `WeeklyReportWorker` — Sunday 7PM, computes report, shows BigText notification, saves snapshots for next-week delta
- `RetentionEventTracker` — Day-1/3/7/30 milestones (each fires exactly once), plus: `trackQuizCompleted`, `trackWotdViewed`, `trackStreakMilestone`, `trackWeeklyReport`, `trackOnboardingCompleted`, `trackSavedWord`, `trackReviewSession`
- **Bug fixed:** `calculateCurrentStreak()` in AnalyticsScreen was reading from disconnected analytics SharedPreferences — now reads from `StreakManager`
- `WeeklyReportCard` composable added to AnalyticsScreen LazyColumn (above HeroStatsSection)
- `MissionMissedDialog v2` — progress ring header, XP cost displayed, streak-aware warning, button hierarchy redesigned

### Workers registered in Application.onCreate()
```kotlin
NotificationHelper.createChannels(this)
if (examGoalPrefs.isOnboardingDone) {
    WorkScheduler.scheduleDailyReminder(this, examGoalPrefs.notifHour, examGoalPrefs.notifMinute)
}
scheduleSpacedReviewWorker(this)   // 10AM daily — spaced review check
scheduleWeeklyReportWorker(this)   // Sunday 7PM — weekly summary
RetentionEventTracker.checkAndFireRetentionMilestone(this)  // Day-1/3/7/30
```

---

## 6. Tech Stack

### Android App
- Language: Kotlin / Jetpack Compose
- Database: Room (AppDatabase — saved words + spaced reviews) + Firestore + DataStore (per-feature cache)
- Auth: Firebase Auth (Google Sign-In + anonymous upgrade)
- Notifications: FCM + WorkManager (3 workers: DailyReminder, SpacedReview, WeeklyReport)
- Ads: Google AdMob
- In-app purchases: Google Play Billing
- Image loading: Coil (AsyncImage)
- Analytics: Firebase Analytics (RetentionEventTracker)
- Dependency injection: Manual (Singleton pattern)

### Backend / Data Pipeline
- Platform: GitLab (namespace: `mahadi07/rtejhs`)
- CI/CD: GitLab CI with pre-built Docker image
- Data storage: GitLab repo (EdData/ folder) — Android reads via GitLab Files API
- Language: Python 3.12
- Key libraries: BeautifulSoup4, Playwright, MoviePy, gTTS, PIL, firebase-admin, google-auth, requests, pytz, google-genai

### Infrastructure
- GitLab Shared Runners (400 min/month free tier)
- Firebase (FCM + Crashlytics + Analytics + Firestore)
- Cloudinary (video hosting for Instagram)
- Google Play (app distribution)

---

## 7. Pipeline Architecture

### GitLab CI Schedules (5 active)

| Schedule | Cron UTC | Dhaka Time | Variable | What runs |
|---|---|---|---|---|
| Morning | 0 6 * * * | 12:00 PM daily | SCHEDULE_TYPE=morning | Scrape + Vocab + WOTD + FB post + WOTD FCM + Quiz |
| Quiz FCM | 0 7 * * * | 1:00 PM daily | SCHEDULE_TYPE=quiz_fcm | PYQ quiz push to word_bn + word_hn |
| eBook FCM | 0 15 * * * | 9:00 PM daily | SCHEDULE_TYPE=ebook_fcm | eBook selling push |
| BD Reel | 0 13 * * 0 | 7:00 PM Sunday | SCHEDULE_TYPE=bd_reel | BD Bengali 10-vocab reel to Facebook |
| Indian Mktg | 0 14 * * 4 | 8:00 PM Thursday | MARKETING_TYPE=indian | WOTD reel to YouTube + Facebook + Instagram |

### Monthly Minute Budget

| Pipeline | Min/run | Runs/month | Total |
|---|---|---|---|
| Morning (main+quiz) | ~10 min | 30 | 300 min |
| Quiz FCM | ~2 min | 30 | 60 min |
| eBook FCM | ~2 min | 30 | 60 min |
| BD Reel (Sun) | ~10 min | 4 | 40 min |
| Indian Marketing (Thu) | ~12 min | 4 | 48 min |
| **Total** | | | **~508 min — monitor** |

Free tier is 400 min. If over: reduce Quiz/eBook FCM to every other day (`0 7 */2 * *`).

### Backend Pipeline Files

```
main.py                        Morning pipeline orchestrator (v2: exam-word dedup, exam fallback)
quiz_pipeline_SEPARATE.py      Quiz: 1 exam + (3 syn + 3 ant + 3 def), Q2-Q10 shuffled daily
vocabulary.py                  Vocab extraction: enriched master + anti-repetition + exam fallback
word_of_day.py                 WOTD: 4-tier source detection (exact/stem/synonym match)
exam_source_intelligence.py    Shared exam-source matching engine (all 3 pipelines use this)
exam_loader.py                 Exam master utility (central hub)
enrich_master_words.py         Pass 1: free Dictionary API enrichment
enrich_pass2_gemini.py         Pass 2: Gemini fills missing syn/ant, fixes multi-word defs
firebase_campaign.py           3 FCM campaigns: WOTD, Quiz, eBook
fcm_pipeline.py                Standalone FCM entry
facebook.py                    Facebook text post
facebook_reel.py               BD + Hindi vocab reel generation + FB posting
reel_pipeline.py               BD/Hindi reel pipeline entry
hindi_reel_pipeline.py         Hindi reel multi-platform
indian_pipeline.py             Indian WOTD reel multi-platform
indian_reel.py                 Indian reel video generator (Hinglish hook)
marketing_coordinator.py       Multi-platform publisher
comment_poster.py              First-comment app link poster
article_storage.py             Article JSON storage (partitioned + legacy + seen_links dedup)
local_runner.py                Windows Tkinter GUI runner (7 pipeline cards)
```

---

## 8. Data Folder Structure (EdData/)

```
EdData/data/
  articles/bangladesh/YYYY/MM/DD-MM-YYYY.json
  articles/india/YYYY/MM/DD-MM-YYYY.json
  article/                              (legacy — kept for 2026 backward compat)
  seen_links.json                       NEW: persistent URL dedup registry
  EnToBnWord/DD-MM-YYYY.json           10 words: [0]=exam word, [1-9]=editorial
  EnToHnWord/DD-MM-YYYY.json           10 words: [0]=exam word, [1-9]=editorial
  WordOfTheDayEnToBn/MM-YYYY.json      Monthly list, newest at index 0
  WordOfTheDayEnToHn/MM-YYYY.json      Monthly list, newest at index 0
  DayOfTheQuizEnToBn/DD-MM-YYYY.json   Q1=exam PYQ, Q2-Q10=editorial (shuffled)
  DayOfTheQuizEnToHn/DD-MM-YYYY.json   Q1=exam PYQ, Q2-Q10=editorial (shuffled)
  ExamWordUsed/bn_used.json            Anti-repeat tracker {word: "DD-MM-YYYY"}
  ExamWordUsed/hn_used.json            Anti-repeat tracker
  master_words_enriched_bn.json        Enriched BN list (11,619 entries)
  master_words_enriched_hn.json        Enriched HN list (1,092 entries)
  community_links.json                 Social + eBook links per region
  facebook_reels/
  indian_reels/
  facebook_posts/
  article_index.json
```

---

## 9. Vocabulary & Quiz JSON Formats

### Vocabulary (EnToBnWord/, EnToHnWord/)
```json
{
  "wordMeaning": [
    "Mitigate : লাঘব করা",    <- position 0: EXAM WORD
    "Accelerate : গতি বাড়ানো", <- positions 1-9: EDITORIAL WORDS
  ]
}
```

### Quiz (DayOfTheQuizEnToBn/, DayOfTheQuizEnToHn/)
```json
{
  "questions": [
    { "id": 1, "source": "BCS 37" },           <- pure exam PYQ (Q1 only)
    { "id": 2, "source": "editorial" },         <- pure editorial
    { "id": 3, "source": "editorial+BCS 39" }   <- editorial word also in exam_master
  ]
}
```

### Source Badge Values
| Value | Badge shown |
|---|---|
| `"BCS 37"` / `"UPSC 2025"` | Gold "Previous Year Question" |
| `"editorial"` | No badge |
| `"editorial+BCS 39"` | Gold "Also in BCS 39" |

### WOTD (WordOfTheDayEnToBn/MM-YYYY.json)
**Critical:** `date` field = `"dd MMMM yyyy"` e.g. `"09 May 2026"`. Android `getTodaySource()` must use `SimpleDateFormat("dd MMMM yyyy")`.

---

## 10. Master Word Lists

| File | Words | Synonyms | Antonyms |
|---|---|---|---|
| `master_words.json` (BN flat) | 11,619 | 0% | 0% |
| `master_words_hn.json` (HN flat) | 1,092 | 0% | 0% |
| `master_words_enriched_bn.json` | 11,619 | ~43% | ~19% |
| `master_words_enriched_hn.json` | 1,092 | ~44% | ~22% |

HN antonym coverage at 22% is too low — run Gemini pass 2 to improve HN quiz antonym questions.

---

## 11. Exam Source Intelligence (exam_source_intelligence.py)

4-tier matching engine used by all 3 pipelines (vocab, quiz, WOTD):

| Tier | Example | Confidence | Min stem length |
|---|---|---|---|
| Exact | `"strategic"` == `"strategic"` | Highest | — |
| Stem | `"strategic"` ~ `"strategy"` (stem: `"strateg"`) | High | 5 chars |
| Synonym | editorial word appears in exam entry's synonyms list | Medium | — |
| Antonym | editorial word appears in exam entry's antonyms list | Lowest (opt-in only) | — |

Default `min_confidence = "synonym"` for WOTD and quiz. Antonym tier not used (too loose for source badges).

`score_exam_word_value()` — ranks exam entries for fallback selection: authentic PYQ question (+30), synonym count (+5 each, max 20), antonym count (+5 each, max 15), example (+10), definition (+10), is_authentic (+15), word length (+4–8).

---

## 12. Android Room Database (Phase 4)

### Tables
```kotlin
saved_words     — SavedWordEntity(word PK, meaning, definition, phonetic,
                  partOfSpeech, synonyms, antonyms, example, source, lang, savedAt)
spaced_reviews  — SpacedReviewEntity(word PK, interval, repetition, easiness,
                  nextReviewMs, totalReviews, correctReviews, lastReviewedMs)
```

### SM-2 Grade Mapping
| Grade | Quality | Next interval |
|---|---|---|
| EASY | 5 | prev_interval × EF (min 1 day) |
| GOOD | 3 | prev_interval × EF |
| HARD | 1 | Reset to 1 day |

EF (easiness factor) starts 2.5, min 1.3. Formula: `EF += 0.1 - (5-q) × (0.08 + (5-q) × 0.02)`

---

## 13. Notification Strategy

| Worker | Schedule | Channel | Content |
|---|---|---|---|
| DailyReminderWorker | User-chosen time (default 8PM) | CHANNEL_DAILY | Streak-aware copy: AT_RISK=urgent, BROKEN=motivational, ACTIVE=standard |
| SpacedReviewWorker | 10AM daily | CHANNEL_REVIEW | "X words due for review" — fires only when dueCount > 0 |
| WeeklyReportWorker | Sunday 7PM | CHANNEL_WEEKLY | Performance summary with BigText expanded view |
| FCM WOTD | 12PM (GitLab CI) | FCM | Today's word of the day |
| FCM Quiz PYQ | 1PM (GitLab CI) | FCM | Quiz push with A/B/C/D in notification |
| FCM eBook | 9PM (GitLab CI) | FCM | eBook promo image |

---

## 14. Monetization — Path to $50/Month

**Current (May 2026):** ~$22/month (AdMob ~$13 + IAP ~$9)

| Source | Current | Target | Lever |
|---|---|---|---|
| AdMob — article reading | $4.95/mo avg | $10 | Grow article DAU via retention phases |
| AdMob — rewarded ad | $0.04/mo avg | $5 | Fix 96% show failure rate — emergency |
| AdMob — quiz ad | $0.06/mo avg | $3 | Grow quiz DAU via streak + spaced review |
| In-app purchase | $9 | $15 | Add monthly subscription tier |
| eBook sales | $0 | $10 | FCM eBook 9PM campaign |
| YouTube AdSense | $0 | $5 | Need 1,000 subscribers |
| **Total** | **$22** | **$50** | |

---

## 15. Social Media Channels

| Platform | BD Handle | IN Handle | Content |
|---|---|---|---|
| Facebook | editorialvocabappbd | editorialvocabapp | Bengali + Hindi |
| YouTube | @editorialvocabappbd | @editorialvocabapp | WOTD + vocab Shorts |
| Instagram | @editorialvocabappbd | @editorialvocabapp | Hindi Reels |

Critical issue: FB page built 19K followers on BD content. Hindi content gets 5–6 views. Separation is the only permanent fix.

---

## 16. Bug Fixes & Engineering — This Session (May–June 2026)

### Article Ordering Fix
**Files:** `ArticleListScreen.kt`, `EditorialNewsSection.kt`

**Problem:** Articles showed in wrong order — fallback source (Financial Express / Times of India) appeared before primary source (Daily Star / The Hindu) for all dates. `EditorialNewsSection` showed last two articles instead of top two.

**Root cause:**
- `ArticleUtils.getSortedArticles()` used source weight as secondary sort. Within same weight group, stable sort preserved SQLite rowid order = insertion order = last JSON article first.
- `serverOrderMap` keyed by `headline1` — silent lookup failures due to whitespace/encoding differences meant all articles got `Int.MAX_VALUE` → rowid order again.
- `EditorialNewsSection` cached path had no `serverOrderMap` at all → always showed DB rowid order = reversed.

**Fix applied:**
- New `applyArticleSort()` in `ArticleListScreen.kt` — 3-key sort: date desc → source weight desc → serverOrderMap asc.
- `serverOrderMap` key changed from `headline1` to `link` (URL) — exact match, no encoding variation.
- Source weight is key 2 (before serverOrderMap) — guarantees Daily Star / Hindu always above FE / TOI regardless of JSON, DB, or scraper order.
- `EditorialNewsSection` cached path removed entirely — always fetches network so `serverOrderMap` is always available. SQLite rowid order cannot corrupt the result.
- `applyArticleSort()` declared `internal` — shared between both files, single definition.

---

### Article Deduplication Fix
**File:** `article_storage.py`

**Problem:** Same article appeared in multiple date JSON files (cross-date duplicates). Two scrapers in the same run could return the same article (same-run duplicates).

**Fix applied:**
- New persistent registry: `EdData/data/seen_links.json` — set of all previously saved article URLs.
- `filter_new_articles()` — two-pass dedup: cross-date (against registry) + same-run (against batch_seen set). Keyed by URL.
- `save_seen_links()` called AFTER successful disk write — crash during write leaves URLs unregistered so they retry next run. No silent data loss.
- Legacy format (`EdData/data/article/`) kept active through 2026 for backward app compatibility. Receives full unfiltered batch so old app versions stay complete.

---

### AdMob Revenue Engineering (Article Reading Screen)
**Files:** `AdConstants.kt`, `AdDailyCounter.kt`, `NativeAdCard.kt`, `ArticleBannerAd.kt`, `SavedWordBannerAd.kt`, `RewardedAdPromptDialog.kt`, `ArticleReadingScreen.kt`, `ArticleReadingViewModel.kt`

Six revenue placements implemented in priority order:

| Priority | Placement | Type | Status |
|---|---|---|---|
| P1 | Inter-paragraph native ads | Native | ✅ Fixed — position algorithm |
| P2 | Sticky bottom banner | Banner | ✅ Live |
| P3 | Vocabulary generation gate | Rewarded | ✅ Live |
| P4 | Back-navigation interstitial | Interstitial | ✅ Live |
| P5 | Translation quota gate | Rewarded | ✅ Fixed — bypass bug |
| P6 | Full-article TTS gate | Rewarded | ✅ Fixed — silent audio bug |

**P1 bug fixed:** Old `% N` formula produced 1 ad on short articles (4 blocks). New algorithm: `spacing = totalBlocks / (MAX_NATIVE_ADS + 1)`, positions computed as `{spacing×1-1, spacing×2-1, spacing×3-1}`. Always exactly 3 ads regardless of article length.

**P5 bug fixed:** `ArticleParagraphCard` called `viewModel.translateSentence()` directly — bypassing quota check entirely. Fix: card now receives `onTranslateClick: (Int, Int) -> Unit` lambda. Lambda calls `viewModel.requestTranslateSentence()` which enforces quota. Two new ViewModel methods: `requestTranslateSentence()` for paragraph path, unified `translateAfterReward()` handles both headline and sentence resumption.

**P6 bug fixed:** `toggleSpeech()` was called inside `onUserEarnedReward` while rewarded ad was still fullscreen. Android's audio focus manager silently rejects `speak()` when app is not in foreground. Fix: split into `markTtsRewardEarned()` (sets flag only, called from `onUserEarnedReward`) and `startSpeechAfterAdDismissed()` (calls `toggleSpeech()` after ad fully dismissed).

---

### WordOfTheDayModels — Gson Null Safety Fix
**File:** `WordOfTheDayModels.kt`

**Problem:** Fatal crash `NullPointerException` at `Word.<init>` parameter `audioUrl`. Gson uses Java reflection to set fields, bypassing Kotlin's null safety. Fields declared `String = ""` in `WordOfTheDay` received `null` from Gson when absent in JSON. `toWord()` passed null to `Word()` which enforces non-null → NPE.

**Fix:** All Gson-deserialized fields in `WordOfTheDay` changed from `String = ""` to `String? = null`. `toWord()` uses `?: ""` / `?: emptyList()` on every field. `word` and `date` kept non-null (meaningless without them).

**Also fixed in `StylishWordCard.kt`:** All 14 field accesses updated to use `isNullOrEmpty()`, `isNullOrBlank()`, and `.orEmpty()` matching the new nullable types. `word.source!!` replaced with `word.source.orEmpty()`.

---

### FCM Notification Back-Stack Fix
**Files:** `FcmNotificationDetailActivity.kt`, `AndroidManifest.xml`, `MyFirebaseMessagingService.kt`

**Problem:** After tapping WOTD notification and pressing HOME (not back), reopening the app showed `FcmNotificationDetailActivity` again instead of `MainActivity`.

**Root cause:**
- No `taskAffinity` on `FcmNotificationDetailActivity` → same affinity as `MainActivity` → `FLAG_ACTIVITY_NEW_TASK` reused the app's main task, pushing `FcmNotificationDetailActivity` on top: `[MainActivity, FcmNotificationDetailActivity]`. HOME → reopen → top of task = notification screen.
- `exitActivity()` started `MainActivity` without task flags → landed in notification's isolated task, not app's main task.

**Fix — three changes:**

1. `AndroidManifest.xml`: Added `android:taskAffinity=""` + `android:excludeFromRecents="true"` + `android:launchMode="singleTop"` to `FcmNotificationDetailActivity`. Now always gets its own isolated task.

2. `exitActivity()` in `FcmNotificationDetailActivity`:
```kotlin
// Before (broken — no flags)
if (isTaskRoot) { startActivity(Intent(this, MainActivity::class.java)) }
finish()

// After (fixed)
val intent = Intent(this, MainActivity::class.java).apply {
    flags = Intent.FLAG_ACTIVITY_CLEAR_TOP or Intent.FLAG_ACTIVITY_SINGLE_TOP
}
startActivity(intent)
finish()
```

3. `showNotification()` in `MyFirebaseMessagingService`: WOTD intent now uses `FLAG_ACTIVITY_NEW_TASK or FLAG_ACTIVITY_CLEAR_TASK` (not `FLAG_ACTIVITY_CLEAR_TOP`). ebook/quiz types keep `FLAG_ACTIVITY_CLEAR_TOP`.

---

### Saved Words & Onboarding Polish (June 2026)
**Files:** `SavedWordsScreen.kt`, `OnboardingScreen.kt`, `HomeScreen.kt`

**Problem:** Saved Words feature was hard to discover, had readability issues in dark mode, and review screens were cut off on small devices. Onboarding buttons were too close to the bottom edge.

**Fixes applied:**
- **HomeScreen discovery:** Added a high-visibility `HomeDueReviewBanner` that appears at the top of the screen only when words are due for review. Moved "Saved Words" to be the primary action (first button) in the Vocabulary section.
- **SavedWordsScreen accessibility:** Integrated `DailyEditorialTheme` colors (`getExamTextPrimary`, `getExamBackgroundColor`, etc.) across the entire screen for perfect dark/light mode alignment.
- **Small device support:** Wrapped `ReviewCard` and `SessionCompleteScreen` in scrollable columns. Removed fixed weights to allow natural height on short screens.
- **Navigation:** Implemented `BackHandler` in `SavedWordsScreen` so the system back button closes the active review overlay instead of finishing the app.
- **Onboarding comfort:** Increased bottom padding to 64dp and spacers to ensure primary buttons are fully visible and accessible on all screen sizes.

---

### Quiz of the Day & XP Refactor (June 2026)
**Files:** `QuizOfTheDayScreen.kt`, `QuizOfTheDayViewModel.kt`, `QuizOfTheDayRepository.kt`

**Problem:** Quiz XP was "all or nothing," retakes didn't encourage improvement once the mission was done, and words from quizzes couldn't be easily saved for review.

**Fixes applied:**
- **XP Logic Overhaul:** Implemented "Incremental XP" (delta-based). Users now earn XP based on their best score improvement, allowing retakes to "top up" XP if they score higher than before.
- **Bookmark Integration:** Added a Bookmark icon to each quiz question. The system automatically extracts the target vocabulary from the question text (e.g., words inside single quotes) and saves it to the Room DB for Spaced Repetition.
- **Exam Intelligence:** Integrated `ExamSourceBadge` directly into questions. This surfaces PYQ data (e.g., "Also in BCS 39") for editorial words, reinforcing the exam-relevance of the daily content.
- **Live Performance Tracking:** Added a mission status banner and a live score pill that updates in real-time, providing immediate feedback on whether the user is on track for the 80% mission credit.
- **Enhanced Results:** Redesigned the Results screen to show "Today's Best" score comparison and a transparent breakdown of XP earned during the attempt.

---

## 17. Known Issues and Status

| Issue | Status | Fix |
|---|---|---|
| **Notification open rate 0.33%** | 🚨 EMERGENCY | Add streak + exam days to FCM payload in firebase_campaign.py |
| **Onboarding completion 33.7%** | 🚨 EMERGENCY | Reduce to 3 steps max or make step 2–4 skippable in one tap |
| **WOTD daily active users: 144** | 🔴 Critical | Add dedicated WOTD FCM campaign at 6PM separate from quiz push |
| **Day-7 retention: no data yet** | ⏳ Pending | Check 7 June 2026 — target ≥15% |
| **Bookmark wire missing** | ✅ Live | saveWord() integrated in WOTD/Quiz |
| Rewarded ad show rate | 🟡 Improving | Retry logic shipped — 108 completions vs near-zero before |
| Analytics/Leaderboard show rate 2.3% | 🟡 Improving | Preload shipped in HomeScreen — measure next cycle |
| HN quiz antonym coverage 22% | Known | Run Gemini pass 2 on HN master words |
| Gemini 429 prepaid credits depleted | Known | Use free AI Studio key (aistudio.google.com/apikey) |
| Day-1 retention inflated (160%) | Known / Self-resolving | Tracker backfill on deploy — first clean cohort 7 June 2026 |
| Streak not syncing to Firestore | Fixed (Phase 2) | syncStreak() after recordActivityToday() |
| Analytics streak disconnected from StreakManager | Fixed (Phase 5) | calculateCurrentStreak() now reads StreakManager |
| Two streak counters | Fixed (Phase 5) | recordQuizAnalytics() removed duplicate streak logic |
| Article cross-date duplicates | Fixed (this session) | seen_links.json persistent URL registry in article_storage.py |
| Article wrong order (FE before Daily Star) | Fixed (this session) | applyArticleSort() 3-key sort — source weight as hard key 2 |
| EditorialNewsSection shows reversed order | Fixed (this session) | Removed cached path — always network fetch with serverOrderMap |
| serverOrderMap lookup misses | Fixed (this session) | Key changed from headline1 to link URL |
| Translation quota never triggered | Fixed (this session) | ArticleParagraphCard now uses lambda instead of direct VM call |
| TTS silent after rewarded ad | Fixed (this session) | Split into markTtsRewardEarned() + startSpeechAfterAdDismissed() |
| P1 native ads only 1 shown | Fixed (this session) | Spacing algorithm replaces modulo formula |
| WordOfTheDay Gson NPE crash | Fixed (this session) | All fields nullable in WordOfTheDayModels.kt |
| FCM notification screen reappears | Fixed (this session) | taskAffinity="" + correct intent flags |
| build_ci_image ran on every schedule | Fixed | $CI_PIPELINE_SOURCE == "push" rule |
| Quiz push failed non-fast-forward | Fixed | Moved quiz into main.py single git push |
| Bengali boxes in reel | Fixed | Playwright HTML renderer |
| WOTD date format mismatch | Fixed | getTodaySource() uses "dd MMMM yyyy" |
| Quiz offline shows error for premium | Fixed | fetchQuiz() pure network; ViewModel routes cache |
| Same word in multiple quiz question types | Fixed | Single global used_words Set |
| Quiz answer truncated | Fixed | _truncate() breaks at word boundary |
| EBookPromoDialog source param error | Fixed | source param removed |

---

## 18. Priority Action Plan (June 2026)

Ranked by revenue + retention impact based on Firebase data.

### ✅ Completed Items

| Task | Status |
|---|---|
| Website static page generation (WOTD + quiz) | ✅ Done |
| BCS/UPSC archive pages | ✅ Done |
| Region-aware navigation | ✅ Done |
| sitemap.xml auto-generation | ✅ Done |

### 🚨 Do this week

**1. Fix FCM notification copy — 0.33% open rate is costing ~$3/month**
In `firebase_campaign.py`, read today's streak from Firestore and include it in the FCM `notification.title`:
```python
# Current (bad):
title = "📖 New quiz published"

# Target (good):
title = f"🔥 {streak}-day streak · {days_to_exam} days to {exam_name}"
body  = f"Today's PYQ: '{quiz_word}' — can you get 10/10?"
```
This alone could move open rate from 0.33% to 2–3% — a 6–9× lift. At current notification volume (155K/month), that's 3,100–4,650 more opens/month → more article impressions → +$1.50–2.50/month from one copy change.
**Day 5 (Fri Jun 13) — Website launch checklist**
1. Verify `editorialvocab.github.io/docs/words/` redirects correctly for BD and IN
2. Submit `https://editorialvocab.github.io/sitemap.xml` to Google Search Console
3. Check 3–4 generated pages display correctly in browser
4. Add `localStorage.setItem('editorial_region', reg)` to `app.js` `setRegion()`
5. Confirm `.nojekyll` exists in docs/ root in GitHub repo
6. Set `GITHUB_PAGES_TARGET_PATH=""` env var in GitLab CI so files push to repo root not /docs/docs/


**2. Shorten onboarding — 33.7% completion means 66% of installs never get personalised notifications**
Step 2 (Exam Goal) and Step 3 (Exam Date) can be merged into one screen. Step 4 (Notification time) should default to 8PM and not require a tap — show it as a confirmation, not a choice. Target: 3 steps max, 60-second completion.

### 🔴 Do this month

**3. Dedicated WOTD FCM campaign**
Only 144 users opened WOTD in 28 days. WOTD has the highest interstitial eCPM ($1.63). Add a 6PM FCM push with the actual word of the day in the title:
```python
title = f"📖 Word of the Day: {wotd_word}"
body  = f"({part_of_speech}) {short_definition} · {source_badge}"
```
Send to `word_bn` and `word_hn` topics. Separate from the 1PM quiz push.
- Submit sitemap to Google Search Console: `https://editorialvocab.github.io/sitemap.xml`
- Apply for Google AdSense once 20+ pages indexed (check in Search Console ~2 weeks)
- Add `localStorage.setItem('editorial_region', reg)` to `setRegion()` in `app.js`
---

**4. Wire bookmark button** on WOTD + QuizOfTheDayScreen (one line each):
```kotlin
savedWordRepo.saveWord(word, meaning, source, lang)
```
This seeds the spaced review queue. SpacedReviewWorker then fires at 10AM when words are due — another notification touchpoint.

**5. Check Day-7 retention on 7 June 2026**
If `day_7_retained` event count in Firebase is ≥ 150 users → Phases 1–5 are working.
If < 100 users → streak system needs a more visible UI hook (e.g. streak count in app icon badge).

### 📊 Watch metrics

| Metric | Current | Target | Check date |
|---|---|---|---|
| Notification open rate | 0.33% | 2.0% | 30 June 2026 |
| Onboarding completion | 33.7% | 55% | 30 June 2026 |
| Day-7 retained events | 0 | ≥150 | 7 June 2026 |
| WOTD unique users/month | 144 | 400 | 30 June 2026 |
| Rewarded ad completions | 108/month | 300/month | 30 June 2026 |
| Monthly AdMob revenue | $13 | $20 | 30 June 2026 |

---

## 19. 🚨 Emergency 3-Day Plan — Reach $50/Month

**Revenue gap: $28/month needed.**
Analysis of all data shows three actions with the highest revenue-per-hour-of-work ratio.
Each can be completed in one day. Together they close the gap.

---

### Day 1 — Fix FCM notification copy (est. +$6–8/month)

**Why this first:** 155,971 notifications sent per month, only 509 opened (0.33%). Every 1% improvement in open rate = ~1,560 more article sessions = ~$1.50 more AdMob revenue. This is pure copy change — no Android build, no Play Store submission.

**File:** `firebase_campaign.py`

**Tasks:**
1. Read `streak_count` and `days_to_exam` from Firestore at campaign send time
2. Update WOTD push title:
   ```python
   title = f"🔥 {streak}d streak · Word: {wotd_word}"
   body  = f"({pos}) {definition[:60]}… · {source_badge}"
   ```
3. Update Quiz push title:
   ```python
   title = f"🎯 {days_to_exam} days to {exam_name} — Daily Quiz"
   body  = f"PYQ: '{quiz_word}' · Can you score 10/10 today?"
   ```
4. Update eBook push title:
   ```python
   title = f"📚 BCS/UPSC Vocab eBook — Free for {streak} streak holders"
   ```
5. Deploy — takes effect immediately on next 12PM CI run.

**Expected impact:** 0.33% → 2.0% open rate = 3,100 more opens/month → 3,100 more article reading sessions → ~$6–8/month at $1.48 eCPM article unit.

---

### Day 2 — Shorten onboarding from 6 steps to 3 (est. +$4–5/month)

**Why this second:** 66% of installs abandon onboarding → never get personalised notifications → never become habitual users → never generate ad revenue. At 1,015 installs/month, fixing this recovers ~670 users/month into the notification funnel.

**File:** `OnboardingScreen.kt`

**Tasks:**
1. Merge Step 2 (Exam Goal) + Step 3 (Exam Date) into one single screen with two inputs side-by-side
2. Step 4 (Notification time): remove the choice entirely. Default to 8PM silently. Show "We'll remind you at 8PM daily" as a confirmation line on the Done screen
3. New flow: Welcome (1) → Region + Exam + Date (2) → Done (3)
4. Keep all existing `ExamGoalPreferences` writes — just restructure the UI
5. No Play Store submission delay — this is a UI-only change in a single composable

**Expected impact:** 33.7% → 55% onboarding completion = ~220 more users/month entering the notification funnel → over 30 days compounds into higher DAU → +$4–5/month by end of June.

---

### Day 3 — Add dedicated 6PM WOTD FCM campaign (est. +$3–4/month)

**Why this third:** WOTD has the highest interstitial eCPM ($1.63) but only 144 unique users opened it in 28 days. The screen exists, the ads are configured — it just needs traffic. A dedicated 6PM push separate from the 1PM quiz push doubles the notification touchpoints per day.

**File:** `firebase_campaign.py` + `.gitlab-ci.yml`

**Tasks:**
1. Add new `run_wotd_evening_campaign()` function in `firebase_campaign.py`:
   ```python
   def run_wotd_evening_campaign(current_date):
       wotd_bn = load_wotd_for_date(current_date, "bn")
       wotd_hn = load_wotd_for_date(current_date, "hn")
       send_fcm(
           topic="word_bn",
           title=f"📖 আজকের শব্দ: {wotd_bn['word']}",
           body=f"{wotd_bn['definition'][:70]}…"
       )
       send_fcm(
           topic="word_hn",
           title=f"📖 आज का शब्द: {wotd_hn['word']}",
           body=f"{wotd_hn['definition'][:70]}…"
       )
   ```
2. Add new GitLab CI schedule: `SCHEDULE_TYPE=wotd_evening` at `0 12 * * *` UTC (6PM Dhaka)
3. Total CI budget impact: +2 min/day × 30 = +60 min/month → total ~568 min. Reduce eBook FCM to every other day to stay under 400 min free tier.

**Expected impact:** WOTD unique users 144 → 350/month = +206 more WOTD sessions at $1.63 eCPM = +$0.34/day = +$10/month potential. Conservative estimate with 30% notification open rate improvement: +$3–4/month.

---

### 3-Day Revenue Summary

| Day | Task | Est. monthly gain | Effort |
|---|---|---|---|
| Day 1 | FCM copy personalisation | +$6–8 | 3–4 hours, Python only |
| Day 2 | Shorten onboarding to 3 steps | +$4–5 | 4–5 hours, Kotlin UI only |
| Day 3 | 6PM WOTD FCM campaign | +$3–4 | 2–3 hours, Python + CI |
| **Total** | | **+$13–17/month** | **~10 hours total** |

**Projected monthly revenue after 3 days: $22 + $15 = ~$37/month**

Remaining gap to $50: ~$13/month — covered by:
- Rewarded ad completions growing (108 → 300 target, already improving)
- Article reading DAU growing from better notification open rate
- Day-7 retention data (7 June) confirming streak system is working

