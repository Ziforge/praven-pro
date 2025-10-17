#!/usr/bin/env python3
"""
Example: Export single detection CSV to Raven Pro selection table
"""

import requests
import sys

# API endpoint
API_URL = "http://localhost:8080"


def export_to_raven(
    detections_csv: str,
    output_path: str,
    audio_file: str,
    audio_path: str,
    low_freq: float = 500.0,
    high_freq: float = 8000.0,
):
    """Export BirdNET detections to Raven Pro format"""

    payload = {
        "detections_csv": detections_csv,
        "output_path": output_path,
        "audio_file": audio_file,
        "audio_path": audio_path,
        "default_low_freq": low_freq,
        "default_high_freq": high_freq,
    }

    print(f"📤 Exporting {detections_csv} to Raven format...")

    try:
        response = requests.post(
            f"{API_URL}/raven/export", json=payload, timeout=300
        )
        response.raise_for_status()
        result = response.json()

        print(f"✅ Success!")
        print(f"   Output: {result.get('output_path')}")
        print(f"   Selections: {result.get('num_selections', 0)}")

        return result

    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Example usage
    result = export_to_raven(
        detections_csv="/workspace/shared/results/csvs/recording_001_detections.csv",
        output_path="/workspace/shared/results/raven_tables/recording_001_raven.txt",
        audio_file="recording_001.wav",
        audio_path="/workspace/shared/audio/recording_001.wav",
        low_freq=500.0,
        high_freq=8000.0,
    )

    print("\n📋 Full response:")
    print(result)
