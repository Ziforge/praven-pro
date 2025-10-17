#!/usr/bin/env python3
"""
Example: Batch export all detection CSVs to Raven Pro selection tables
"""

import requests
import sys

API_URL = "http://localhost:8080"


def batch_export_to_raven(
    detections_dir: str,
    output_dir: str,
    audio_dir: str,
    file_pattern: str = "*_detections.csv",
    low_freq: float = 500.0,
    high_freq: float = 8000.0,
):
    """Batch export multiple detection CSVs to Raven format"""

    payload = {
        "detections_dir": detections_dir,
        "output_dir": output_dir,
        "audio_dir": audio_dir,
        "file_pattern": file_pattern,
        "default_low_freq": low_freq,
        "default_high_freq": high_freq,
    }

    print(f"📦 Batch exporting detections from {detections_dir}...")
    print(f"   Pattern: {file_pattern}")

    try:
        response = requests.post(
            f"{API_URL}/raven/export_batch", json=payload, timeout=600
        )
        response.raise_for_status()
        result = response.json()

        print(f"\n✅ Batch export complete!")
        print(f"   Files processed: {result.get('num_files', 0)}")
        print(f"   Total selections: {result.get('total_selections', 0)}")

        if "files" in result:
            print(f"\n📄 Files exported:")
            for file_info in result["files"]:
                print(
                    f"   - {file_info['csv_file']} → {file_info['output_path']} "
                    f"({file_info['num_selections']} selections)"
                )

        return result

    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Example: Export all detection CSVs
    result = batch_export_to_raven(
        detections_dir="/workspace/shared/results/csvs",
        output_dir="/workspace/shared/results/raven_tables",
        audio_dir="/workspace/shared/audio",
        file_pattern="*_detections.csv",
        low_freq=500.0,
        high_freq=8000.0,
    )

    print("\n📋 Full response:")
    print(result)
