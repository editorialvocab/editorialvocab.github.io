// Configuration - Replace with your actual GitLab Raw URL base
const GITLAB_BASE_URL = "https://gitlab.com/Mahadi07/rtejhs/-/raw/main/";

const state = {
    userRegion: 'IN', // Default: India
    source: 'The Hindu',
    contentType: 'editorial' // or 'vocabulary'
};

async function initApp() {
    await detectLocation();
    loadContent();
    
    // Tab Listeners
    document.getElementById('tab-editorial').addEventListener('click', () => switchTab('editorial'));
    document.getElementById('tab-vocabulary').addEventListener('click', () => switchTab('vocabulary'));
}

async function detectLocation() {
    const statusEl = document.getElementById('region-status');
    try {
        const response = await fetch('https://ipapi.co/json/');
        const data = await response.json();
        
        if (data.country_code === 'BD') {
            state.userRegion = 'BD';
            state.source = 'Daily Star';
        } else {
            state.userRegion = 'IN';
            state.source = 'The Hindu';
        }
        statusEl.innerText = `Source: ${state.source} (${data.country_name})`;
    } catch (error) {
        console.error("Location detection failed", error);
        statusEl.innerText = "Source: The Hindu (Default)";
    }
}

async function loadContent() {
    const loader = document.getElementById('content-loader');
    const view = document.getElementById('content-view');
    
    loader.style.display = 'block';
    view.innerHTML = '';

    // Construct file path based on region and type
    // Example path: data/BD/editorial.md
    const fileName = `${state.userRegion}/${state.contentType}.md`;
    const fullUrl = `${GITLAB_BASE_URL}${fileName}`;

    try {
        const response = await fetch(fullUrl);
        const markdown = await response.text();
        view.innerHTML = marked.parse(markdown);
    } catch (error) {
        view.innerHTML = `<p style="color:red">Failed to load content from GitLab. Please check your path: ${fullUrl}</p>`;
    } finally {
        loader.style.display = 'none';
    }
}

function switchTab(type) {
    if (state.contentType === type) return;

    state.contentType = type;

    // Update UI Buttons
    document.getElementById('tab-editorial').classList.toggle('active', type === 'editorial');
    document.getElementById('tab-vocabulary').classList.toggle('active', type === 'vocabulary');

    // Reload data
    loadContent();
}

window.onload = initApp;