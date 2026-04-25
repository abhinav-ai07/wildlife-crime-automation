// Wildlife Crime Intelligence System - Enhanced Frontend Logic

document.addEventListener('DOMContentLoaded', () => {
    // Initial data fetch
    fetchData();

    // Event Listeners
    const runBtn = document.getElementById('runPipelineBtn');
    if (runBtn) {
        runBtn.addEventListener('click', runPipeline);
    }

    // Scroll Logic
    window.addEventListener('scroll', handleScroll);
    setupScrollAnimations();
    highlightNavOnScroll();
});

// --- API Integration ---

async function fetchData() {
    const container = document.getElementById('dataContainer');
    
    try {
        const response = await fetch('/data');
        if (!response.ok) throw new Error('Failed to fetch data');
        
        const data = await response.json();
        renderData(data);
        updateStats(data);
    } catch (error) {
        console.error('Error:', error);
        container.innerHTML = `<div style="grid-column: 1/-1; text-align: center; color: #ef4444; padding: 40px;">
            <p>Intelligence server connection lost. Retrying...</p>
        </div>`;
    }
}

async function runPipeline() {
    const btn = document.getElementById('runPipelineBtn');
    const spinner = document.getElementById('spinner');
    const statusMsg = document.getElementById('statusMessage');

    // UI State: Loading
    btn.disabled = true;
    btn.innerText = 'Initializing Pipeline...';
    spinner.style.display = 'block';
    statusMsg.innerText = 'Connecting to extraction engine...';

    try {
        const response = await fetch('/run-pipeline');
        const result = await response.json();

        if (result.status === 'started') {
            statusMsg.innerText = 'Pipeline operating in background';
            btn.innerText = 'System Running';
            pollForData();
        } else if (result.status === 'already_running') {
            statusMsg.innerText = 'Intelligence cycle already active';
            btn.innerText = 'System Busy';
        }
    } catch (error) {
        statusMsg.innerText = 'Critical link failure';
    } finally {
        setTimeout(() => {
            btn.disabled = false;
            btn.innerText = 'Run Intelligence Pipeline';
            spinner.style.display = 'none';
        }, 5000);
    }
}

function pollForData() {
    let attempts = 0;
    const interval = setInterval(async () => {
        attempts++;
        await fetchData();
        if (attempts >= 12) clearInterval(interval);
    }, 10000); 
}

// --- UI Rendering ---

function renderData(items) {
    const container = document.getElementById('dataContainer');
    if (!items || items.length === 0) {
        container.innerHTML = '<p style="grid-column: 1/-1; text-align: center; padding: 60px;">Awaiting intelligence reports...</p>';
        return;
    }

    container.innerHTML = '';
    items.forEach((item, index) => {
        const card = document.createElement('div');
        card.className = 'data-card reveal';
        
        card.innerHTML = `
            <div class="tags">
                <span class="tag tag-crime">${item.crime_type || 'INCIDENT'}</span>
                <span class="tag tag-species">${item.species || 'GENERIC'}</span>
            </div>
            <h3>${item.title}</h3>
            <div class="tag tag-location" style="display:block; width:fit-content; margin-bottom: 10px;">📍 ${item.location || 'Global'}</div>
            <div class="card-footer">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span>📅 ${item.published}</span>
                    <span style="font-weight: 700; color: var(--primary-color);">Accused: ${item.accused_count || '0'}</span>
                </div>
            </div>
            <a href="${item.link}" target="_blank" style="display:inline-block; margin-top:20px; color:#2d6a4f; text-decoration:none; font-weight:700; font-size:0.9rem; letter-spacing:0.02em;">VIEW FULL INTEL →</a>
        `;
        container.appendChild(card);
    });

    // Re-run intersection observer for new cards
    setupScrollAnimations();
}

function updateStats(data) {
    if (!data || data.length === 0) return;

    animateValue('statTotal', 0, data.length, 1000);
    
    const speciesCount = new Set(data.map(i => i.species).filter(Boolean)).size;
    animateValue('statSpecies', 0, speciesCount, 1000);

    const locationCount = new Set(data.map(i => i.location).filter(Boolean)).size;
    animateValue('statLocations', 0, locationCount, 1000);
}

function animateValue(id, start, end, duration) {
    const obj = document.getElementById(id);
    if (!obj) return;
    let startTimestamp = null;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        obj.innerHTML = Math.floor(progress * (end - start) + start);
        if (progress < 1) {
            window.requestAnimationFrame(step);
        }
    };
    window.requestAnimationFrame(step);
}

// --- UX Utilities ---

function handleScroll() {
    const nav = document.querySelector('nav');
    if (window.scrollY > 50) {
        nav.classList.add('scrolled');
    } else {
        nav.classList.remove('scrolled');
    }
}

function setupScrollAnimations() {
    const reveals = document.querySelectorAll('.reveal');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('active');
            }
        });
    }, { threshold: 0.1 });

    reveals.forEach(reveal => observer.observe(reveal));
}

function highlightNavOnScroll() {
    const sections = document.querySelectorAll('section, header');
    const navLinks = document.querySelectorAll('.nav-links a');

    window.addEventListener('scroll', () => {
        let current = "";
        sections.forEach((section) => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.clientHeight;
            if (window.scrollY >= sectionTop - 150) {
                current = section.getAttribute("id") || "";
            }
        });

        navLinks.forEach((a) => {
            a.classList.remove("active");
            if (a.getAttribute("href").includes(current)) {
                a.classList.add("active");
            }
        });
    });
}

function scrollToSection(id) {
    const element = document.getElementById(id);
    if (element) {
        window.scrollTo({
            top: element.offsetTop - 80,
            behavior: 'smooth'
        });
    }
}
