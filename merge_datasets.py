"""
merge_datasets.py
Combines phishing URLs with benign URLs and balances the dataset
"""
import pandas as pd

print("Step 1: Loading phishing dataset...")
phish_df = pd.read_csv("data/url_phish.csv")
# Keep only url and label columns
phish_df = phish_df[["url", "label"]]
print(f"  Phishing URLs: {len(phish_df[phish_df['label'] == 1])}")
print(f"  Benign URLs: {len(phish_df[phish_df['label'] == 0])}")

print("\nStep 2: Loading Tranco benign dataset...")
benign_df = pd.read_csv("data/benign_1m.csv")
print(f"  Loaded {len(benign_df)} benign URLs from Tranco")

print("\nStep 3: Combining datasets...")
# Combine all data
combined_df = pd.concat([phish_df, benign_df], ignore_index=True)

print(f"\nDataset Statistics:")
print(f"  Total URLs: {len(combined_df)}")
print(f"  Benign (label=0): {len(combined_df[combined_df['label'] == 0])}")
print(f"  Phishing (label=1): {len(combined_df[combined_df['label'] == 1])}")
print(f"  Ratio: {len(combined_df[combined_df['label'] == 0]) / len(combined_df[combined_df['label'] == 1]):.2f}:1 (benign:phishing)")

print("\nStep 4: Shuffling dataset...")
combined_df = combined_df.sample(frac=1, random_state=42).reset_index(drop=True)

print("\nStep 5: Saving final dataset...")
combined_df.to_csv("data/dataset_final.csv", index=False)

print(f"✓ Saved {len(combined_df)} URLs to data/dataset_final.csv")
print("\nSample from final dataset:")
print(combined_df.head(10))
print("\nDataset is ready for training!")
