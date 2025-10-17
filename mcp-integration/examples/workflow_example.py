#!/usr/bin/env python3
"""
Complete workflow example: Process → Export → (Manual Review) → Import

This demonstrates a typical bioacoustics workflow:
1. Run BirdNET analysis (Jupyter notebook)
2. Export detections to Raven Pro (API)
3. Manual review/refinement in Raven Pro (user does this)
4. Import refined selections back to CSV (API)
"""

import requests
import time
from pathlib import Path

API_URL = "http://localhost:8080"


def check_api_health():
    """Verify API is running"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        response.raise_for_status()
        print("✅ API is running")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ API not available: {e}")
        print("   Run 'docker compose up -d' in mcp-integration/ directory")
        return False


def export_batch_to_raven():
    """Step 2: Export all detections to Raven format"""
    print("\n📦 STEP 2: Batch export to Raven Pro format")
    print("=" * 60)

    payload = {
        "detections_dir": "/workspace/shared/results/csvs",
        "output_dir": "/workspace/shared/results/raven_tables",
        "audio_dir": "/workspace/shared/audio",
        "file_pattern": "*_detections.csv",
        "default_low_freq": 500.0,
        "default_high_freq": 8000.0,
    }

    response = requests.post(
        f"{API_URL}/raven/export_batch", json=payload, timeout=600
    )
    response.raise_for_status()
    result = response.json()

    print(f"✅ Exported {result.get('num_files', 0)} files")
    print(f"   Total selections: {result.get('total_selections', 0)}")

    return result


def import_refined_selections():
    """Step 4: Import refined Raven tables back to CSV"""
    print("\n📥 STEP 4: Import refined selections from Raven Pro")
    print("=" * 60)

    # Example: Import one refined table
    payload = {
        "raven_table_path": "/workspace/shared/results/raven_tables/recording_001_raven.txt",
        "output_csv": "/workspace/shared/results/csvs/recording_001_refined.csv",
    }

    response = requests.post(
        f"{API_URL}/raven/import", json=payload, timeout=300
    )
    response.raise_for_status()
    result = response.json()

    print(f"✅ Imported {result.get('num_selections', 0)} refined selections")
    print(f"   Output: {result.get('output_csv')}")

    return result


def main():
    """Run complete workflow"""
    print("🐦 PRAVEN PRO - COMPLETE WORKFLOW EXAMPLE")
    print("=" * 60)

    # Check API
    if not check_api_health():
        return

    # Step 1: Run BirdNET analysis
    print("\n📊 STEP 1: Run BirdNET analysis")
    print("=" * 60)
    print("👉 Run the Jupyter notebook: notebooks/bird_audio_batch_analysis.ipynb")
    print("   This generates detection CSVs in results/csvs/")
    print("\n⏸️  Press Enter once you've completed Step 1...")
    input()

    # Step 2: Export to Raven
    export_result = export_batch_to_raven()

    # Step 3: Manual review in Raven Pro
    print("\n🔍 STEP 3: Manual review in Raven Pro")
    print("=" * 60)
    print("👉 Open Raven Pro and load selection tables from:")
    print(f"   {Path.cwd().parent / 'results' / 'raven_tables'}")
    print("\n   - Verify detections")
    print("   - Delete false positives")
    print("   - Adjust time/frequency bounds")
    print("   - Add manual annotations")
    print("   - Save changes")
    print("\n⏸️  Press Enter once you've completed Step 3...")
    input()

    # Step 4: Import refined selections
    import_result = import_refined_selections()

    # Done
    print("\n✅ WORKFLOW COMPLETE!")
    print("=" * 60)
    print("📁 Outputs:")
    print(f"   - Original detections: results/csvs/*_detections.csv")
    print(f"   - Raven tables: results/raven_tables/*_raven.txt")
    print(f"   - Refined CSVs: results/csvs/*_refined.csv")
    print("\n📊 You can now use refined CSVs for statistical analysis!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Workflow interrupted by user")
    except requests.exceptions.RequestException as e:
        print(f"\n❌ API Error: {e}")
        print("   Check that Docker services are running:")
        print("   cd mcp-integration && docker compose logs")
