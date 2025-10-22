#!/usr/bin/env python3
"""
Validate BirdNET CSV results using Praven Pro.

Example:
    python validate_csv.py BirdNET_results.txt --output validated_results.csv
"""

import os
import sys
import argparse
import pandas as pd

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from praven import BiologicalValidator, ValidationConfig


def main():
    """Validate BirdNET CSV file."""

    parser = argparse.ArgumentParser(description='Validate BirdNET results with biological checks')

    parser.add_argument('input', help='Path to BirdNET results CSV/TXT file')
    parser.add_argument('--output', '-o', help='Path to output validated CSV file')

    parser.add_argument('--lat', type=float, required=True, help='Latitude')
    parser.add_argument('--lon', type=float, required=True, help='Longitude')
    parser.add_argument('--date', required=True, help='Recording date (YYYY-MM-DD)')
    parser.add_argument('--habitat', required=True,
                        choices=['wetland', 'forest', 'oceanic', 'grassland', 'urban', 'mixed'],
                        help='Habitat type')

    parser.add_argument('--rain', type=float, default=0.0, help='Rain intensity (0-1)')
    parser.add_argument('--fog', type=float, default=0.0, help='Fog density (0-1)')
    parser.add_argument('--temp', type=float, default=10.0, help='Temperature (Celsius)')

    parser.add_argument('--ebird-key', help='eBird API key (or set EBIRD_API_KEY env var)')
    parser.add_argument('--radius', type=float, default=50.0, help='Geographic search radius (km)')

    parser.add_argument('--min-confidence', type=float, default=0.1,
                        help='Minimum BirdNET confidence (0-1)')

    args = parser.parse_args()

    # Load BirdNET results
    print(f"Loading BirdNET results from: {args.input}")

    try:
        # Try tab-separated first (BirdNET default)
        df = pd.read_csv(args.input, sep='\t')
    except:
        # Fallback to comma-separated
        df = pd.read_csv(args.input)

    print(f"  Loaded {len(df)} detections")

    # Detect column names (BirdNET uses different formats)
    species_col = None
    time_col = None
    confidence_col = None
    scientific_col = None

    # Common column name variations
    for col in df.columns:
        col_lower = col.lower()

        if 'common' in col_lower and 'name' in col_lower:
            species_col = col
        elif 'species' in col_lower:
            species_col = col

        if 'begin' in col_lower and 'time' in col_lower:
            time_col = col
        elif 'start' in col_lower:
            time_col = col

        if 'confidence' in col_lower or 'score' in col_lower:
            confidence_col = col

        if 'scientific' in col_lower:
            scientific_col = col

    if not all([species_col, time_col, confidence_col]):
        print("Error: Could not detect required columns")
        print(f"  Found columns: {list(df.columns)}")
        print("  Need: species name, timestamp, confidence score")
        sys.exit(1)

    print(f"  Detected columns:")
    print(f"    Species: {species_col}")
    print(f"    Time: {time_col}")
    print(f"    Confidence: {confidence_col}")

    # Configure validator
    config = ValidationConfig(
        location=(args.lat, args.lon),
        date=args.date,
        habitat_type=args.habitat,
        weather_conditions={
            "rain": args.rain,
            "fog": args.fog,
            "temperature": args.temp
        },
        ebird_api_key=args.ebird_key or os.getenv('EBIRD_API_KEY'),
        geographic_radius_km=args.radius,
        min_confidence=args.min_confidence
    )

    print(f"\nValidation Configuration:")
    print(f"  Location: ({args.lat}, {args.lon})")
    print(f"  Date: {args.date}")
    print(f"  Habitat: {args.habitat}")
    print(f"  Weather: Rain={args.rain}, Fog={args.fog}, Temp={args.temp}°C")
    print(f"  eBird API: {'Enabled' if config.ebird_api_key else 'Disabled'}")
    print()

    # Run validation
    validator = BiologicalValidator(config)

    results_df = validator.validate_dataframe(
        df,
        species_col=species_col,
        time_col=time_col,
        confidence_col=confidence_col,
        scientific_col=scientific_col
    )

    # Get statistics
    stats = validator.get_validation_stats(results_df)

    print("\n" + "=" * 70)
    print("Validation Statistics")
    print("=" * 70)
    print(f"Total Detections:     {stats['total_detections']}")
    print(f"Accepted:             {stats['accepted']} ({100*stats['auto_pass_rate']:.1f}%)")
    print(f"Rejected:             {stats['rejected']} ({100*stats['auto_reject_rate']:.1f}%)")
    print(f"Needs Review:         {stats['needs_review']} ({100*stats['review_rate']:.1f}%)")

    if 'rejection_reasons' in stats:
        print("\nTop Rejection Reasons:")
        for reason, count in list(stats['rejection_reasons'].items())[:5]:
            print(f"  [{count}] {reason[:60]}...")

    # Save output
    if args.output:
        results_df.to_csv(args.output, index=False)
        print(f"\nResults saved to: {args.output}")

        # Also save summary files
        summary_dir = os.path.dirname(args.output) or '.'
        base_name = os.path.splitext(os.path.basename(args.output))[0]

        accepted_file = os.path.join(summary_dir, f"{base_name}_accepted.csv")
        rejected_file = os.path.join(summary_dir, f"{base_name}_rejected.csv")
        review_file = os.path.join(summary_dir, f"{base_name}_review.csv")

        results_df[results_df['status'] == 'ACCEPT'].to_csv(accepted_file, index=False)
        results_df[results_df['status'] == 'REJECT'].to_csv(rejected_file, index=False)
        results_df[results_df['status'] == 'REVIEW'].to_csv(review_file, index=False)

        print(f"  Accepted:     {accepted_file}")
        print(f"  Rejected:     {rejected_file}")
        print(f"  Needs Review: {review_file}")

    print("\nDone!")


if __name__ == "__main__":
    main()
