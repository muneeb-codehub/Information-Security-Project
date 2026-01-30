/**
 * background.js
 * Service worker for SafeBrowse AI extension
 * Monitors tab updates and classifies URLs using LightGBM model
 */

import { extractFeatures } from "./feature_extractor.js";

let modelData = null;
let isModelLoaded = false;

// Whitelist of known-safe domains (to prevent false positives)
const SAFE_DOMAINS = new Set([
    'google.com', 'youtube.com', 'facebook.com', 'twitter.com', 'instagram.com',
    'linkedin.com', 'amazon.com', 'ebay.com', 'wikipedia.org', 'reddit.com',
    'github.com', 'stackoverflow.com', 'microsoft.com', 'apple.com', 'netflix.com',
    'yahoo.com', 'bing.com', 'paypal.com', 'dropbox.com', 'zoom.us'
]);

// Protected brands - detect typosquatting attempts
const PROTECTED_BRANDS = [
    'paypal', 'google', 'facebook', 'amazon', 'microsoft', 'apple', 
    'netflix', 'instagram', 'twitter', 'linkedin', 'youtube', 'github',
    'dropbox', 'spotify', 'ebay', 'walmart', 'target', 'bestbuy'
];

// Load model on extension startup
loadModel();

// Levenshtein distance for typo detection
function levenshteinDistance(str1, str2) {
    const len1 = str1.length;
    const len2 = str2.length;
    const matrix = Array(len1 + 1).fill(null).map(() => Array(len2 + 1).fill(0));
    
    for (let i = 0; i <= len1; i++) matrix[i][0] = i;
    for (let j = 0; j <= len2; j++) matrix[0][j] = j;
    
    for (let i = 1; i <= len1; i++) {
        for (let j = 1; j <= len2; j++) {
            const cost = str1[i - 1] === str2[j - 1] ? 0 : 1;
            matrix[i][j] = Math.min(
                matrix[i - 1][j] + 1,      // deletion
                matrix[i][j - 1] + 1,      // insertion
                matrix[i - 1][j - 1] + cost // substitution
            );
        }
    }
    return matrix[len1][len2];
}

async function loadModel() {
    try {
        const response = await fetch(chrome.runtime.getURL("model_export.json"));
        modelData = await response.json();
        isModelLoaded = true;
        console.log("✓ SafeBrowse AI model loaded successfully");
    } catch (error) {
        console.error("Failed to load model:", error);
    }
}

// Monitor tab updates
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.status !== "complete" || !isModelLoaded || !tab.url) return;
    
    // Skip internal/extension URLs
    if (tab.url.startsWith("chrome://") || 
        tab.url.startsWith("chrome-extension://") ||
        tab.url.startsWith("about:")) {
        return;
    }

    analyzeURL(tab.url, tabId);
});

// Also check when tab becomes active
chrome.tabs.onActivated.addListener(async (activeInfo) => {
    if (!isModelLoaded) return;
    
    const tab = await chrome.tabs.get(activeInfo.tabId);
    if (tab.url && !tab.url.startsWith("chrome://") && 
        !tab.url.startsWith("chrome-extension://")) {
        analyzeURL(tab.url, activeInfo.tabId);
    }
});

function analyzeURL(url, tabId) {
    try {
        // Extract features
        const features = extractFeatures(url);
        if (!features) return;

        // Check whitelist first (bypass ML for known-safe domains)
        const hostname = new URL(url).hostname.toLowerCase();
        const domain = hostname.replace(/^www\./, ''); // Remove www.
        
        console.log(`🔍 Analyzing domain: "${domain}"`);
        
        // TYPOSQUATTING DETECTION: Check for brand impersonation
        let typosquattingDetected = false;
        for (const brand of PROTECTED_BRANDS) {
            // Extract base domain (before first dot) and clean it
            const baseDomain = domain.split('.')[0].toLowerCase();
            // Remove hyphens and numbers for comparison
            const cleanBase = baseDomain.replace(/[-\d]/g, '');
            
            // Check if domain contains brand or is very similar
            const containsBrand = domain.includes(brand);
            const similarToClean = levenshteinDistance(cleanBase, brand) <= 2;
            const similarToBase = levenshteinDistance(baseDomain, brand) <= 2;
            
            if ((containsBrand || similarToClean || similarToBase) && !SAFE_DOMAINS.has(domain)) {
                console.log(`🔎 Brand: ${brand} | Base: ${baseDomain} | Clean: ${cleanBase} | Similar: ${similarToClean || similarToBase}`); // DEBUG
                
                // Check for suspicious patterns indicating phishing
                const hasSuspiciousKeywords = domain.includes('secure') || domain.includes('login') || 
                                             domain.includes('verify') || domain.includes('account') ||
                                             domain.includes('update') || domain.includes('confirm');
                const hasHyphens = domain.includes('-');
                const hasDigits = baseDomain.match(/\d/);
                const isLongDomain = baseDomain.length > brand.length + 3;
                
                if (hasSuspiciousKeywords || hasHyphens || hasDigits || isLongDomain) {
                    typosquattingDetected = true;
                    console.log(`⚠️ TYPOSQUATTING DETECTED: ${url} (impersonating ${brand})`);
                    
                    showWarning(url, 0.99, tabId); // Force high score
                    chrome.storage.local.set({
                        [tabId]: {
                            url: url,
                            score: 0.99,
                            reason: `Suspected ${brand} impersonation`,
                            timestamp: Date.now()
                        }
                    });
                    return;
                }
            }
        }
        
        if (SAFE_DOMAINS.has(domain) || Array.from(SAFE_DOMAINS).some(d => hostname.endsWith(d))) {
            console.log(`✓ Whitelisted: ${url.substring(0, 50)}... | Score: 0.000 (safe domain)`);
            
            // Store as safe
            chrome.storage.local.set({
                [tabId]: {
                    url: url,
                    score: 0.0,
                    timestamp: Date.now()
                }
            });
            return;
        }

        // Scale features
        const scaledFeatures = scaleFeatures(features, modelData.scaler_mean, modelData.scaler_scale);

        // Predict using LightGBM
        const score = predictLightGBM(modelData.model, scaledFeatures);

        console.log(`URL: ${url.substring(0, 50)}... | Phishing Score: ${score.toFixed(3)}`);

        // Alert if suspicious (score > 0.5)
        if (score > 0.5) {
            showWarning(url, score, tabId);
        }

        // Store result for popup
        chrome.storage.local.set({
            [tabId]: {
                url: url,
                score: score,
                timestamp: Date.now()
            }
        });

    } catch (error) {
        console.error("Analysis error:", error);
    }
}

function scaleFeatures(featuresObj, meanArr, scaleArr) {
    const vals = Object.values(featuresObj);
    return vals.map((v, i) => (v - meanArr[i]) / scaleArr[i]);
}

function predictLightGBM(model, features) {
    // Simple LightGBM inference from dump_model
    // This is a placeholder - actual implementation would traverse the tree structure
    // For now, using a simplified approach
    
    const trees = model.tree_info || [];
    let totalScore = 0;

    // For each tree, traverse and sum predictions
    for (let tree of trees) {
        totalScore += traverseTree(tree.tree_structure, features);
    }

    // Apply sigmoid to get probability
    const probability = 1 / (1 + Math.exp(-totalScore));
    return probability;
}

function traverseTree(node, features) {
    if (!node) return 0;

    // Leaf node
    if (node.leaf_value !== undefined) {
        return node.leaf_value;
    }

    // Internal node
    const featureValue = features[node.split_feature];
    const threshold = node.threshold;

    if (featureValue <= threshold) {
        return traverseTree(node.left_child, features);
    } else {
        return traverseTree(node.right_child, features);
    }
}

function showWarning(url, score, tabId) {
    chrome.notifications.create({
        type: "basic",
        iconUrl: "icons/icon48.png",
        title: "⚠️ Phishing Warning",
        message: `This website may be dangerous!\nRisk Score: ${(score * 100).toFixed(1)}%`,
        priority: 2
    });

    // Update badge
    chrome.action.setBadgeText({ text: "!", tabId: tabId });
    chrome.action.setBadgeBackgroundColor({ color: "#FF0000", tabId: tabId });
}
