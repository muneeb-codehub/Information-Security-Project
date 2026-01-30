import pandas as pd
import joblib
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from src.features import extract_lexical_features

# Load trained model and scaler
model = joblib.load("lightgbm_url_model.pkl")
scaler = joblib.load("scaler.pkl")

# Load dataset
print("Loading dataset...")
df = pd.read_csv("data/dataset_final.csv")

print(f"Dataset size: {len(df)} URLs")
print(f"  Benign (0): {len(df[df['label'] == 0])}")
print(f"  Phishing (1): {len(df[df['label'] == 1])}")

urls = df["url"].values
labels = df["label"].values

# Extract features
print("Extracting features...")
features = [extract_lexical_features(u) for u in urls]
X = pd.DataFrame(features)

# Scale features
X_scaled = scaler.transform(X)

# Predict
print("Making predictions...")
preds = model.predict(X_scaled)
preds = (preds >= 0.5).astype(int)

# Evaluation metrics
print("\n" + "="*50)
print("MODEL EVALUATION RESULTS")
print("="*50)
print(f"\nAccuracy: {accuracy_score(labels, preds):.4f}")
print("\nClassification Report:")
print(classification_report(labels, preds, target_names=['Benign', 'Phishing']))
print("\nConfusion Matrix:")
print(confusion_matrix(labels, preds))
print("="*50)
