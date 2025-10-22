#!/usr/bin/env python3
"""
Fast validation of Gaulossen dataset - skip API calls, use rule-based only.
"""

import os
import sys
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from praven.config import ValidationConfig, ValidationResult
from praven.rules import TemporalValidator, HabitatValidator
from praven.models import WeatherActivityModel


def fast_validate(row, temporal_validator, habitat_validator, weather_model, config):
    """Fast validation without API calls."""

    species = row['common_name']
    timestamp = row['absolute_timestamp']
    confidence = row['confidence']

    # Parse timestamp
    date_part, time_part = timestamp.split(' ', 1) if ' ' in timestamp else (config.date, timestamp)

    result = ValidationResult(
        species=species,
        timestamp=timestamp,
        confidence=confidence,
        status="REVIEW",
        geographic_valid=True,  # Skip API validation
        temporal_valid=True,
        habitat_valid=True
    )

    rejection_reasons = []
    review_notes = []

    # 1. Habitat Validation
    habitat_valid, habitat_reason, habitat_score = habitat_validator.validate(
        species_name=species,
        habitat_type=config.habitat_type,
        min_threshold=0.3
    )

    result.habitat_valid = habitat_valid
    if not habitat_valid:
        rejection_reasons.append(habitat_reason)

    # Check native region
    native_valid, native_reason = habitat_validator.check_native_region(species, "Europe")
    if not native_valid:
        result.habitat_valid = False
        rejection_reasons.append(native_reason)

    # 2. Temporal Validation
    temporal_valid, temporal_warnings = temporal_validator.is_species_active(
        species_name=species,
        timestamp=time_part,
        date=date_part
    )

    result.temporal_valid = temporal_valid
    if not temporal_valid:
        rejection_reasons.extend(temporal_warnings)

    # 3. Weather Activity Score
    if config.weather_conditions:
        weather_score = weather_model.predict_activity_score(
            species_name=species,
            weather_conditions=config.weather_conditions
        )
        result.weather_score = weather_score

        if weather_score < 0.3:
            review_notes.append(f"Low weather activity: {weather_score:.2f}")

    # 4. Calculate Overall Score (without geographic data)
    scores = []
    scores.append(habitat_score * 0.4)  # Increased weight
    scores.append(1.0 * 0.3 if result.temporal_valid else 0.0)
    scores.append(confidence * 0.3)

    result.overall_score = sum(scores)

    # 5. Determine Status
    if rejection_reasons:
        result.status = "REJECT"
        result.rejection_reason = "; ".join(rejection_reasons)
    elif result.overall_score >= 0.7 and confidence >= 0.7:
        result.status = "ACCEPT"
    elif result.overall_score < 0.4 or confidence < config.min_confidence:
        result.status = "REVIEW"
        review_notes.append(f"Low score: {result.overall_score:.2f}")
    else:
        result.status = "REVIEW"

    result.review_notes = review_notes

    return result.to_dict()


def main():
    """Fast validation of Gaulossen dataset."""

    print("=" * 80)
    print("Praven Pro - Fast Gaulossen Validation (Rule-Based Only)")
    print("=" * 80)

    # Paths
    all_detections = "../gaulossen/gaulosen_study/raw_data/analysis_csvs/all_detections.csv"
    verified_detections = "../gaulossen/gaulosen_study/raw_data/analysis_csvs/verified_detections.csv"

    # Load data
    print(f"\nLoading data...")
    df_all = pd.read_csv(all_detections)
    df_verified = pd.read_csv(verified_detections)

    print(f"  All detections: {len(df_all):,}")
    print(f"  Manually verified: {len(df_verified):,}")
    print(f"  Manual rejection rate: {100*(1 - len(df_verified)/len(df_all)):.1f}%")

    # Configure validator
    config = ValidationConfig(
        location=(63.341, 10.215),
        date="2025-10-13",
        habitat_type="wetland",
        weather_conditions={
            "rain": 0.8,
            "fog": 0.7,
            "temperature": 8.0
        },
        min_confidence=0.1
    )

    print(f"\nValidation Configuration:")
    print(f"  Location: {config.location}")
    print(f"  Habitat: {config.habitat_type}")
    print(f"  Weather: Rain=80%, Fog=70%, Temp=8°C")
    print(f"  Mode: Rule-based only (no API calls)")

    # Initialize validators
    print(f"\nInitializing validators...")
    temporal_validator = TemporalValidator()
    habitat_validator = HabitatValidator()
    weather_model = WeatherActivityModel()

    # Run validation
    print(f"\nValidating {len(df_all):,} detections...")

    results = []
    for idx, row in df_all.iterrows():
        result = fast_validate(row, temporal_validator, habitat_validator, weather_model, config)
        results.append(result)

        if (idx + 1) % 1000 == 0:
            print(f"  Processed {idx + 1:,}/{len(df_all):,} detections...")

    # Create results dataframe
    results_df = pd.DataFrame(results)
    output_df = pd.concat([df_all.reset_index(drop=True), results_df], axis=1)

    # Save results
    output_df.to_csv('gaulossen_validated_fast.csv', index=False)

    # Statistics
    print(f"\n{'=' * 80}")
    print("Automated Validation Results")
    print("=" * 80)

    status_counts = results_df['status'].value_counts()
    total = len(results_df)

    accepted = status_counts.get('ACCEPT', 0)
    rejected = status_counts.get('REJECT', 0)
    review = status_counts.get('REVIEW', 0)

    print(f"\nOverall Statistics:")
    print(f"  Total Detections:     {total:,}")
    print(f"  Auto-Accepted:        {accepted:,} ({100*accepted/total:.1f}%)")
    print(f"  Auto-Rejected:        {rejected:,} ({100*rejected/total:.1f}%)")
    print(f"  Needs Review:         {review:,} ({100*review/total:.1f}%)")

    # Compare to manual verification
    print(f"\n{'=' * 80}")
    print("Comparison to Manual Verification")
    print("=" * 80)

    # Species-level comparison
    manual_species = set(df_verified['common_name'].unique())
    auto_rejected_df = output_df[output_df['status'] == 'REJECT']
    auto_rejected_species = set(auto_rejected_df['common_name'].unique())

    all_species = set(df_all['common_name'].unique())

    print(f"\nSpecies-Level Analysis:")
    print(f"  Total species detected: {len(all_species)}")
    print(f"  Manually verified species: {len(manual_species)}")
    print(f"  Auto-rejected species: {len(auto_rejected_species)}")

    # Find correctly rejected species
    correctly_rejected = auto_rejected_species - manual_species
    incorrectly_rejected = auto_rejected_species & manual_species

    print(f"\n  Correctly rejected (not in manual): {len(correctly_rejected)}")
    print(f"  Incorrectly rejected (in manual): {len(incorrectly_rejected)}")

    # Show rejected species
    if correctly_rejected:
        print(f"\n  Auto-Rejected Species (not in manual verification):")
        rejected_counts = auto_rejected_df[auto_rejected_df['common_name'].isin(correctly_rejected)]['common_name'].value_counts()
        for species, count in rejected_counts.items():
            print(f"    [{count:3d}] {species}")

    if incorrectly_rejected:
        print(f"\n  WARNING - Incorrectly Rejected (were manually verified):")
        incorrect_counts = auto_rejected_df[auto_rejected_df['common_name'].isin(incorrectly_rejected)]['common_name'].value_counts()
        for species, count in incorrect_counts.items():
            print(f"    [{count:3d}] {species}")

    # Top rejection reasons
    rejection_reasons = results_df[results_df['status'] == 'REJECT']['rejection_reason'].value_counts()
    if len(rejection_reasons) > 0:
        print(f"\n  Top Rejection Reasons:")
        for reason, count in rejection_reasons.head(15).items():
            reason_short = reason[:75] + "..." if len(reason) > 75 else reason
            print(f"    [{count:3d}] {reason_short}")

    # Efficiency metrics
    print(f"\n{'=' * 80}")
    print("Time Savings Estimate")
    print("=" * 80)

    auto_decided = accepted + rejected

    print(f"\nAutomated Decisions: {auto_decided:,} ({100*auto_decided/total:.1f}%)")
    print(f"Human Review Needed: {review:,} ({100*review/total:.1f}%)")
    print(f"\nEstimated Time Savings:")
    print(f"  Manual review (all): ~{total*2/60:.0f} minutes")
    print(f"  With automation: ~{review*2/60:.0f} minutes")
    print(f"  Time saved: ~{auto_decided*2/60:.0f} minutes ({100*auto_decided/total:.0f}% reduction)")

    # Save subset files
    output_df[output_df['status'] == 'ACCEPT'].to_csv('gaulossen_auto_accepted.csv', index=False)
    output_df[output_df['status'] == 'REJECT'].to_csv('gaulossen_auto_rejected.csv', index=False)
    output_df[output_df['status'] == 'REVIEW'].to_csv('gaulossen_needs_review.csv', index=False)

    print(f"\nOutput Files:")
    print(f"  gaulossen_validated_fast.csv - All detections with validation")
    print(f"  gaulossen_auto_accepted.csv - Auto-accepted detections")
    print(f"  gaulossen_auto_rejected.csv - Auto-rejected (likely false positives)")
    print(f"  gaulossen_needs_review.csv - Ambiguous, needs human check")

    print(f"\n{'=' * 80}")
    print("Done!")
    print("=" * 80)


if __name__ == "__main__":
    main()
