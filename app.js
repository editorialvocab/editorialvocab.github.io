const BASE_URL = "https://gitlab.com/Mahadi07/rtejhs/-/raw/main/EdData/data/";

const state = {
    region: 'IN', // Default
    view: 'articles',
    data: {
        wordOfDay: null,
        vocab: [],
        articles: [],
        quiz: []
    }
};

async function init() {
    await detectLocation();
    setupTabs();
    loadAllData();
}

async function detectLocation() {
    try {
        const res = await fetch('https://ipapi.co/json/');
        const info = await res.json();
        state.region = info.country_code === 'BD' ? 'BD' : 'IN';
        document.getElementById('region-status').innerText = `Source: ${state.region === 'BD' ? 'Daily Star' : 'The Hindu'}`;
    } catch (e) {
        console.log("Location fallback to IN");
    }
}

async function loadAllData() {
    toggleLoader(true);
    try {
        // Fetch common data
        const [wod, vocab, quiz, articles] = await Promise.all([
            fetchJSON('word_of_day.json'),
            fetchJSON('daily_vocab.json'),
            fetchJSON('quiz.json'),
            fetchJSON(`articles_${state.region.toLowerCase()}.json`)
        ]);

        state.data = { wordOfDay: wod, vocab, quiz, articles };
        renderWordOfDay();
        renderCurrentView();
    } catch (err) {
        document.getElementById('main-content').innerHTML = `<div class="error-msg">Error loading JSON data from GitLab.</div>`;
    }
    toggleLoader(false);
}

async function fetchJSON(fileName) {
    const response = await fetch(`${BASE_URL}${fileName}`);
    return await response.json();
}

function renderWordOfDay() {
    const container = document.getElementById('word-of-day-container');
    if (!state.data.wordOfDay) return;
    container.innerHTML = `
        <div class="word-of-day">
            <h3>Word of the Day</h3>
            <div class="word">${state.data.wordOfDay.word}</div>
            <div class="meaning">${state.data.wordOfDay.meaning}</div>
        </div>
    `;
}

function renderCurrentView() {
    const container = document.getElementById('main-content');
    let html = '';

    if (state.view === 'articles') {
        html = state.data.articles.map(art => `
            <div class="article-item">
                <h2>${art.title}</h2>
                <p>${art.description}</p>
            </div>
        `).join('');
    } else if (state.view === 'vocab') {
        html = state.data.vocab.map(v => `
            <div class="vocab-item">
                <div class="vocab-word">${v.word}</div>
                <div class="vocab-meaning">${v.meaning}</div>
            </div>
        `).join('');
    } else if (state.view === 'quiz') {
        html = `<div class="quiz-container"><h3>Quiz feature coming soon!</h3><p>Practice the 10 daily words here.</p></div>`;
    }

    container.innerHTML = html || '<p>No data available.</p>';
}

function setupTabs() {
    const tabs = { 'tab-articles': 'articles', 'tab-vocab': 'vocab', 'tab-quiz': 'quiz' };
    Object.keys(tabs).forEach(id => {
        document.getElementById(id).onclick = (e) => {
            document.querySelectorAll('.tabs button').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            state.view = tabs[id];
            renderCurrentView();
        };
    });
}

function toggleLoader(show) { document.getElementById('loader').style.display = show ? 'block' : 'none'; }
init();