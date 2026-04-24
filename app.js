const BASE_URL = "https://gitlab.com/Mahadi07/rtejhs/-/raw/main/EdData/data";

const state = {
    region: 'IN', // Default: Hindu User
    suffix: 'EnToHn',
    view: 'articles',
    dateStrings: {},
    data: { wordOfDay: null, vocab: [], articles: [], quiz: [] }
};

function setupDateStrings() {
    const now = new Date();
    const day = String(now.getDate()).padStart(2, '0');
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const year = now.getFullYear();
    const monthName = now.toLocaleString('default', { month: 'long' });
    
    state.dateStrings = {
        daily: `${day}-${month}-${year}`,
        monthly: `${month}-${year}`,
        searchDate: `${parseInt(day)} ${monthName} ${year}` // Matches "24 April 2026"
    };
}

async function init() {
    setupDateStrings();
    
    // 1. Setup UI Listeners
    const picker = document.getElementById('region-picker');
    picker.onchange = (e) => switchRegion(e.target.value);
    
    document.getElementById('tab-articles').onclick = () => switchTab('articles');
    document.getElementById('tab-vocab').onclick = () => switchTab('vocab');
    document.getElementById('tab-quiz').onclick = () => switchTab('quiz');

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
    document.getElementById(`tab-${view}`).classList.add('active');
    renderCurrentView();
}

async function loadAllData() {
    toggleLoader(true);
    try {
        const suffix = state.suffix;
        const [wodRes, vocabRes, quizRes, artRes] = await Promise.allSettled([
            fetch(`${BASE_URL}/WordOfTheDay${suffix}/${state.dateStrings.monthly}.json`).then(r => r.json()),
            fetch(`${BASE_URL}/${suffix}Word/${state.dateStrings.daily}.json`).then(r => r.json()),
            fetch(`${BASE_URL}/DayOfTheQuiz${suffix}/${state.dateStrings.daily}.json`).then(r => r.json()),
            fetch(`${BASE_URL}/articles_${state.region.toLowerCase()}.json`).then(r => r.json())
        ]);

        state.data.wordOfDay = wodRes.status === 'fulfilled' ? wodRes.value.find(i => i.date.includes(state.dateStrings.searchDate)) : null;
        state.data.vocab = vocabRes.status === 'fulfilled' ? vocabRes.value.wordMeaning : [];
        state.data.quiz = quizRes.status === 'fulfilled' ? quizRes.value.questions : [];
        state.data.articles = artRes.status === 'fulfilled' ? artRes.value : [];

        renderWordOfDay();
        renderCurrentView();
    } catch (err) {
        console.error("Data load error", err);
    }
    toggleLoader(false);
}

function renderWordOfDay() {
    const container = document.getElementById('word-of-day-container');
    const wod = state.data.wordOfDay;
    if (!wod) { container.innerHTML = ''; return; }
    
    const mKey = state.region === 'BD' ? 'bangla_meaning' : 'hindi_meaning';
    container.innerHTML = `
        <div class="word-of-day">
            <h3>Word of the Day</h3>
            <div class="word">${wod.word}</div>
            <div class="phonetic">${wod.phonetic} <small>${wod.part_of_speech}</small></div>
            <div class="meaning">${wod[mKey]}</div>
        </div>`;
}

function renderCurrentView() {
    const container = document.getElementById('main-content');
    if (state.view === 'articles') {
        container.innerHTML = state.data.articles.map(a => `<div class="article-item"><h2>${a.title}</h2><p>${a.description}</p></div>`).join('');
    } else if (state.view === 'vocab') {
        container.innerHTML = state.data.vocab.map(v => {
            const [word, mean] = v.split(' : ');
            return `<div class="vocab-item"><div class="vocab-word">${word}</div><div class="vocab-meaning">${mean}</div></div>`;
        }).join('');
    } else {
        container.innerHTML = `<div class="quiz-container"><h3>Quiz</h3><p>${state.data.quiz.length} Questions available for today.</p></div>`;
    }
}

function toggleLoader(s) { document.getElementById('loader').style.display = s ? 'block' : 'none'; }

window.onload = init;