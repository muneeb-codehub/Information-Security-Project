import joblib
import json
import numpy as np

# Load trained model and scaler
model = joblib.load("lightgbm_url_model.pkl")
scaler = joblib.load("scaler.pkl")

print("Exporting model to JSON format...")

# Export model structure and parameters
# model is a Booster object from lgb.train(), so use dump_model() directly
model_json = {
    "model": model.dump_model(),
    "scaler_mean": scaler.mean_.tolist(),
    "scaler_scale": scaler.scale_.tolist()
}

# Save to JSON file
with open("extension/model_export.json", "w") as f:
    json.dump(model_json, f, indent=2)

print("✓ Export complete → extension/model_export.json")
print(f"  - Model trees: {model.num_trees()}")
print(f"  - Feature count: {len(scaler.mean_)}")
print(f"  - Scaler mean: {scaler.mean_[:5]}... (first 5)")
print(f"  - Scaler scale: {scaler.scale_[:5]}... (first 5)")
