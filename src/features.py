# src/features.py
"""
features.py
Utilities: lexical feature extraction for URLs and char-level tokenizer/sequence helpers.
Safe: purely feature extraction for classification (no networking or harmful actions).
"""

import re
import math
from urllib.parse import urlparse
import tldextract
import numpy as np

# ----- Basic helpers -----
def has_ip(url: str) -> bool:
    """Return True if hostname is an IPv4 address."""
    try:
        host = urlparse(url).hostname or ""
        return bool(re.match(r'^\d{1,3}(\.\d{1,3}){3}$', host))
    except Exception:
        return False

def entropy(s: str) -> float:
    """Shannon entropy for a string."""
    if not s:
        return 0.0
    counts = {}
    for ch in s:
        counts[ch] = counts.get(ch, 0) + 1
    probs = [c / len(s) for c in counts.values()]
    e = -sum(p * math.log2(p) for p in probs)
    return float(e)

# ----- Lexical feature extraction -----
def extract_lexical_features(url: str) -> dict:
    """Return a dictionary of lexical features for a given URL string.
    Designed to be stable and deterministic.
    """
    u = (url or "").strip()
    parsed = urlparse(u)
    domain = parsed.netloc or ""
    path = parsed.path or ""
    query = parsed.query or ""

    # Use tldextract to parse domain pieces
    ext = tldextract.extract(u)
    tld = ext.suffix or ""
    subdomain = ext.subdomain or ""
    domain_name = ext.domain or ""

    # Basic counts and presence features
    features = {
        "url_length": len(u),
        "host_length": len(domain),
        "path_length": len(path),
        "query_length": len(query),
        "count_digits": sum(1 for c in u if c.isdigit()),
        "count_hyphen": u.count("-"),
        "count_at": u.count("@"),
        "count_percent": u.count("%"),
        "count_question": u.count("?"),
        "count_equals": u.count("="),
        "count_slash": u.count("/"),
        "num_dots": u.count("."),
        "has_ip": 1 if has_ip(u) else 0,
        "entropy": entropy(u),
        "tld_len": len(tld),
        "subdomain_len": len(subdomain),
        "domain_len": len(domain_name),
        "uses_https": 1 if parsed.scheme == "https" else 0
    }
    return features

# ----- Char-level tokenizer & sequence helpers for LSTM -----
try:
    from tensorflow.keras.preprocessing.text import Tokenizer  # type: ignore
    from tensorflow.keras.preprocessing.sequence import pad_sequences  # type: ignore
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    Tokenizer = None
    pad_sequences = None

def build_char_tokenizer(urls, num_chars=None):
    """Return a Keras char-level tokenizer fitted on the given list of URLs."""
    if not TENSORFLOW_AVAILABLE:
        raise ImportError("TensorFlow is required for char tokenizer. Install with: pip install tensorflow")
    tok = Tokenizer(char_level=True, oov_token="[OOV]")
    tok.fit_on_texts(urls)
    if num_chars:
        # Optionally trim tokenizer vocabulary size (not altering tok.word_index here,
        # but you can manage vocab when embedding)
        pass
    return tok

def url_to_seq(tok, url, maxlen=200):
    """Convert single URL to a padded char-level sequence using a fitted tokenizer."""
    if not TENSORFLOW_AVAILABLE:
        raise ImportError("TensorFlow is required for url_to_seq. Install with: pip install tensorflow")
    seq = tok.texts_to_sequences([url])
    seq = pad_sequences(seq, maxlen=maxlen, padding="post", truncating="post")
    return seq
