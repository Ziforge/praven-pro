#!/usr/bin/env python3
"""
Praven Pro - One-Line Validation Script

Quick validation of BirdNET CSV files with minimal configuration.

Usage:
    python validate.py path/to/birdnet.csv --lat 63.341 --lon 10.215 --habitat wetland
"""

import argparse
import sys
from pathlib import Path

from praven.validator import BiologicalValidator
from praven.config import ValidationConfig
from praven.pipeline import ValidationPipeline


def main():
    parser = argparse.ArgumentParser(
        description="Validate BirdNET detections using biological rules",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate with auto-detection (habitat and weather from GPS)
  python validate.py detections.csv --lat 63.341 --lon 10.215 --date 2025-10-13

  # Validate with manual habitat specification
  python validate.py detections.csv --lat 63.341 --lon 10.215 --habitat wetland

  # Validate with manual weather conditions
  python validate.py detections.csv --lat 63.341 --lon 10.215 --habitat wetland --rain 0.8 --fog 0.7

  # Disable auto-detection features
  python validate.py detections.csv --lat 63.341 --lon 10.215 --habitat wetland \
    --no-auto-weather --no-auto-habitat

  # Export to multiple formats
  python validate.py detections.csv --lat 63.341 --lon 10.215 --formats csv json

Habitats:
  wetland, forest, oceanic, grassland, urban, agricultural (or auto-detected from GPS)
        """
    )

    parser.add_argument(
        'input_csv',
        help='Path to BirdNET detections CSV file'
    )

    parser.add_argument(
        '--lat',
        type=float,
        required=True,
        help='Latitude of study site'
    )

    parser.add_argument(
        '--lon',
        type=float,
        required=True,
        help='Longitude of study site'
    )

    parser.add_argument(
        '--habitat',
        required=False,
        default=None,
        choices=['wetland', 'forest', 'oceanic', 'grassland', 'urban', 'agricultural'],
        help='Habitat type of study site (auto-detected from GPS if not specified)'
    )

    parser.add_argument(
        '--date',
        help='Study date (YYYY-MM-DD format)',
        default=None
    )

    parser.add_argument(
        '--rain',
        type=float,
        help='Rain intensity (0.0-1.0)',
        default=None
    )

    parser.add_argument(
        '--fog',
        type=float,
        help='Fog density (0.0-1.0)',
        default=None
    )

    parser.add_argument(
        '--temp',
        type=float,
        help='Temperature (°C)',
        default=None
    )

    parser.add_argument(
        '--output',
        help='Output directory (default: same as input)',
        default=None
    )

    parser.add_argument(
        '--formats',
        nargs='+',
        choices=['csv', 'json', 'excel'],
        default=['csv'],
        help='Output formats (default: csv)'
    )

    parser.add_argument(
        '--no-ebird',
        action='store_true',
        help='Disable eBird preloading (faster but less accurate)'
    )

    parser.add_argument(
        '--no-auto-weather',
        action='store_true',
        help='Disable automatic weather fetching from GPS'
    )

    parser.add_argument(
        '--no-auto-habitat',
        action='store_true',
        help='Disable automatic habitat detection from GPS'
    )

    args = parser.parse_args()

    # Validate input file
    input_path = Path(args.input_csv)
    if not input_path.exists():
        print(f"ERROR: Input file not found: {input_path}")
        sys.exit(1)

    # Build config
    print("\n" + "=" * 80)
    print("Praven Pro 2.0 - BirdNET Biological Validation")
    print("=" * 80)

    print(f"\nConfiguration:")
    print(f"  Input:    {input_path}")
    print(f"  Location: ({args.lat}, {args.lon})")
    print(f"  Habitat:  {args.habitat}")
    if args.date:
        print(f"  Date:     {args.date}")

    # Build weather conditions
    weather = None
    if any([args.rain is not None, args.fog is not None, args.temp is not None]):
        weather = {}
        if args.rain is not None:
            weather['rain'] = args.rain
        if args.fog is not None:
            weather['fog'] = args.fog
        if args.temp is not None:
            weather['temperature'] = args.temp
        print(f"  Weather:  {weather}")

    # Create config
    config = ValidationConfig(
        location=(args.lat, args.lon),
        date=args.date or "2025-01-01",  # Default date if not provided
        habitat_type=args.habitat,
        weather_conditions=weather,
        auto_detect_weather=not args.no_auto_weather and weather is None,
        auto_detect_habitat=not args.no_auto_habitat and args.habitat is None
    )

    # Create pipeline
    pipeline = ValidationPipeline(config)

    # Disable eBird preload if requested
    if args.no_ebird:
        pipeline.validator.ebird_preloader = None
        print("\n  eBird preloading: DISABLED")

    # Run validation
    try:
        output_files = pipeline.process_birdnet_csv(
            input_path=str(input_path),
            output_dir=args.output,
            export_formats=args.formats
        )

        print(f"\n{'=' * 80}")
        print("Validation Complete!")
        print("=" * 80)

        print(f"\nOutput files:")
        for name, path in output_files.items():
            print(f"  {name:20s} → {path}")

        print(f"\n✅ Successfully validated {input_path.name}")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
