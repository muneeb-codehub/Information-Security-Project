from src.features import extract_lexical_features
import json

# Test with the exact Google URL you got
url = "https://www.google.com/?zx=1765289896187&no_sw_cr=1"

features = extract_lexical_features(url)

print("Python Feature Extraction for Google URL:")
print(json.dumps(features, indent=2))
print("\nFeature values as array:")
print(list(features.values()))
