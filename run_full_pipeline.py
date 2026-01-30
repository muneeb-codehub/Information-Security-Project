"""
run_full_pipeline.py
Complete pipeline: prepare data → merge → train → evaluate → export
"""
import subprocess
import sys

def run_script(script_name, description):
    print("\n" + "="*70)
    print(f"📌 {description}")
    print("="*70)
    result = subprocess.run([sys.executable, script_name], capture_output=False)
    if result.returncode != 0:
        print(f"❌ Error running {script_name}")
        return False
    return True

print("""
╔══════════════════════════════════════════════════════════════════╗
║         SafeBrowse-AI Full Training Pipeline                     ║
║         Preparing 1M+ URLs for Accurate Phishing Detection       ║
╚══════════════════════════════════════════════════════════════════╝
""")

# Step 1: Prepare benign dataset
if not run_script("prepare_benign_dataset.py", "Step 1/5: Preparing benign URLs from Tranco"):
    sys.exit(1)

# Step 2: Merge datasets
if not run_script("merge_datasets.py", "Step 2/5: Merging phishing + benign datasets"):
    sys.exit(1)

# Step 3: Train model
if not run_script("train_lightgbm.py", "Step 3/5: Training LightGBM model (this may take several minutes)"):
    sys.exit(1)

# Step 4: Evaluate model
if not run_script("evaluate.py", "Step 4/5: Evaluating model performance"):
    sys.exit(1)

# Step 5: Export model
if not run_script("export_model.py", "Step 5/5: Exporting model for browser extension"):
    sys.exit(1)

print("\n" + "="*70)
print("✅ PIPELINE COMPLETE!")
print("="*70)
print("""
Next steps:
1. Reload your browser extension (brave://extensions/)
2. Test with google.com - should now show 0% risk
3. Test with suspicious URLs - should detect properly

Your model is now trained on 1M+ URLs and ready for production! 🚀
""")
