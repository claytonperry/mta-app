/* MTA Arrival Board — frontend logic */

const REFRESH_INTERVAL = (window.MTA_REFRESH_INTERVAL || 30) * 1000;

// Line colors matching CSS variables — used for inline badge styling
const LINE_COLORS = {
    "1": "#ee352e", "2": "#ee352e", "3": "#ee352e",
    "4": "#00933c", "5": "#00933c", "6": "#00933c",
    "7": "#b933ad",
    "A": "#0039a6", "C": "#0039a6", "E": "#0039a6",
    "B": "#ff6319", "D": "#ff6319", "F": "#ff6319", "M": "#ff6319",
    "G": "#6cbe45",
    "J": "#996633", "Z": "#996633",
    "L": "#a7a9ac",
    "N": "#fccc0a", "Q": "#fccc0a", "R": "#fccc0a", "W": "#fccc0a",
    "S": "#808183",
};

function lineBadge(line) {
    const color = LINE_COLORS[line] || "#666";
    // N/Q/R/W bullets use dark text
    const textColor = ["N", "Q", "R", "W"].includes(line) ? "#000" : "#fff";
    return `<span class="line-badge" style="background:${color};color:${textColor}">${line}</span>`;
}

function formatMinutes(min) {
    if (min <= 0) return `<span class="time now">NOW</span>`;
    return `<span class="time">${min} min</span>`;
}

function renderArrivals(arrivals) {
    if (!arrivals.length) {
        return `<div class="no-trains">No trains</div>`;
    }
    return arrivals.map(a =>
        `<div class="arrival">
            ${lineBadge(a.line)}
            <span class="dest">${a.destination || ""}</span>
            ${formatMinutes(a.minutes_away)}
        </div>`
    ).join("");
}

function renderStation(station) {
    const badges = station.lines.map(l => lineBadge(l)).join("");
    return `
        <div class="station">
            <div class="station-header">
                <div class="line-badges">${badges}</div>
                <div class="station-name">${station.name}</div>
            </div>
            <div class="directions">
                <div class="direction">
                    <div class="direction-label">Manhattan-bound</div>
                    ${renderArrivals(station.northbound)}
                </div>
                <div class="direction">
                    <div class="direction-label">Brooklyn / Queens</div>
                    ${renderArrivals(station.southbound)}
                </div>
            </div>
        </div>
    `;
}

async function fetchAndRender() {
    const container = document.getElementById("stations");
    try {
        const resp = await fetch("/api/arrivals");
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
        const data = await resp.json();
        container.setAttribute("data-count", data.length);
        container.innerHTML = data.map(renderStation).join("");
    } catch (err) {
        container.innerHTML = `<div class="status error">Error fetching data: ${err.message}</div>`;
    }
}

function updateClock() {
    const el = document.getElementById("clock");
    if (!el) return;
    const now = new Date();
    el.textContent = now.toLocaleTimeString("en-US", {
        hour: "numeric",
        minute: "2-digit",
        second: "2-digit",
    });
}

// Init
document.addEventListener("DOMContentLoaded", () => {
    fetchAndRender();
    setInterval(fetchAndRender, REFRESH_INTERVAL);

    updateClock();
    setInterval(updateClock, 1000);
});
