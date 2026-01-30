/**
 * popup.js
 * Displays current tab's safety status in extension popup
 */

document.addEventListener('DOMContentLoaded', async () => {
    const content = document.getElementById('content');

    try {
        // Get current tab
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        
        if (!tab || !tab.id) {
            showError("Unable to access current tab");
            return;
        }

        // Check if it's a special URL
        if (tab.url.startsWith("chrome://") || 
            tab.url.startsWith("chrome-extension://") ||
            tab.url.startsWith("about:")) {
            showInfo("This page cannot be analyzed (system page)");
            return;
        }

        // Get stored analysis result
        const result = await chrome.storage.local.get([tab.id.toString()]);
        const data = result[tab.id.toString()];

        if (data && data.score !== undefined) {
            displayResult(data.url, data.score);
        } else {
            showInfo("No analysis available yet. Please refresh the page.");
        }

    } catch (error) {
        console.error("Popup error:", error);
        showError("An error occurred while loading results");
    }
});

function displayResult(url, score) {
    const content = document.getElementById('content');
    
    // Determine risk level
    let statusClass, statusTitle, statusText, scoreClass;
    
    if (score < 0.3) {
        statusClass = 'safe';
        statusTitle = '✓ Safe';
        statusText = 'This website appears to be legitimate.';
        scoreClass = 'safe';
    } else if (score < 0.5) {
        statusClass = 'warning';
        statusTitle = '⚠ Caution';
        statusText = 'This website shows some suspicious indicators.';
        scoreClass = 'warning';
    } else {
        statusClass = 'danger';
        statusTitle = '⛔ Danger';
        statusText = 'This website is likely a phishing attempt!';
        scoreClass = 'danger';
    }

    content.innerHTML = `
        <div class="status ${statusClass}">
            <div class="status-title">${statusTitle}</div>
            <div class="status-text">${statusText}</div>
        </div>
        
        <div class="score ${scoreClass}">
            Risk: ${(score * 100).toFixed(1)}%
        </div>
        
        <div class="url-display">
            ${sanitizeHTML(url)}
        </div>
        
        <div class="info">
            Powered by LightGBM ML Model<br>
            SafeBrowse AI v1.0
        </div>
    `;
}

function showInfo(message) {
    const content = document.getElementById('content');
    content.innerHTML = `
        <div class="status warning">
            <div class="status-text">${message}</div>
        </div>
    `;
}

function showError(message) {
    const content = document.getElementById('content');
    content.innerHTML = `
        <div class="status danger">
            <div class="status-title">Error</div>
            <div class="status-text">${message}</div>
        </div>
    `;
}

function sanitizeHTML(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}
