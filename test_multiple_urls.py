import joblib
import pandas as pd
from src.features import extract_lexical_features

# Load model and scaler
model = joblib.load("lightgbm_url_model.pkl")
scaler = joblib.load("scaler.pkl")

# Test multiple URLs
test_urls = [
    "https://www.google.com",
    "https://www.youtube.com",
    "https://www.facebook.com",
    "https://www.github.com",
    "http://phishing-test-example.com",
    "http://192.168.0.1",
]

print("="*70)
print("Testing Multiple URLs")
print("="*70)

for url in test_urls:
    features = extract_lexical_features(url)
    X = pd.DataFrame([features])
    X_scaled = scaler.transform(X)
    prediction = model.predict(X_scaled)[0]
    
    classification = "⚠️  PHISHING" if prediction > 0.5 else "✅ BENIGN"
    print(f"{classification} | Score: {prediction:.4f} | {url}")

print("="*70)
