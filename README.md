# 🛡️ SafeBrowse-AI

**Real-time phishing URL detection system using machine learning and browser extension integration.**

A lightweight, privacy-focused phishing detection system that combines lexical feature analysis with LightGBM classification, deployable as a Chrome/Edge browser extension for real-time protection.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Development Guide](#development-guide)
- [Future Enhancements](#future-enhancements)
- [Contributing](#contributing)

---

## 🎯 Overview

SafeBrowse-AI is a machine learning-based phishing detection system designed for:

- **Real-time protection** - Instant URL analysis in browser
- **Privacy-first** - All processing happens locally
- **Lightweight** - Fast inference with minimal overhead
- **Accurate** - Uses 17 engineered lexical features + LightGBM

### Key Technologies

- **Python** - Model training and evaluation
- **LightGBM** - Gradient boosting classifier
- **JavaScript (ES6)** - Browser extension
- **Chrome Manifest V3** - Modern extension architecture

---

## ✨ Features

### Core Detection Capabilities

-  **17 Lexical Features** extracted from URLs
  - Length metrics (URL, host, path, query)
  - Character frequency analysis
  - IP address detection
  - Shannon entropy calculation
  - TLD/subdomain parsing
  - Protocol analysis (HTTPS)

-  **LightGBM Classifier**
  - Fast gradient boosting
  - High accuracy with low latency
  - Exportable to JSON for browser use

-  **Real-time Browser Extension**
  - Automatic tab monitoring
  - Instant notifications for suspicious sites
  - Visual risk score display
  - No external API calls

---

## 🎯 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    TRAINING PIPELINE                        │
│                                                             │
│  CSV Dataset (phishing_and_benign_urls.csv)                 │
│       ↓                                                     │
│  Feature Extraction (17 lexical features)                   │
│       ↓                                                     │
│  LightGBM Training (300 trees, binary classification)       │
│       ↓                                                     │
│  Model Export (JSON format for browser)                     │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                  BROWSER EXTENSION                          │
│                                                             │
│  User visits URL                                            │
│       ↓                                                     │
│  Tab Update Event (background.js)                           │
│       ↓                                                     │
│  Extract Features (feature_extractor.js)                    │
│       ↓                                                     │
│  Scale Features (using exported scaler)                     │
│       ↓                                                     │
│  LightGBM Inference (tree traversal in JS)                  │
│       ↓                                                     │
│  Risk Score Calculation (0 - 100)                           │
│       ↓                                                     │
│  ├─ Show Warning (if score > 0.5)                           │
│  └─ Update Popup Display                                    │
└─────────────────────────────────────────────────────────────┘
```

---

### Components

1. **Training Pipeline** (`train_lightgbm.py`)
   - Loads phishing/benign URL dataset
   - Extracts 17 lexical features
   - Trains LightGBM classifier
   - Saves model + scaler

2. **Evaluation** (`evaluate.py`)
   - Tests model accuracy
   - Generates classification report
   - Produces a confusion matrix

3. **Model Export** (`export_model.py`)
   - Converts model to JSON
   - Exports scaler parameters
   - Prepares for browser deployment

4. **Browser Extension** (`extension/`)
   - Service worker for monitoring
   - Feature extraction in JavaScript
   - LightGBM inference engine
   - User interface popup

---

## 🚀 Installation

### Prerequisites

- Python 3.8+
- pip package manager
- Chrome or Edge browser
- Dataset: `phishing_and_benign_urls.csv`


### Install Python Dependencies

```bash
pip install pandas numpy scikit-learn lightgbm joblib tldextract
```

### Prepare Dataset

Place your dataset as `data/url_phish.csv` with columns:
- `url` - Full URL string
- `label` - Binary label (0 = benign, 1 = phishing)

---

## 📖 Usage

### 1️⃣ Train the Model

```bash
python train_lightgbm.py
```

**Output:**
- `lightgbm_url_model.pkl` - Trained LightGBM model
- `scaler.pkl` - Feature scaler

### 2️⃣ Evaluate Performance

```bash
python evaluate.py
```

**Example Output:**
```
MODEL EVALUATION RESULTS
==================================================
Accuracy: 0.9542

Classification Report:
              precision    recall  f1-score   support

      Benign       0.96      0.95      0.95     50000
    Phishing       0.95      0.96      0.95     50000

    accuracy                           0.95    100000
   macro avg       0.95      0.95      0.95    100000
weighted avg       0.95      0.95      0.95    100000
```

### 3️⃣ Export Model for Browser

```bash
python export_model.py
```

**Output:**
- `extension/model_export.json` - Model + scaler in JSON format

### 4️⃣ Install Browser Extension

1. Open Chrome/Edge
2. Navigate to `chrome://extensions/`
3. Enable **Developer mode**
4. Click **Load unpacked**
5. Select the `extension/` folder
6. Extension is now active! 🎉

### 5️⃣ Test the Extension

- Visit any website
- Click the SafeBrowse AI icon
- View risk score and safety status
- High-risk sites trigger automatic warnings

---

## 📁 Project Structure

```
safebrowse-ai/
│
├── data/
│   └── url_phish.csv              # Training dataset
│
├── src/
│   └── features.py                # Feature extraction utilities
│
├── extension/
│   ├── manifest.json              # Extension configuration
│   ├── background.js              # Service worker (ML inference)
│   ├── feature_extractor.js       # JS feature extraction
│   ├── popup.html                 # Extension UI
│   ├── popup.js                   # Popup logic
│   ├── model_export.json          # Exported model (generated)
│   ├── icons/                     # Extension icons
│   └── README.md                  # Extension documentation
│
├── train_lightgbm.py              # Model training script
├── evaluate.py                    # Model evaluation script
├── export_model.py                # Model export script
├── test_features.py               # Feature extraction test
│
├── lightgbm_url_model.pkl         # Trained model (generated)
├── scaler.pkl                     # Feature scaler (generated)
│
└── README.md                      # This file
```

---

## 🔧 Development Guide

### Feature Engineering

The system extracts **17 lexical features** from each URL:

| Feature | Description | Example |
|---------|-------------|---------|
| `url_length` | Total URL length | 72 |
| `host_length` | Hostname length | 25 |
| `path_length` | Path length | 12 |
| `query_length` | Query string length | 15 |
| `count_digits` | Number of digits | 8 |
| `count_hyphen` | Number of hyphens | 3 |
| `count_at` | Number of @ symbols | 1 |
| `count_percent` | Number of % symbols | 2 |
| `count_question` | Number of ? symbols | 1 |
| `count_equals` | Number of = symbols | 2 |
| `count_slash` | Number of / symbols | 4 |
| `num_dots` | Number of dots | 5 |
| `has_ip` | Contains IP address? | 0/1 |
| `entropy` | Shannon entropy | 4.23 |
| `tld_len` | TLD length | 3 |
| `subdomain_len` | Subdomain length | 12 |
| `domain_len` | Domain name length | 8 |
| `uses_https` | Uses HTTPS? | 0/1 |

### Adding Custom Features

Edit `src/features.py`:

```python
def extract_lexical_features(url: str) -> dict:
    # ... existing features ...
    
    features["my_custom_feature"] = custom_logic(url)
    
    return features
```

Then update `extension/feature_extractor.js` accordingly.

### Model Tuning

Adjust hyperparameters in `train_lightgbm.py`:

```python
model = lgb.LGBMClassifier(
    n_estimators=300,      # Number of trees
    learning_rate=0.05,    # Learning rate
    max_depth=-1,          # Max tree depth
    num_leaves=64,         # Max leaves per tree
    objective="binary"     # Binary classification
)
```

### Testing Feature Extraction

```bash
python test_features.py
```

Validates that feature extraction works correctly on sample URLs.

---

## 🔮 Future Enhancements

### Planned Features

- [ ] **CNN Character-Level Model**
  - TensorFlow.js integration
  - Character-level sequence analysis
  - Ensemble with LightGBM (60% LGBM + 40% CNN)

- [ ] **Enhanced Detection**
  - Google Safe Browsing API integration
  - SSL certificate validation
  - Domain age checking
  - WHOIS lookup integration

- [ ] **Improved UX**
  - Detailed threat analysis view
  - Whitelist/blacklist management
  - User feedback mechanism
  - Statistics dashboard

- [ ] **Performance**
  - Model compression
  - Lazy loading optimization
  - Background analysis caching

### Research Extensions

- Multi-class classification (phishing types)
- Adversarial robustness testing
- Cross-browser compatibility (Firefox, Safari)
- Mobile browser support

---

## Acknowledgments

- **LightGBM** - Microsoft Research
- **tldextract** - John Kurkowski
- **scikit-learn** - scikit-learn developers
- Chrome Extension API documentation


<div align="center">

[⬆ Back to Top](#-safebrowse-ai)

</div>
