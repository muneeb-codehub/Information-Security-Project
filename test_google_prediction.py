import joblib
import pandas as pd
from src.features import extract_lexical_features

# Load model and scaler
model = joblib.load("lightgbm_url_model.pkl")
scaler = joblib.load("scaler.pkl")

# Test Google URL
url = "https://www.google.com/?zx=1765289896187&no_sw_cr=1"

features = extract_lexical_features(url)
X = pd.DataFrame([features])

# Scale
X_scaled = scaler.transform(X)

# Predict
prediction = model.predict(X_scaled)[0]

print(f"URL: {url}")
print(f"Python Model Prediction: {prediction:.4f}")
print(f"Classification: {'PHISHING' if prediction > 0.5 else 'BENIGN'}")
print(f"\nScaled features: {X_scaled[0][:5]}... (first 5)")
