#!/usr/bin/env python3
"""
Example: Import Raven Pro selection table back to CSV format
(useful after manual annotation/refinement in Raven Pro)
"""

import requests
import sys

API_URL = "http://localhost:8080"


def import_from_raven(raven_table_path: str, output_csv: str):
    """Import Raven selection table to standard CSV format"""

    payload = {
        "raven_table_path": raven_table_path,
        "output_csv": output_csv,
    }

    print(f"📥 Importing Raven table: {raven_table_path}...")

    try:
        response = requests.post(
            f"{API_URL}/raven/import", json=payload, timeout=300
        )
        response.raise_for_status()
        result = response.json()

        print(f"✅ Import successful!")
        print(f"   Output: {result.get('output_csv')}")
        print(f"   Selections imported: {result.get('num_selections', 0)}")

        return result

    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Example: Import annotated Raven table back to CSV
    result = import_from_raven(
        raven_table_path="/workspace/shared/results/raven_tables/recording_001_raven_annotated.txt",
        output_csv="/workspace/shared/results/csvs/recording_001_annotated.csv",
    )

    print("\n📋 Full response:")
    print(result)
