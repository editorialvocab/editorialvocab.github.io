const BASE_URL = "https://gitlab.com/Mahadi07/rtejhs/-/raw/main/EdData/data";

const state = {
    region: 'IN', // Default: Hindu User
    suffix: 'EnToHn',
    view: 'wod',
    dateStrings: {},
    data: { wordOfDay: null, vocab: [], articles: [], quiz: [] }
};

function setupDateStrings() {
    const now = new Date();

    // If current time is before 8:30 AM, use yesterday's data
    const hours = now.getHours();
    const minutes = now.getMinutes();
    if (hours < 8 || (hours === 8 && minutes < 30)) {
        now.setDate(now.getDate() - 1);
    } else {
        // Ensure we are working with today if it's after 8:30
    }

    const day = String(now.getDate()).padStart(2, '0');
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const year = now.getFullYear();
    const monthName = now.toLocaleString('default', { month: 'long' });
    
    state.dateStrings = {
        daily: `${day}-${month}-${year}`,
        monthly: `${month}-${year}`,
        year: year,
        month: month,
        searchDate: `${day} ${monthName} ${year}` 
    };
}

async function init() {
    console.log("App initializing...");
    setupDateStrings();
    
    // 1. Setup UI Listeners
    const picker = document.getElementById('region-picker');
    if (picker) picker.onchange = (e) => switchRegion(e.target.value);
    
    const btnWod = document.getElementById('tab-wod');
    const btnArticles = document.getElementById('tab-articles');
    const btnVocab = document.getElementById('tab-vocab');
    const btnQuiz = document.getElementById('tab-quiz');

    if (btnWod) btnWod.onclick = () => switchTab('wod');
    if (btnArticles) btnArticles.onclick = () => switchTab('articles');
    if (btnVocab) btnVocab.onclick = () => switchTab('vocab');
    if (btnQuiz) btnQuiz.onclick = () => switchTab('quiz');

    switchTab('wod'); // Preselect Word of the Day

    // 2. Initial Load (Default IN)
    loadAllData();

    // 3. Try Auto-Detection (Fail-safe)
    detectLocation();
}

async function detectLocation() {
    const statusEl = document.getElementById('region-status');
    try {
        // 2 second timeout for location check
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 2000);
        
        const res = await fetch('https://ipapi.co/json/', { signal: controller.signal });
        const info = await res.json();
        clearTimeout(timeoutId);

        if (info.country_code === 'BD' && state.region !== 'BD') {
            document.getElementById('region-picker').value = 'BD';
            switchRegion('BD');
            statusEl.innerText = "Auto-detected: Bangladesh";
        } else {
            statusEl.innerText = `Region: ${state.region === 'BD' ? 'Bangladesh' : 'India'}`;
        }
    } catch (e) {
        statusEl.innerText = "Location: Manual Selection";
    }
}

function switchRegion(reg) {
    state.region = reg;
    state.suffix = reg === 'BD' ? 'EnToBn' : 'EnToHn';
    loadAllData();
}

function switchTab(view) {
    state.view = view;
    document.querySelectorAll('.tabs button').forEach(b => b.classList.remove('active'));
    const activeTab = document.getElementById(`tab-${view}`);
    if (activeTab) activeTab.classList.add('active');
    renderCurrentView();
}

async function loadAllData() {
    toggleLoader(true);
    try {
        const suffix = state.suffix;
        const { daily, monthly, year, month } = state.dateStrings;
        const regionFolder = state.region === 'IN' ? 'india' : 'bangladesh';

        // New Article Path: EdData/data/articles/india/2026/04/03-04-2026.json
        const articlePath = `${BASE_URL}/articles/${regionFolder}/${year}/${month}/${daily}.json`;

        const apiRequests = [
            fetch(`${BASE_URL}/WordOfTheDay${suffix}/${monthly}.json`).then(r => r.ok ? r.json() : null),
            fetch(`${BASE_URL}/${suffix}Word/${daily}.json`).then(r => r.ok ? r.json() : null),
            fetch(`${BASE_URL}/DayOfTheQuiz${suffix}/${daily}.json`).then(r => r.ok ? r.json() : null),
            fetch(articlePath).then(r => r.ok ? r.json() : null)
        ];

        const [wodRes, vocabRes, quizRes, artRes] = await Promise.allSettled([
            ...apiRequests
        ]);

        state.data.wordOfDay = (wodRes.status === 'fulfilled' && wodRes.value) ? wodRes.value.find(i => i.date.includes(state.dateStrings.searchDate)) : null;
        
        state.data.vocab = (vocabRes.status === 'fulfilled' && vocabRes.value) ? (vocabRes.value.wordMeaning || []) : [];
        state.data.quiz = (quizRes.status === 'fulfilled' && quizRes.value) ? (quizRes.value.questions || []) : [];
        
        state.data.articles = (artRes.status === 'fulfilled' && artRes.value) ? (artRes.value.articles || []) : [];

        renderCurrentView();
    } catch (err) {
        console.error("Data load error", err);
    }
    toggleLoader(false);
}

function renderCurrentView() {
    const container = document.getElementById('main-content');
    if (!container) return;
    
    if (state.view === 'wod') {
        const wod = state.data.wordOfDay;
        if (!wod) {
            container.innerHTML = `<p class="error-msg">Word of the Day not available for ${state.dateStrings.searchDate}</p>`;
            return;
        }
        const mKey = state.region === 'BD' ? 'bangla_meaning' : 'hindi_meaning';
        container.innerHTML = `
            <div class="word-of-day-detail">
                <h2 style="color:var(--primary-color)">${wod.word}</h2>
                <p><i>${wod.phonetic || ''} - ${wod.part_of_speech || ''}</i></p>
                <h3 style="margin-top:20px">${wod[mKey] || ''}</h3>
                <hr>
                <p><b>Definition:</b> ${wod.definition || ''}</p>
                <p><b>Example:</b> ${wod.example || ''}</p>
            </div>`;
    } else if (state.view === 'articles') {
        const articles = state.data.articles;
        if (!articles || articles.length === 0) {
            container.innerHTML = `<p class="error-msg">No articles found for ${state.dateStrings.daily}. Path checked: articles/${state.region === 'IN' ? 'india' : 'bangladesh'}/${state.dateStrings.year}/${state.dateStrings.month}/</p>`;
            return;
        }
        container.innerHTML = articles.map(a => `
            <div class="article-item" style="border-bottom: 1px solid #eee; padding-bottom: 15px; margin-bottom: 15px;">
                <small style="color: var(--primary-color); font-weight: bold;">${a.news_paper_name}</small>
                <h2 style="margin: 5px 0; font-size: 1.1rem;">${a.headline_1}</h2>
                <h3 style="margin: 5px 0; font-size: 0.95rem; color: #555; font-weight: normal;">${a.headline_2}</h3>
                <p style="font-size: 0.9rem; color: #666; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden;">
                    ${a.full_article}
                </p>
                <a href="${a.link}" target="_blank" style="font-size: 0.8rem; color: var(--primary-color); text-decoration: none;">Read Full Article →</a>
            </div>
        `).join('');
    } else if (state.view === 'vocab') {
        if (!state.data.vocab || state.data.vocab.length === 0) {
            container.innerHTML = '<p class="error-msg">Daily vocabulary not found for today.</p>';
            return;
        }
        container.innerHTML = state.data.vocab.map(v => {
            const parts = v.split(' : ');
            return `<div class="vocab-item"><div class="vocab-word">${parts[0]}</div><div class="vocab-meaning">${parts[1] || ''}</div></div>`;
        }).join('');
    } else {
        container.innerHTML = `<div class="quiz-container"><h3>Daily Quiz</h3><p>${state.data.quiz ? state.data.quiz.length : 0} Questions available for today.</p></div>`;
    }
}

function toggleLoader(s) { document.getElementById('loader').style.display = s ? 'block' : 'none'; }

window.onload = init;