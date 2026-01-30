/**
 * feature_extractor.js
 * Extracts 17 lexical features from URLs (mirrors Python implementation)
 */

export function extractFeatures(url) {
    try {
        const u = new URL(url);
        const host = u.hostname || "";
        const path = u.pathname || "";
        const query = u.search || "";
        const full = url;

        // Parse domain components
        const parts = host.split(".");
        const tld = parts.length > 0 ? parts[parts.length - 1] : "";
        const domain = parts.length > 1 ? parts[parts.length - 2] : host;
        const subdomain = parts.length > 2 ? parts.slice(0, -2).join(".") : "";

        return {
            url_length: full.length,
            host_length: host.length,
            path_length: path.length,
            query_length: query.length,
            count_digits: (full.match(/[0-9]/g) || []).length,
            count_hyphen: (full.match(/-/g) || []).length,
            count_at: (full.match(/@/g) || []).length,
            count_percent: (full.match(/%/g) || []).length,
            count_question: (full.match(/\?/g) || []).length,
            count_equals: (full.match(/=/g) || []).length,
            count_slash: (full.match(/\//g) || []).length,
            num_dots: (full.match(/\./g) || []).length,
            has_ip: /^[0-9.]+$/.test(host) ? 1 : 0,
            entropy: computeEntropy(full),
            tld_len: tld.length,
            subdomain_len: subdomain.length,
            domain_len: domain.length,
            uses_https: url.startsWith("https") ? 1 : 0
        };
    } catch (e) {
        console.error("Feature extraction error:", e);
        return null;
    }
}

function computeEntropy(str) {
    if (!str) return 0;
    
    const map = {};
    for (let ch of str) {
        map[ch] = (map[ch] || 0) + 1;
    }

    let entropy = 0;
    const len = str.length;
    for (let ch in map) {
        const p = map[ch] / len;
        entropy -= p * Math.log2(p);
    }
    return entropy;
}
