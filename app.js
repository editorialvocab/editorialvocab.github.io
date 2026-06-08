/* ═══════════════════════════════════════════════════════════════
   Editorial Vocabulary Web App — app.js
   Fetches live data from GitLab public repo.
   Features: WOD · Vocabulary · Articles · Full Interactive Quiz
   ═══════════════════════════════════════════════════════════════ */

const BASE = "https://gl.githack.com/Mahadi07/rtejhs/raw/main/EdData/data";

// ── App State ────────────────────────────────────────────────────
const state = {
    region:    "IN",
    suffix:    "EnToHn",
    activeTab: "vocab",
    dates:     {},
    wod:       null,
    vocab:     [],
    articles:  [],
    quiz:      [],
    quizState: { current: 0, answers: {}, submitted: {}, score: 0, done: false },
};

// ── Date helpers ──────────────────────────────────────────────────
function buildDates(specificDate = null) {
    const now  = specificDate || new Date();
    const dd   = String(now.getDate()).padStart(2, "0");
    const mm   = String(now.getMonth() + 1).padStart(2, "0");
    const yyyy = now.getFullYear();
    const monthNames = ["January","February","March","April","May","June",
                        "July","August","September","October","November","December"];
    state.dates = {
        daily:      `${dd}-${mm}-${yyyy}`,
        monthly:    `${mm}-${yyyy}`,
        year:       yyyy,
        month:      mm,
        searchDate: `${Number(dd)} ${monthNames[now.getMonth()]} ${yyyy}`,
    };
}

// ── Fetch helper ──────────────────────────────────────────────────
async function fetchJSON(url) {
    try {
        const r = await fetch(url, { cache: "no-store" });
        if (!r.ok) return null;
        return await r.json();
    } catch { return null; }
}

// ── Init ──────────────────────────────────────────────────────────
async function init() {
    buildDates();
    bindUI();
    initFeaturesCarousel();
    await detectRegion();
    await loadAll();
    updateVisitorCount();
}

// ── Region detection ──────────────────────────────────────────────
async function detectRegion() {
    const statusEl = document.getElementById("region-status");
    try {
        const ctrl = new AbortController();
        setTimeout(() => ctrl.abort(), 2500);
        const r    = await fetch("https://ipwho.is/", { signal: ctrl.signal });
        const info = await r.json();
        if (info?.country_code === "BD") {
            setRegion("BD");
            document.getElementById("region-picker").value = "BD";
        } else {
            setRegion("IN");
        }
    } catch { /* default IN */ }
    statusEl.textContent = state.region === "BD" ? "🇧🇩 Bangladesh" : "🇮🇳 India";
}

function setRegion(reg) {
    state.region = reg;
    state.suffix = reg === "BD" ? "EnToBn" : "EnToHn";
    updateBrandUI();
}

function updateBrandUI() {
    const topBrand    = document.getElementById("brand-name-top");
    const footerBrand = document.getElementById("brand-name-footer");
    const badge       = document.getElementById("brand-badge");
    if (!topBrand || !badge) return;

    const isBD     = state.region === "BD";
    const mainTitle = isBD
        ? `Daily Star Vocab & Editorials <span class="brand-accent">Official</span>`
        : `Hindu Vocab & Editorials <span class="brand-accent">Official</span>`;

    topBrand.innerHTML = mainTitle;
    if (footerBrand) footerBrand.innerHTML = mainTitle;
    badge.innerHTML = `⚡ ${isBD ? "Daily Star" : "Hindu"} Vocab Official | 106 K+ Aspirants | 4.8 ⭐ Rating`;
}

// ── Load all data ─────────────────────────────────────────────────
async function loadAll(isRetry = false) {
    showLoader(true);
    const { daily, monthly, year, month, searchDate } = state.dates;
    const sf     = state.suffix;
    const folder = state.region === "IN" ? "india" : "bangladesh";

    const [wodData, vocabData, quizData, artData] = await Promise.all([
        fetchJSON(`${BASE}/WordOfTheDay${sf}/${monthly}.json`),
        fetchJSON(`${BASE}/${sf}Word/${daily}.json`),
        fetchJSON(`${BASE}/DayOfTheQuiz${sf}/${daily}.json`),
        fetchJSON(`${BASE}/articles/${folder}/${year}/${month}/${daily}.json`),
    ]);

    if (!vocabData && !isRetry) {
        const yesterday = new Date();
        yesterday.setDate(yesterday.getDate() - 1);
        buildDates(yesterday);
        return loadAll(true);
    }

    state.wod = Array.isArray(wodData)
        ? (wodData.find(w => w.date && w.date.includes(searchDate)) || null)
        : null;

    state.vocab    = Array.isArray(vocabData?.wordMeaning) ? vocabData.wordMeaning : [];
    state.quiz     = Array.isArray(quizData?.questions)    ? quizData.questions    : [];
    state.articles = Array.isArray(artData?.articles)      ? artData.articles      : [];

    resetQuizState();
    showLoader(false);
    renderWOD();
    renderActiveTab();
    renderAppDownloadIcon();
    renderSocialLinks();
    renderDatePicker();

    // ── SEO: update page title + meta when word loads ─────────────
    updatePageMeta();

    // ── Schema: inject WordDefinition structured data ─────────────
    injectWordSchema();
}

// ── Dynamic page meta (SEO) ───────────────────────────────────────
function updatePageMeta() {
    if (!state.wod?.word) return;
    const word   = state.wod.word;
    const region = state.region === "BD" ? "BCS PSC Bangladesh" : "UPSC SSC India";
    const suffix = state.region === "BD" ? "in Bengali" : "in Hindi";
    const def    = (state.wod.definition || "").slice(0, 100);

    document.title = `${word} meaning ${suffix} — Editorial Vocabulary | ${region}`;

    const metaDesc = document.querySelector('meta[name="description"]');
    if (metaDesc) {
        metaDesc.content =
            `${word}: ${def}. Daily vocabulary from editorials for ${region} exam prep. ` +
            `Word of the Day, quiz, and 10 vocab words — free.`;
    }

    const ogTitle = document.querySelector('meta[property="og:title"]');
    if (ogTitle) ogTitle.content = `${word} — Word of the Day | Editorial Vocabulary`;

    const ogDesc = document.querySelector('meta[property="og:description"]');
    if (ogDesc) ogDesc.content = `${word}: ${def}`;
}

// ── Schema.org WordDefinition injection ──────────────────────────
function injectWordSchema() {
    const existing = document.getElementById("word-schema-ld");
    if (existing) existing.remove();
    if (!state.wod?.word) return;

    const schema = {
        "@context": "https://schema.org",
        "@type": "DefinedTerm",
        "name": state.wod.word,
        "description": state.wod.definition || "",
        "inDefinedTermSet": {
            "@type": "DefinedTermSet",
            "name": "Editorial Vocabulary — Daily Word",
            "url": "https://promahadihasan.github.io/editroail_app/",
        },
        "termCode": state.dates.searchDate,
    };

    const script = document.createElement("script");
    script.id   = "word-schema-ld";
    script.type = "application/ld+json";
    script.text = JSON.stringify(schema);
    document.head.appendChild(script);
}

// ── Visitor Counter ───────────────────────────────────────────────
// FIX: countapi.xyz shut down in 2023 — replaced with counterapi.dev
async function updateVisitorCount() {
    const countEl  = document.getElementById("visitor-count");
    if (!countEl) return;
    const APP_BASE = 106000;

    try {
        // counterapi.dev is a CORS-friendly free hit counter
        const r    = await fetch("https://api.counterapi.dev/v1/mahadi-editorial-vocab/web-visits/hit");
        const data = await r.json();
        const total = APP_BASE + (data?.count || 0);
        countEl.innerHTML = `
            <span class="count-number">${total.toLocaleString()}</span>
            <span class="count-label">Aspirants Learning</span>`;
    } catch {
        // Graceful fallback — estimate based on install count + daily growth
        const daysSinceJan25 = Math.max(0, Math.floor(
            (Date.now() - new Date("2025-01-01").getTime()) / 86_400_000
        ));
        const estimated = APP_BASE + daysSinceJan25 * 12;
        countEl.innerHTML = `
            <span class="count-number">${estimated.toLocaleString()}+</span>
            <span class="count-label">Aspirants Learning</span>`;
    }
}

// ── Bind UI ───────────────────────────────────────────────────────
function bindUI() {
    document.getElementById("region-picker").onchange = e => {
        setRegion(e.target.value);
        document.getElementById("region-status").textContent =
            state.region === "BD" ? "🇧🇩 Bangladesh" : "🇮🇳 India";
        loadAll();
    };

    document.querySelectorAll(".tab-btn").forEach(btn => {
        btn.onclick = () => switchTab(btn.dataset.tab);
    });

    const backTop = document.getElementById("back-top");
    window.addEventListener("scroll", () => {
        backTop.classList.toggle("visible", window.scrollY > 300);
    }, { passive: true });
    backTop.onclick = () => window.scrollTo({ top: 0, behavior: "smooth" });
}

// ── Features Carousel Logic ──────────────────────────────────────
function initFeaturesCarousel() {
    const wrapper = document.getElementById("carousel-wrapper");
    const grid    = document.getElementById("features-grid");
    const cards   = grid.querySelectorAll(".feature-card");
    const dotsEl  = document.getElementById("features-dots");
    const nextBtn = document.getElementById("features-next");
    const prevBtn = document.getElementById("features-prev");

    let currentIndex = 0;
    const gap = 24;
    let startX = 0, isDragging = false;

    cards.forEach((_, i) => {
        const dot = document.createElement("div");
        dot.className = `dot ${i === 0 ? "active" : ""}`;
        dot.onclick   = () => goToSlide(i);
        dotsEl.appendChild(dot);
    });

    function updateNavButtons() {
        prevBtn.style.display = currentIndex === 0 ? "none" : "flex";
        const cardWidth   = cards[0].offsetWidth;
        const totalWidth  = (cardWidth + gap) * cards.length - gap;
        const visibleWidth = wrapper.offsetWidth;
        nextBtn.style.display =
            (currentIndex * (cardWidth + gap) + visibleWidth) >= totalWidth ? "none" : "flex";
    }

    function goToSlide(index) {
        if (index < 0) index = 0;
        if (index >= cards.length) index = cards.length - 1;
        currentIndex = index;
        const cardWidth = cards[0].offsetWidth;
        grid.style.transform = `translateX(-${index * (cardWidth + gap)}px)`;
        document.querySelectorAll(".dot").forEach((d, i) =>
            d.classList.toggle("active", i === index));
        updateNavButtons();
    }

    nextBtn.onclick = () => goToSlide(currentIndex + 1);
    prevBtn.onclick = () => goToSlide(currentIndex - 1);

    wrapper.addEventListener("touchstart", e => {
        startX = e.touches[0].clientX; isDragging = true;
    }, { passive: true });
    wrapper.addEventListener("touchend", e => {
        if (!isDragging) return;
        const diff = startX - e.changedTouches[0].clientX;
        if (Math.abs(diff) > 50) goToSlide(currentIndex + (diff > 0 ? 1 : -1));
        isDragging = false;
    }, { passive: true });

    let autoTimer = setInterval(() => goToSlide((currentIndex + 1) % cards.length), 4000);
    wrapper.addEventListener("mouseenter", () => clearInterval(autoTimer));
    wrapper.addEventListener("touchstart",  () => clearInterval(autoTimer));
    window.addEventListener("resize", () => goToSlide(currentIndex));
    updateNavButtons();
}

function switchTab(tab) {
    state.activeTab = tab;
    document.querySelectorAll(".tab-btn").forEach(b =>
        b.classList.toggle("active", b.dataset.tab === tab));
    document.querySelectorAll(".tab-panel").forEach(p =>
        p.classList.toggle("active", p.id === `panel-${tab}`));
    renderActiveTab();
}

function renderActiveTab() {
    switch (state.activeTab) {
        case "vocab":    renderVocab();    break;
        case "articles": renderArticles(); break;
        case "quiz":     renderQuiz();     break;
    }
}

function showLoader(on) {
    document.getElementById("loader").style.display = on ? "block" : "none";
}

function renderAppDownloadIcon() {
    const appIconLink = document.getElementById("app-icon-link");
    const appIconImg  = document.getElementById("app-icon-img");
    if (!appIconLink || !appIconImg) return;

    appIconImg.src    = state.region === "BD"
        ? "image/appIcon/app_icon_dailyStar.png"
        : "image/appIcon/app_icon_The_Hindu.png";
    appIconLink.href  = "https://play.google.com/store/apps/details?id=megaminds.dailyeditorialword";
    appIconLink.title = `Download on Google Play (${state.region === "BD" ? "Daily Star" : "The Hindu"} version)`;
}

// ── Render Social Links — FIXED ───────────────────────────────────
// Changes from previous version:
//   1. BD Facebook now uses editorialvocabappbd (was editorialvocabapp)
//   2. Instagram now reads from links object per region (was hardcoded India URL)
//   3. igLink handled safely with correct BD/IN handle

function renderSocialLinks() {
    const fbLink = document.getElementById("footer-fb");
    const ytLink = document.getElementById("footer-yt");
    const igLink = document.getElementById("footer-ig");
    const tag    = document.getElementById("social-region-tag");
    if (!fbLink || !ytLink) return;

    const links = {
        BD: {
            fb:    "https://www.facebook.com/editorialvocabappbd",   
            yt:    "https://www.youtube.com/@editorialvocabappbd",
            ig:    "https://www.instagram.com/editorialvocabappbd",  
            label: "(Bangladesh)",
        },
        IN: {
            fb:    "https://www.facebook.com/editorialvocabapp",
            yt:    "https://www.youtube.com/@editorialvocabapp",
            ig:    "https://www.instagram.com/editorialvocabapp",
            label: "(India)",
        },
    };

    const active = links[state.region] || links.IN;
    fbLink.href = active.fb;
    ytLink.href = active.yt;
    if (igLink) igLink.href = active.ig;     // ← FIXED: now reads from links object
    if (tag)    tag.textContent = active.label;
}

function renderDatePicker() {
    const container = document.getElementById("date-selector");
    if (!container) return;

    const today = new Date();
    if (today.getHours() < 11 || (today.getHours() === 11 && today.getMinutes() < 30)) {
        today.setDate(today.getDate() - 1);
    }

    let html = "";
    for (let i = 0; i < 3; i++) {
        const d    = new Date(today);
        d.setDate(d.getDate() - i);
        const dd   = String(d.getDate()).padStart(2, "0");
        const mm   = String(d.getMonth() + 1).padStart(2, "0");
        const yyyy = d.getFullYear();
        const dateStr = `${dd}-${mm}-${yyyy}`;
        const label = i === 0 ? "Today"
            : i === 1 ? "Yesterday"
            : `${d.getDate()} ${d.toLocaleString("en-US", { month: "short" })}`;
        const active = state.dates.daily === dateStr ? "active" : "";
        html += `<button class="date-pill ${active}" onclick="selectDate('${dateStr}')">${label}</button>`;
    }
    container.innerHTML = html;
}

window.selectDate = (dateStr) => {
    const [dd, mm, yyyy] = dateStr.split("-").map(Number);
    buildDates(new Date(yyyy, mm - 1, dd));
    loadAll();
};

// ═══════════════════════════════════════════════════════════════
//  WORD OF THE DAY
// ═══════════════════════════════════════════════════════════════
function renderWOD() {
    const el  = document.getElementById("wod-card");
    const wod = state.wod;

    if (!wod) {
        el.innerHTML = `
            <div class="wod-empty">
                <p>Word of the Day not available for<br><strong>${state.dates.searchDate}</strong></p>
                <p style="margin-top:8px;font-size:0.8rem;color:var(--text-mute)">
                    Data updates daily at noon. Try again later.
                </p>
            </div>`;
        return;
    }

    const mKey  = state.region === "BD" ? "bangla_meaning" : "hindi_meaning";
    const native = esc(wod[mKey] || wod.hindi_meaning || wod.bangla_meaning || "");
    const syns   = (wod.synonyms || []).slice(0, 5).map(s => `<span class="chip">${esc(s)}</span>`).join("");
    const ants   = (wod.antonyms || []).slice(0, 5).map(a => `<span class="chip">${esc(a)}</span>`).join("");

    el.innerHTML = `
        <div class="wod-date-top">${esc(state.dates.searchDate)}</div>
        ${wod.word     ? `<div class="wod-word">${esc(wod.word)}</div>` : ""}
        ${wod.phonetic ? `<div class="wod-phonetic">${esc(wod.phonetic)}</div>` : ""}
        ${wod.part_of_speech ? `<div class="wod-pos">${esc(wod.part_of_speech)}</div>` : ""}
        ${native       ? `<div class="wod-native">${native}</div>` : ""}
        <div class="wod-divider"></div>
        ${wod.definition ? `
            <div class="wod-field">
                <div class="wod-label">Definition</div>
                <div class="wod-value">${esc(wod.definition)}</div>
            </div>` : ""}
        ${wod.example ? `
            <div class="wod-field">
                <div class="wod-label">Example</div>
                <div class="wod-value wod-example">"${esc(wod.example)}"</div>
            </div>` : ""}
        ${syns ? `
            <div class="wod-field">
                <div class="wod-label">Synonyms</div>
                <div class="wod-chips">${syns}</div>
            </div>` : ""}
        ${ants ? `
            <div class="wod-field">
                <div class="wod-label">Antonyms</div>
                <div class="wod-chips">${ants}</div>
            </div>` : ""}
        <div class="wod-actions">
            ${wod.audio_url ? `
                <button class="wod-audio-btn" onclick="playAudio('${esc(wod.audio_url)}')">
                    🔊 Pronunciation
                </button>` : ""}
            <button class="wod-share-btn" onclick="shareWord()">
                📤 Share Word
            </button>
        </div>
    `;
}

function playAudio(url) {
    if (!url) return;
    new Audio(url).play().catch(() => {});
}

// ── Share Word (Web Share API + clipboard fallback) ───────────────
function shareWord() {
    const wod     = state.wod;
    if (!wod?.word) return;
    const mKey    = state.region === "BD" ? "bangla_meaning" : "hindi_meaning";
    const meaning = wod[mKey] || wod.definition || "";
    const text    = `📖 Word of the Day: ${wod.word}\n` +
                    `${wod.phonetic ? wod.phonetic + "\n" : ""}` +
                    `${wod.part_of_speech ? "(" + wod.part_of_speech + ")\n" : ""}` +
                    `\n${meaning}\n` +
                    `${wod.definition ? "\n" + wod.definition : ""}\n` +
                    `\n🎯 Learn free: ${window.location.href}\n` +
                    `📱 App: https://cutt.ly/lnSnI0A`;

    if (navigator.share) {
        navigator.share({ title: `Word: ${wod.word}`, text }).catch(() => {});
    } else {
        navigator.clipboard?.writeText(text).then(() => {
            alert("Word copied to clipboard!");
        }).catch(() => {
            alert("Share: " + text);
        });
    }
}
window.shareWord = shareWord;

// ═══════════════════════════════════════════════════════════════
//  VOCABULARY
// ═══════════════════════════════════════════════════════════════
function renderVocab() {
    const el  = document.getElementById("panel-vocab");
    const src = state.region === "BD" ? "The Daily Star" : "The Hindu";

    if (!state.vocab.length) {
        el.innerHTML = emptyState("📚", `No vocabulary found for ${state.dates.daily}.`);
        return;
    }

    const items = state.vocab.map((entry, i) => {
        const [word, meaning] = entry.split(" : ");
        return `
            <div class="vocab-item">
                <div class="vocab-num">${String(i + 1).padStart(2, "0")}</div>
                <div class="vocab-body">
                    <div class="vocab-word">${esc(word?.trim() || "")}</div>
                    <div class="vocab-meaning">${esc(meaning?.trim() || "")}</div>
                </div>
            </div>`;
    }).join("");

    el.innerHTML = `
        <div class="vocab-header">
            10 Daily Vocab — <em>${src}</em> for ${esc(state.dates.searchDate)}
        </div>
        <div class="vocab-list">${items}</div>`;
}

// ═══════════════════════════════════════════════════════════════
//  ARTICLES
// ═══════════════════════════════════════════════════════════════
function renderArticles() {
    const el = document.getElementById("panel-articles");

    if (!state.articles.length) {
        el.innerHTML = emptyState("📰",
            `No articles found for ${state.dates.daily}.<br>
             Articles are fetched from editorials scraped each day at noon.`);
        return;
    }

    const cards = state.articles.map(a => `
        <div class="article-card">
            <div class="article-source">${esc(a.news_paper_name || "")}</div>
            <div class="article-h1">${esc(a.headline_1 || "")}</div>
            ${a.headline_2 ? `<div class="article-h2">${esc(a.headline_2)}</div>` : ""}
            <p class="article-excerpt">${esc(a.full_article?.slice(0, 300) || "")}</p>
            <a class="article-link" href="${esc(a.link || "#")}" target="_blank" rel="noopener">
                Read full article →
            </a>
        </div>`).join("");

    el.innerHTML = `
        <div class="vocab-header">Articles for ${esc(state.dates.searchDate)}</div>
        <div class="articles-list">${cards}</div>`;
}

// ═══════════════════════════════════════════════════════════════
//  QUIZ ENGINE
// ═══════════════════════════════════════════════════════════════
function resetQuizState() {
    state.quizState = { current: 0, answers: {}, submitted: {}, score: 0, done: false };
}

function renderQuiz() {
    const el  = document.getElementById("panel-quiz");
    const qs  = state.quizState;
    const all = state.quiz;

    if (!all.length) {
        el.innerHTML = emptyState("✏️", `No quiz available for ${state.dates.daily}.`);
        return;
    }
    if (qs.done) { renderQuizResult(el); return; }

    const q        = all[qs.current];
    const total    = all.length;
    const progress = (qs.current / total) * 100;
    const answered = qs.submitted[qs.current];

    const options = q.options.map((opt, i) => {
        let cls = "quiz-option";
        if (answered) {
            if (opt === q.answer)               cls += qs.answers[qs.current] === opt ? " selected-correct" : " show-correct";
            else if (qs.answers[qs.current] === opt) cls += " selected-wrong";
        }
        return `<button class="${cls}" ${answered ? "disabled" : ""}
                    onclick="selectAnswer(${i}, \`${escAttr(opt)}\`)">
                    ${esc(opt)}
                </button>`;
    }).join("");

    el.innerHTML = `
        <div class="quiz-header">
            <div class="quiz-title">Daily Quiz — ${esc(state.dates.searchDate)}</div>
            <div class="quiz-score-badge">Score ${qs.score} / ${total}</div>
        </div>
        <div class="quiz-progress">
            <div class="quiz-progress-bar" style="width:${progress}%"></div>
        </div>
        <div class="quiz-q-block">
            <div class="quiz-q-num">Question ${qs.current + 1} of ${total}</div>
            <div class="quiz-q-text">${esc(q.question || "")}</div>
            <div class="quiz-options">${options}</div>
            <div class="quiz-nav">
                ${qs.current > 0
                    ? `<button class="quiz-btn quiz-btn-secondary" onclick="quizPrev()">← Prev</button>`
                    : `<span></span>`}
                ${answered
                    ? (qs.current < total - 1
                        ? `<button class="quiz-btn quiz-btn-primary" onclick="quizNext()">Next →</button>`
                        : `<button class="quiz-btn quiz-btn-primary" onclick="finishQuiz()">See Results 🎉</button>`)
                    : `<span style="font-size:0.8rem;color:var(--text-mute)">Select an answer</span>`}
            </div>
        </div>`;
}

function selectAnswer(optionIndex, value) {
    const qs = state.quizState;
    if (qs.submitted[qs.current]) return;
    qs.answers[qs.current]   = value;
    qs.submitted[qs.current] = true;
    if (value === state.quiz[qs.current].answer) qs.score++;
    renderQuiz();
}

function quizNext() {
    if (state.quizState.current < state.quiz.length - 1) { state.quizState.current++; renderQuiz(); }
}
function quizPrev() {
    if (state.quizState.current > 0) { state.quizState.current--; renderQuiz(); }
}
function finishQuiz() { state.quizState.done = true; renderQuiz(); }

function renderQuizResult(el) {
    const { score } = state.quizState;
    const total = state.quiz.length;
    const pct   = Math.round((score / total) * 100);
    let emoji = "😟", grade = "Keep practising";
    if      (pct >= 90) { emoji = "🏆"; grade = "Excellent!";    }
    else if (pct >= 70) { emoji = "🎯"; grade = "Well done!";    }
    else if (pct >= 50) { emoji = "📚"; grade = "Good effort!";  }

    el.innerHTML = `
        <div class="quiz-result">
            <div class="quiz-result-emoji">${emoji}</div>
            <div class="quiz-result-title">${grade}</div>
            <div class="quiz-result-score">${score}/${total}</div>
            <div class="quiz-result-label">${pct}% accuracy · ${state.dates.daily}</div>
            <button class="quiz-restart-btn" onclick="restartQuiz()">Try Again</button>
            <p style="margin-top:16px;font-size:0.78rem;color:var(--text-mute)">
                Practice more with XP, streaks &amp; leaderboards in the app.
            </p>
            <a class="wod-share-btn" href="https://play.google.com/store/apps/details?id=megaminds.dailyeditorialword"
               target="_blank" rel="noopener" style="display:inline-block;margin-top:8px;text-decoration:none;">
               📱 Download App
            </a>
        </div>`;
}

function restartQuiz() { resetQuizState(); renderQuiz(); }

// ── Helpers ───────────────────────────────────────────────────────
function esc(s) {
    if (typeof s !== "string") return "";
    return s.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;")
            .replace(/"/g,"&quot;").replace(/'/g,"&#39;");
}
function escAttr(s) {
    if (typeof s !== "string") return "";
    return s.replace(/`/g, "\\`").replace(/\$/g, "\\$");
}
function emptyState(icon, msg) {
    return `<div class="empty-state"><div class="empty-icon">${icon}</div><p>${msg}</p></div>`;
}

// ── Boot ──────────────────────────────────────────────────────────
window.addEventListener("DOMContentLoaded", init);