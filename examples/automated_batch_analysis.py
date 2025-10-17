#!/usr/bin/env python3
"""
Automated Batch Analysis Script for Large Audio Files
Example: Processing multi-hour field recordings with timestamp extraction

This script demonstrates:
- Automated processing of multiple large audio files
- Timestamp extraction from filenames
- Progress tracking and logging
- Multiple output formats (CSV, Audacity labels, Raven tables)
- Memory-efficient handling of large files

Filename format expected: DeviceID_YYYYMMDD_HHMMSS.WAV
Example: 245AAA0563ED3DA7_20251013_113753.WAV
"""

import os
import sys
import glob
import re
from datetime import datetime
from pathlib import Path
import pandas as pd
import numpy as np

# Progress tracking
from tqdm import tqdm

# Audio processing
import librosa
import soundfile as sf

# BirdNET
from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer

print("=" * 80, flush=True)
print("🐦 AUTOMATED BATCH ANALYSIS - PRAVEN PRO", flush=True)
print("=" * 80, flush=True)
print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", flush=True)
print(flush=True)

# ============================================================================
# CONFIGURATION - Customize these settings for your project
# ============================================================================

# Directories
AUDIO_DIR = "audio_files"
RESULTS_DIR = "results"

# Recording location (for species filtering)
# Example: Gaulossen, Norway
LAT = 63.4305
LON = 10.3951

# BirdNET settings
MIN_CONF = 0.25  # Confidence threshold (0.0-1.0)
SENSITIVITY = 1.0  # Sensitivity (0.5-1.5)

# For large files - limit visualizations to save memory
MAX_DETECTIONS_PER_FILE = 50

# Filename pattern (customize for your device)
# This pattern matches: DeviceID_YYYYMMDD_HHMMSS.WAV
# Where DeviceID can contain hex digits (0-9, A-F)
FILENAME_PATTERN = r'([A-F0-9]+)_(\d{8})_(\d{6})\.WAV'

# ============================================================================
# SETUP
# ============================================================================

# Create results directories
os.makedirs(f"{RESULTS_DIR}/csvs", exist_ok=True)
os.makedirs(f"{RESULTS_DIR}/labels", exist_ok=True)
os.makedirs(f"{RESULTS_DIR}/raven_tables", exist_ok=True)
os.makedirs(f"{RESULTS_DIR}/visualizations", exist_ok=True)

print("📁 Directory structure:")
print(f"   Audio: {AUDIO_DIR}/")
print(f"   Results: {RESULTS_DIR}/")
print()

# ============================================================================
# FIND AUDIO FILES
# ============================================================================

audio_files = sorted(glob.glob(f"{AUDIO_DIR}/**/*.WAV", recursive=True))
print(f"📊 Found {len(audio_files)} audio files:")
for f in audio_files:
    size_gb = os.path.getsize(f) / (1024**3)
    print(f"   - {os.path.basename(f)} ({size_gb:.2f} GB)")
print()

if len(audio_files) == 0:
    print("❌ No audio files found!")
    print(f"   Please place WAV files in {AUDIO_DIR}/")
    sys.exit(1)

# ============================================================================
# PARSE TIMESTAMPS FROM FILENAMES
# ============================================================================

def parse_filename(filepath, pattern=FILENAME_PATTERN):
    """
    Parse filename to extract recording timestamp.

    Default pattern: DeviceID_YYYYMMDD_HHMMSS.WAV

    Args:
        filepath: Path to audio file
        pattern: Regex pattern (customize for your filename format)

    Returns:
        tuple: (date_str, time_str, datetime_obj)
    """
    filename = os.path.basename(filepath)
    match = re.match(pattern, filename)

    if match:
        device_id, date_str, time_str = match.groups()
        year = int(date_str[0:4])
        month = int(date_str[4:6])
        day = int(date_str[6:8])
        hour = int(time_str[0:2])
        minute = int(time_str[2:4])
        second = int(time_str[4:6])

        dt = datetime(year, month, day, hour, minute, second)
        date_str_formatted = dt.strftime("%Y-%m-%d")
        time_str_formatted = dt.strftime("%H:%M:%S")

        return date_str_formatted, time_str_formatted, dt

    # If pattern doesn't match, use file modification time as fallback
    print(f"   ⚠️  Could not parse timestamp from: {filename}")
    print(f"   Using file modification time as fallback")
    mtime = os.path.getmtime(filepath)
    dt = datetime.fromtimestamp(mtime)
    return dt.strftime("%Y-%m-%d"), dt.strftime("%H:%M:%S"), dt

print("📅 Recording timestamps:")
file_metadata = []
for audio_file in audio_files:
    date, time, dt = parse_filename(audio_file)
    if dt:
        file_metadata.append({
            'filepath': audio_file,
            'filename': os.path.basename(audio_file),
            'date': date,
            'time': time,
            'datetime': dt
        })
        print(f"   {os.path.basename(audio_file)}")
        print(f"      Date: {date}, Time: {time}")
print()

# ============================================================================
# INITIALIZE BIRDNET ANALYZER
# ============================================================================

print("🤖 Initializing BirdNET analyzer...")
print(f"   Location: {LAT}°N, {LON}°E")
print(f"   Confidence threshold: {MIN_CONF}")
print()

analyzer = Analyzer()

# ============================================================================
# PROCESS EACH FILE
# ============================================================================

all_detections = []
file_summary = []

for idx, metadata in enumerate(file_metadata, 1):
    filepath = metadata['filepath']
    filename = metadata['filename']
    recording_date = metadata['date']
    recording_time = metadata['time']

    print(f"{'='*80}")
    print(f"📄 Processing file {idx}/{len(file_metadata)}: {filename}")
    print(f"   Date: {recording_date}, Time: {recording_time}")
    print(f"{'='*80}")

    # Get file info
    file_size_gb = os.path.getsize(filepath) / (1024**3)
    print(f"   Size: {file_size_gb:.2f} GB")

    # Get audio duration
    try:
        info = sf.info(filepath)
        duration_hours = info.duration / 3600
        print(f"   Duration: {duration_hours:.2f} hours ({info.duration:.0f} seconds)")
        print(f"   Sample rate: {info.samplerate} Hz")
    except Exception as e:
        print(f"   ⚠️  Could not read audio info: {e}")
        continue

    print(f"\n   🔍 Running BirdNET analysis...")
    start_time = datetime.now()

    try:
        # Create recording object
        recording = Recording(
            analyzer,
            filepath,
            lat=LAT,
            lon=LON,
            date=datetime.strptime(recording_date, "%Y-%m-%d"),
            min_conf=MIN_CONF,
            sensitivity=SENSITIVITY
        )

        # Analyze
        recording.analyze()

        end_time = datetime.now()
        analysis_duration = (end_time - start_time).total_seconds()
        print(f"   ✅ Analysis complete in {analysis_duration:.1f} seconds ({analysis_duration/60:.1f} minutes)")

        # Get detections
        detections = recording.detections
        print(f"   🐦 Found {len(detections)} detections above {MIN_CONF} confidence")

        if len(detections) == 0:
            print(f"   ℹ️  No detections found - skipping this file")
            continue

        # Process detections
        file_stem = os.path.splitext(filename)[0]

        # Convert to DataFrame
        det_df = pd.DataFrame(detections)

        # Add file metadata
        det_df['file_index'] = idx
        det_df['filename'] = filename
        det_df['file_stem'] = file_stem
        det_df['recording_date'] = recording_date
        det_df['recording_start_time'] = recording_time

        # Calculate absolute timestamp for each detection
        # Add detection start time to recording start time
        det_df['absolute_timestamp'] = det_df.apply(
            lambda row: (metadata['datetime'] + pd.Timedelta(seconds=row['start_time'])).strftime('%Y-%m-%d %H:%M:%S'),
            axis=1
        )

        # Rename columns for clarity
        det_df = det_df.rename(columns={
            'start_time': 'start_s',
            'end_time': 'end_s'
        })

        all_detections.append(det_df)

        # Save per-file CSV
        csv_path = f"{RESULTS_DIR}/csvs/{file_stem}_detections.csv"
        det_df.to_csv(csv_path, index=False)
        print(f"   💾 Saved: {csv_path}")

        # Generate Audacity labels
        label_path = f"{RESULTS_DIR}/labels/{file_stem}_labels.txt"
        with open(label_path, 'w') as f:
            for _, det in det_df.iterrows():
                f.write(f"{det['start_s']}\t{det['end_s']}\t{det['common_name']} ({det['confidence']:.2f})\n")
        print(f"   💾 Saved: {label_path}")

        # Generate Raven Pro selection table
        raven_path = f"{RESULTS_DIR}/raven_tables/{file_stem}_raven.txt"
        raven_df = pd.DataFrame()
        raven_df['Selection'] = range(1, len(det_df) + 1)
        raven_df['View'] = 'Spectrogram 1'
        raven_df['Channel'] = 1
        raven_df['Begin Time (s)'] = det_df['start_s']
        raven_df['End Time (s)'] = det_df['end_s']
        raven_df['Low Freq (Hz)'] = 500.0  # Default - adjust as needed
        raven_df['High Freq (Hz)'] = 8000.0  # Default - adjust as needed
        raven_df['Begin File'] = filename
        raven_df['Begin Path'] = filepath
        raven_df['File Offset (s)'] = 0.0
        raven_df['Common Name'] = det_df['common_name']
        raven_df['Scientific Name'] = det_df['scientific_name']
        raven_df['Confidence'] = det_df['confidence']
        raven_df['Absolute Timestamp'] = det_df['absolute_timestamp']

        raven_df.to_csv(raven_path, sep='\t', index=False)
        print(f"   💾 Saved: {raven_path}")

        # File summary
        unique_species = det_df['common_name'].nunique()
        file_summary.append({
            'file_index': idx,
            'filename': filename,
            'recording_date': recording_date,
            'recording_start_time': recording_time,
            'duration_hours': duration_hours,
            'num_detections': len(det_df),
            'unique_species': unique_species,
            'analysis_duration_seconds': analysis_duration,
            'csv_file': csv_path,
            'label_file': label_path,
            'raven_file': raven_path
        })

        print(f"   📊 Summary: {len(det_df)} detections, {unique_species} unique species")

    except Exception as e:
        print(f"   ❌ Error processing file: {e}")
        import traceback
        traceback.print_exc()
        continue

    print()

# ============================================================================
# CREATE MASTER FILES
# ============================================================================

print(f"{'='*80}")
print("📊 CREATING MASTER FILES")
print(f"{'='*80}")

if all_detections:
    all_detections_df = pd.concat(all_detections, ignore_index=True)

    # Save master CSV
    master_csv = f"{RESULTS_DIR}/all_detections.csv"
    all_detections_df.to_csv(master_csv, index=False)
    print(f"💾 Saved master detections: {master_csv}")
    print(f"   Total detections: {len(all_detections_df)}")

    # Save file summary
    summary_df = pd.DataFrame(file_summary)
    summary_csv = f"{RESULTS_DIR}/file_summary.csv"
    summary_df.to_csv(summary_csv, index=False)
    print(f"💾 Saved file summary: {summary_csv}")

    # Species summary
    species_counts = all_detections_df['common_name'].value_counts()
    print(f"\n🐦 Top 10 detected species:")
    for species, count in species_counts.head(10).items():
        print(f"   {count:4d}x  {species}")

    species_summary_csv = f"{RESULTS_DIR}/species_summary.csv"
    species_counts.to_csv(species_summary_csv, header=['count'])
    print(f"\n💾 Saved species summary: {species_summary_csv}")

else:
    print("⚠️  No detections found in any files")

# ============================================================================
# SUMMARY
# ============================================================================

print(f"\n{'='*80}")
print("✅ ANALYSIS COMPLETE")
print(f"{'='*80}")
print(f"Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"\n📁 All results saved to: {RESULTS_DIR}/")
print("\n📖 Next steps:")
print("   1. Review detections: results/csvs/")
print("   2. Open in Raven Pro: results/raven_tables/")
print("   3. Import to Audacity: results/labels/")
print("   4. Check species summary: results/species_summary.csv")
print()
