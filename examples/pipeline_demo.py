#!/usr/bin/env python3
"""
Demonstration of Praven Pro validation pipeline.

Automates: BirdNET CSV → Validation → Filtered Results
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from praven.pipeline import create_pipeline


def main():
    """Demo validation pipeline."""

    print("=" * 80)
    print("Praven Pro - Automated Validation Pipeline Demo")
    print("=" * 80)

    # Create pipeline for Gaulossen
    pipeline = create_pipeline(
        location=(63.341, 10.215),
        date="2025-10-13",
        habitat_type="wetland",
        weather={"rain": 0.8, "fog": 0.7, "temperature": 8.0}
    )

    # Process Gaulossen data
    input_file = "../gaulossen/gaulosen_study/raw_data/analysis_csvs/all_detections.csv"

    if not os.path.exists(input_file):
        print(f"\nERROR: Input file not found: {input_file}")
        print("Please run this script from the praven-pro directory")
        return

    # Run pipeline
    outputs = pipeline.process_birdnet_csv(
        input_path=input_file,
        output_dir="pipeline_output",
        export_formats=['csv', 'json']
    )

    print(f"\n{'=' * 80}")
    print("Pipeline Complete!")
    print("=" * 80)

    print(f"\nOutput Files:")
    for name, path in outputs.items():
        print(f"  {name:20s} → {path}")

    print(f"\nNext Steps:")
    print(f"  1. Review accepted detections:  pipeline_output/*_accepted.csv")
    print(f"  2. Check rejected detections:   pipeline_output/*_rejected.csv")
    print(f"  3. Manually review ambiguous:   pipeline_output/*_review.csv")
    print(f"  4. Read summary report:         pipeline_output/*_summary.txt")


if __name__ == "__main__":
    main()
