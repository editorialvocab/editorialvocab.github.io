/* ═══════════════════════════════════════════════════════════════
   Editorial Vocabulary Web App — app.js
   Fetches live data from GitLab public repo.
   Features: WOD · Vocabulary · Articles · Full Interactive Quiz
   ═══════════════════════════════════════════════════════════════ */

const BASE = "https://gitlab.com/Mahadi07/rtejhs/-/raw/main/EdData/data";

// ── App State ────────────────────────────────────────────────────
const state = {
    region: "IN",           // "IN" = India (Hindi), "BD" = Bangladesh (Bengali)
    suffix: "EnToHn",
    activeTab: "vocab",
    dates: {},

    // fetched data
    wod:      null,
    vocab:    [],
    articles: [],
    quiz:     [],

    // quiz engine
    quizState: {
        current:   0,
        answers:   {},         // { index: selectedOption }
        submitted: {},         // { index: true } once answered
        score:     0,
        done:      false,
    },
};

// ── Date helpers ──────────────────────────────────────────────────
function buildDates() {
    const now = new Date();
    // If before 8:30 AM, use yesterday's data (pipeline runs at noon)
    if (now.getHours() < 8 || (now.getHours() === 8 && now.getMinutes() < 30)) {
        now.setDate(now.getDate() - 1);
    }
    const dd    = String(now.getDate()).padStart(2, "0");
    const mm    = String(now.getMonth() + 1).padStart(2, "0");
    const yyyy  = now.getFullYear();
    const monthNames = ["January","February","March","April","May","June",
                        "July","August","September","October","November","December"];
    state.dates = {
        daily:      `${dd}-${mm}-${yyyy}`,     // 25-04-2026
        monthly:    `${mm}-${yyyy}`,            // 04-2026
        year:       yyyy,
        month:      mm,
        searchDate: `${Number(dd)} ${monthNames[now.getMonth()]} ${yyyy}`, // "25 April 2026"
    };
    console.log("Generated dates:", state.dates);
}

// ── Fetch helper ──────────────────────────────────────────────────
async function fetchJSON(url) {
    try {
        const r = await fetch(url, { cache: "no-store" });
        if (!r.ok) {
            console.error(`Fetch failed for ${url}: HTTP status ${r.status}`);
            return null;
        }
        const data = await r.json();
        return data;
    } catch (e) { console.error(`Error fetching ${url}:`, e); return null; }
}

// ── Init ──────────────────────────────────────────────────────────
async function init() {
    buildDates();
    bindUI();
    await detectRegion();       // auto-detect first (fast)
    await loadAll();
}

// ── Region detection ──────────────────────────────────────────────
async function detectRegion() {
    const statusEl = document.getElementById("region-status");
    try {
        const ctrl = new AbortController();
        setTimeout(() => ctrl.abort(), 2500);
        const r    = await fetch("https://ipapi.co/json/", { signal: ctrl.signal });
        const info = await r.json();
        if (info?.country_code === "BD") {
            setRegion("BD");
            document.getElementById("region-picker").value = "BD";
        } else {
            setRegion("IN");
        }
        statusEl.textContent = state.region === "BD" ? "🇧🇩 Bangladesh" : "🇮🇳 India";
    } catch {
        statusEl.textContent = state.region === "BD" ? "🇧🇩 Bangladesh" : "🇮🇳 India";
    }
}

function setRegion(reg) {
    state.region = reg;
    state.suffix = reg === "BD" ? "EnToBn" : "EnToHn";
}

// ── Load all data ─────────────────────────────────────────────────
async function loadAll() {
    showLoader(true);
    const { daily, monthly, year, month, searchDate } = state.dates;
    const sf     = state.suffix;
    const folder = state.region === "IN" ? "india" : "bangladesh";

    // Log the URLs being constructed
    const wodUrl      = `${BASE}/WordOfTheDay${sf}/${monthly}.json`;
    const vocabUrl    = `${BASE}/${sf}Word/${daily}.json`;
    const quizUrl     = `${BASE}/DayOfTheQuiz${sf}/${daily}.json`;
    const articlesUrl = `${BASE}/articles/${folder}/${year}/${month}/${daily}.json`;
    console.log("Fetching WOD from:", wodUrl);
    console.log("Fetching Vocab from:", vocabUrl);
    console.log("Fetching Quiz from:", quizUrl);
    console.log("Fetching Articles from:", articlesUrl);

    const [wodData, vocabData, quizData, artData] = await Promise.all([
        fetchJSON(`${BASE}/WordOfTheDay${sf}/${monthly}.json`),
        fetchJSON(`${BASE}/${sf}Word/${daily}.json`),
        fetchJSON(`${BASE}/DayOfTheQuiz${sf}/${daily}.json`),
        fetchJSON(`${BASE}/articles/${folder}/${year}/${month}/${daily}.json`),
    ]);

    // WOD: find today's entry by date string
    if (Array.isArray(wodData)) {
        state.wod = wodData.find(w => w.date && w.date.includes(searchDate)) || null;
    } else {
        state.wod = null;
    }

    state.vocab    = Array.isArray(vocabData?.wordMeaning)  ? vocabData.wordMeaning  : [];
    state.quiz     = Array.isArray(quizData?.questions)     ? quizData.questions     : [];
    state.articles = Array.isArray(artData?.articles)       ? artData.articles       : [];

    // Reset quiz engine on region/date change
    resetQuizState();

    showLoader(false);
    renderWOD();
    renderActiveTab();
}

// ── Bind UI ───────────────────────────────────────────────────────
function bindUI() {
    // Region picker
    document.getElementById("region-picker").onchange = e => {
        setRegion(e.target.value);
        document.getElementById("region-status").textContent =
            state.region === "BD" ? "🇧🇩 Bangladesh" : "🇮🇳 India";
        loadAll();
    };

    // Tabs
    document.querySelectorAll(".tab-btn").forEach(btn => {
        btn.onclick = () => switchTab(btn.dataset.tab);
    });

    // Back to top
    const backTop = document.getElementById("back-top");
    window.addEventListener("scroll", () => {
        backTop.classList.toggle("visible", window.scrollY > 300);
    }, { passive: true });
    backTop.onclick = () => window.scrollTo({ top: 0, behavior: "smooth" });
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

// ── Loader ────────────────────────────────────────────────────────
function showLoader(on) {
    document.getElementById("loader").style.display = on ? "block" : "none";
}

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

    const mKey   = state.region === "BD" ? "bangla_meaning" : "hindi_meaning";
    const native = esc(wod[mKey] || wod.hindi_meaning || wod.bangla_meaning || "");
    const syns   = (wod.synonyms || []).slice(0, 5).map(s => `<span class="chip">${esc(s)}</span>`).join("");
    const ants   = (wod.antonyms || []).slice(0, 5).map(a => `<span class="chip">${esc(a)}</span>`).join("");

    el.innerHTML = `
        ${wod.word ? `<div class="wod-word">${esc(wod.word)}</div>` : ""}
        ${wod.phonetic ? `<div class="wod-phonetic">${esc(wod.phonetic)}</div>` : ""}
        ${wod.part_of_speech ? `<div class="wod-pos">${esc(wod.part_of_speech)}</div>` : ""}
        ${native ? `<div class="wod-native">${esc(native)}</div>` : ""}
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
        ${wod.audio_url ? `
            <button class="wod-audio-btn" onclick="playAudio('${esc(wod.audio_url)}')">
                🔊 Pronunciation
            </button>` : ""}
    `;
}

function playAudio(url) {
    if (!url) return;
    new Audio(url).play().catch(() => {});
}

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
                <div class="vocab-num">${String(i+1).padStart(2,"0")}</div>
                <div class="vocab-body">
                    <div class="vocab-word">${esc(word?.trim() || "")}</div>
                    <div class="vocab-meaning">${esc(meaning?.trim() || "")}</div>
                </div>
            </div>`;
    }).join("");

    el.innerHTML = `
        <div class="vocab-header">
            Today's 10 Words — <em>${src}</em>
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

    el.innerHTML = `<div class="articles-list">${cards}</div>`;
}

// ═══════════════════════════════════════════════════════════════
//  QUIZ ENGINE
// ═══════════════════════════════════════════════════════════════
function resetQuizState() {
    state.quizState = {
        current:   0,
        answers:   {},
        submitted: {},
        score:     0,
        done:      false,
    };
}

function renderQuiz() {
    const el  = document.getElementById("panel-quiz");
    const qs  = state.quizState;
    const all = state.quiz;

    if (!all.length) {
        el.innerHTML = emptyState("✏️", `No quiz available for ${state.dates.daily}.`);
        return;
    }

    if (qs.done) {
        renderQuizResult(el);
        return;
    }

    const q         = all[qs.current];
    const total     = all.length;
    const progress  = ((qs.current) / total) * 100;
    const answered  = qs.submitted[qs.current];

    const options = q.options.map((opt, i) => {
        let cls = "quiz-option";
        if (answered) {
            if (opt === q.answer) {
                cls += qs.answers[qs.current] === opt ? " selected-correct" : " show-correct";
            } else if (qs.answers[qs.current] === opt) {
                cls += " selected-wrong";
            }
        }
        const disabled = answered ? "disabled" : "";
        return `<button class="${cls}" ${disabled}
                    onclick="selectAnswer(${i}, \`${escAttr(opt)}\`)">
                    ${esc(opt)}
                </button>`;
    }).join("");

    el.innerHTML = `
        <div class="quiz-header">
            <div class="quiz-title">Daily Quiz</div>
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
    const q  = state.quiz[qs.current];

    if (qs.submitted[qs.current]) return; // already answered

    qs.answers[qs.current]   = value;
    qs.submitted[qs.current] = true;

    if (value === q.answer) qs.score++;

    renderQuiz();
}

function quizNext() {
    if (state.quizState.current < state.quiz.length - 1) {
        state.quizState.current++;
        renderQuiz();
    }
}

function quizPrev() {
    if (state.quizState.current > 0) {
        state.quizState.current--;
        renderQuiz();
    }
}

function finishQuiz() {
    state.quizState.done = true;
    renderQuiz();
}

function renderQuizResult(el) {
    const { score } = state.quizState;
    const total     = state.quiz.length;
    const pct       = Math.round((score / total) * 100);

    let emoji = "😟", grade = "Keep practising";
    if (pct >= 90) { emoji = "🏆"; grade = "Excellent!";     }
    else if (pct >= 70) { emoji = "🎯"; grade = "Well done!";    }
    else if (pct >= 50) { emoji = "📚"; grade = "Good effort!";  }

    el.innerHTML = `
        <div class="quiz-result">
            <div class="quiz-result-emoji">${emoji}</div>
            <div class="quiz-result-title">${grade}</div>
            <div class="quiz-result-score">${score}/${total}</div>
            <div class="quiz-result-label">${pct}% accuracy · ${state.dates.daily}</div>
            <button class="quiz-restart-btn" onclick="restartQuiz()">Try Again</button>
        </div>`;
}

function restartQuiz() {
    resetQuizState();
    renderQuiz();
}

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
    return `<div class="empty-state">
                <div class="empty-icon">${icon}</div>
                <p>${msg}</p>
            </div>`;
}

// ── Boot ──────────────────────────────────────────────────────────
window.addEventListener("DOMContentLoaded", init);