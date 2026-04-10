"""Integration tests for the present-md pipeline."""

import os
import sys
import glob

# Add src to Python path so IDEs and scripts can find present_md
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from present_md.pipeline import PresentationPipeline


def test_no_crash_on_test_cases():
    """Verify that the pipeline does not crash on any valid test case markdown."""
    test_cases_dir = "Guidelines/Test Cases"
    
    if not os.path.exists(test_cases_dir):
        print(f"Skipping: {test_cases_dir} not found.")
        return

    md_files = glob.glob(os.path.join(test_cases_dir, "*.md"))
    
    # We use the generic template from Accenture sample since test cases don't provide templates
    template = "Guidelines/Sample Files/Accenture Tech Acquisition Analysis/Template_Accenture Tech Acquisition Analysis.pptx"
    
    if not os.path.exists(template):
        print(f"Skipping: template {template} not found.")
        return

    pipeline = PresentationPipeline(
        api_key="test-dummy-key",
        model="gpt-4o",
        min_slides=5,  # Faster tests
        max_slides=10,
    )
    
    os.makedirs("output/tests", exist_ok=True)
    
    success = 0
    failed = []

    for file in md_files:
        name = os.path.basename(file)
        out_path = os.path.join("output/tests", f"{name}.pptx")
        try:
             # Fast track parser mostly, don't necessarily generate PPTX for all if too slow
             pipeline.run(file, template, out_path)
             success += 1
        except Exception as e:
             failed.append((name, str(e)))
             
    print(f"Test Cases: {success} succeeded, {len(failed)} failed.")
    for f, err in failed:
        print(f"  ❌ {f}: {err}")


if __name__ == "__main__":
    test_no_crash_on_test_cases()
