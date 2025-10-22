#!/usr/bin/env python3
"""
Validate Gaulossen BirdNET results and compare to manual verification.
"""

import os
import sys
import pandas as pd

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from praven import BiologicalValidator, ValidationConfig


def main():
    """Validate Gaulossen dataset."""

    print("=" * 80)
    print("Praven Pro - Gaulossen Nature Reserve Validation")
    print("=" * 80)

    # Paths
    all_detections = "../gaulossen/gaulosen_study/raw_data/analysis_csvs/all_detections.csv"
    verified_detections = "../gaulossen/gaulosen_study/raw_data/analysis_csvs/verified_detections.csv"
    output_file = "gaulossen_automated_validation.csv"

    # Load data
    print(f"\nLoading data...")
    df_all = pd.read_csv(all_detections)
    df_verified = pd.read_csv(verified_detections)

    print(f"  All detections: {len(df_all):,}")
    print(f"  Manually verified: {len(df_verified):,}")
    print(f"  Manual rejection rate: {100*(1 - len(df_verified)/len(df_all)):.1f}%")

    # Configure validator for Gaulossen
    config = ValidationConfig(
        location=(63.341, 10.215),  # Gaulosen coordinates
        date="2025-10-13",  # Start date
        habitat_type="wetland",
        weather_conditions={
            "rain": 0.8,      # 80% rain coverage from study
            "fog": 0.7,       # Heavy fog
            "temperature": 8.0  # 7-11°C range, use midpoint
        },
        ebird_api_key=os.getenv('EBIRD_API_KEY'),
        geographic_radius_km=50,
        min_confidence=0.1
    )

    print(f"\nValidation Configuration:")
    print(f"  Location: {config.location}")
    print(f"  Habitat: {config.habitat_type}")
    print(f"  Weather: Rain=80%, Fog=70%, Temp=8°C")
    print(f"  eBird API: {'Enabled' if config.ebird_api_key else 'Disabled (using GBIF only)'}")

    # Run automated validation
    print(f"\n{'=' * 80}")
    print("Running Automated Validation...")
    print("=" * 80)

    validator = BiologicalValidator(config)

    results_df = validator.validate_dataframe(
        df_all,
        species_col="common_name",
        time_col="absolute_timestamp",
        confidence_col="confidence",
        scientific_col="scientific_name"
    )

    # Save results
    results_df.to_csv(output_file, index=False)
    print(f"\nFull results saved to: {output_file}")

    # Get statistics
    stats = validator.get_validation_stats(results_df)

    print(f"\n{'=' * 80}")
    print("Automated Validation Results")
    print("=" * 80)

    print(f"\nOverall Statistics:")
    print(f"  Total Detections:     {stats['total_detections']:,}")
    print(f"  Auto-Accepted:        {stats['accepted']:,} ({100*stats['auto_pass_rate']:.1f}%)")
    print(f"  Auto-Rejected:        {stats['rejected']:,} ({100*stats['auto_reject_rate']:.1f}%)")
    print(f"  Needs Review:         {stats['needs_review']:,} ({100*stats['review_rate']:.1f}%)")

    # Compare to manual verification
    print(f"\n{'=' * 80}")
    print("Comparison to Manual Verification")
    print("=" * 80)

    # Get species-level comparison
    manual_species = set(df_verified['common_name'].unique())
    auto_accepted_df = results_df[results_df['status'] == 'ACCEPT']
    auto_accepted_species = set(auto_accepted_df['common_name'].unique())
    auto_rejected_df = results_df[results_df['status'] == 'REJECT']
    auto_rejected_species = set(auto_rejected_df['common_name'].unique())

    all_species = set(df_all['common_name'].unique())

    print(f"\nSpecies-Level Analysis:")
    print(f"  Total species detected: {len(all_species)}")
    print(f"  Manually verified species: {len(manual_species)}")
    print(f"  Auto-accepted species: {len(auto_accepted_species)}")
    print(f"  Auto-rejected species: {len(auto_rejected_species)}")

    # Find agreement and disagreement
    correctly_rejected = auto_rejected_species - manual_species
    correctly_accepted = auto_accepted_species & manual_species
    false_rejects = auto_rejected_species & manual_species
    false_accepts = auto_accepted_species - manual_species

    print(f"\n  Correctly rejected (not in manual): {len(correctly_rejected)}")
    print(f"  Correctly accepted (in manual): {len(correctly_accepted)}")
    print(f"  False rejects (rejected but in manual): {len(false_rejects)}")
    print(f"  False accepts (accepted but not in manual): {len(false_accepts)}")

    # Show rejected species
    if correctly_rejected:
        print(f"\n  Top Auto-Rejected Species (not in manual verification):")
        rejected_counts = auto_rejected_df[auto_rejected_df['common_name'].isin(correctly_rejected)]['common_name'].value_counts()
        for species, count in rejected_counts.head(10).items():
            print(f"    [{count:3d}] {species}")

    # Show top rejection reasons
    if 'rejection_reasons' in stats and stats['rejection_reasons']:
        print(f"\n  Top Rejection Reasons:")
        for reason, count in list(stats['rejection_reasons'].items())[:10]:
            # Truncate long reasons
            reason_short = reason[:70] + "..." if len(reason) > 70 else reason
            print(f"    [{count:3d}] {reason_short}")

    # Efficiency metrics
    print(f"\n{'=' * 80}")
    print("Time Savings Estimate")
    print("=" * 80)

    auto_decided = stats['accepted'] + stats['rejected']
    review_needed = stats['needs_review']

    print(f"\nAutomated Decisions: {auto_decided:,} ({100*auto_decided/stats['total_detections']:.1f}%)")
    print(f"Human Review Needed: {review_needed:,} ({100*review_needed/stats['total_detections']:.1f}%)")
    print(f"\nEstimated Time Savings:")
    print(f"  Manual review time (all detections): ~{stats['total_detections']*2/60:.1f} minutes")
    print(f"  With automation (review only): ~{review_needed*2/60:.1f} minutes")
    print(f"  Time saved: ~{(auto_decided*2)/60:.1f} minutes ({100*auto_decided/stats['total_detections']:.0f}% reduction)")

    # Save subset files
    results_df[results_df['status'] == 'ACCEPT'].to_csv('gaulossen_auto_accepted.csv', index=False)
    results_df[results_df['status'] == 'REJECT'].to_csv('gaulossen_auto_rejected.csv', index=False)
    results_df[results_df['status'] == 'REVIEW'].to_csv('gaulossen_needs_review.csv', index=False)

    print(f"\nOutput Files:")
    print(f"  gaulossen_automated_validation.csv - All detections with validation")
    print(f"  gaulossen_auto_accepted.csv - Auto-accepted detections")
    print(f"  gaulossen_auto_rejected.csv - Auto-rejected (likely false positives)")
    print(f"  gaulossen_needs_review.csv - Ambiguous, needs human check")

    print(f"\n{'=' * 80}")
    print("Done!")
    print("=" * 80)


if __name__ == "__main__":
    main()
