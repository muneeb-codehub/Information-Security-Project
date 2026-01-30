import pandas as pd
import numpy as np
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from src.features import extract_lexical_features
import joblib

# -------------------------
# 1. Load dataset
# -------------------------
print("Loading dataset...")
df = pd.read_csv("data/dataset_final.csv")  # merged dataset with 1M benign + phishing

print(f"Dataset size: {len(df)} URLs")
print(f"  Benign (0): {len(df[df['label'] == 0])}")
print(f"  Phishing (1): {len(df[df['label'] == 1])}")

urls = df["url"].values
labels = df["label"].values  # 0 = benign, 1 = phishing

# -------------------------
# 2. Extract lexical features
# -------------------------
print("\nExtracting features from URLs...")
feature_list = []
total_urls = len(urls)
for idx, u in enumerate(urls):
    if (idx + 1) % 10000 == 0:
        print(f"  Processed {idx + 1}/{total_urls} URLs...")
    feature_list.append(extract_lexical_features(u))

print(f"✓ Extracted features from {len(feature_list)} URLs")
lexical_matrix = pd.DataFrame(feature_list)

# -------------------------
# 3. Normalize numeric features
# -------------------------
scaler = StandardScaler()
X_scaled = scaler.fit_transform(lexical_matrix)

# -------------------------
# 4. Train-test split
# -------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, labels, test_size=0.2, random_state=42
)

# -------------------------
# 5. LightGBM model
# -------------------------
print("\nTraining LightGBM model...")
params = {
    "objective": "binary",
    "boosting_type": "gbdt",
    "learning_rate": 0.05,
    "num_leaves": 64,  # Increased for larger dataset
    "max_depth": 10,
    "metric": "binary_logloss",
    "feature_fraction": 0.8,
    "bagging_fraction": 0.8,
    "bagging_freq": 5,
    "verbose": -1
}

train_data = lgb.Dataset(X_train, label=y_train)
test_data = lgb.Dataset(X_test, label=y_test)

model = lgb.train(
    params,
    train_data,
    valid_sets=[train_data, test_data],
    num_boost_round=300,
    callbacks=[lgb.log_evaluation(period=20)]
)

print("\n✓ Training complete!")

# -------------------------
# 6. Save model + scaler
# -------------------------
joblib.dump(model, "lightgbm_url_model.pkl")
joblib.dump(scaler, "scaler.pkl")

print("Model training complete. Saved as lightgbm_url_model.pkl")
