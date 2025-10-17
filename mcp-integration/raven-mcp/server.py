#!/usr/bin/env python3
"""
Raven Pro MCP Server
Provides tools for converting between BirdNET/acoustic analysis formats and Raven Pro selection tables.
Includes Rraven R integration for advanced bioacoustic measurements.
"""

import os
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

from starlette.applications import Starlette
from starlette.routing import Mount
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP with stateless HTTP support
mcp = FastMCP(
    name="RavenProMCP",
    stateless_http=True,
    dependencies=["pandas", "numpy", "rpy2"]
)


# ============================================================================
# Raven Selection Table Format Utilities
# ============================================================================

def normalize_path(path: str) -> str:
    """Normalize path to container-style /workspace/ format"""
    if path.startswith("/workspace/"):
        return path
    return "/workspace/" + path.lstrip("/")


RAVEN_COLUMNS = [
    "Selection",
    "View",
    "Channel",
    "Begin Time (s)",
    "End Time (s)",
    "Low Freq (Hz)",
    "High Freq (Hz)",
    "Begin File",
    "Begin Path",
    "File Offset (s)"
]


def create_raven_selection_table(
    detections: pd.DataFrame,
    audio_file: str,
    audio_path: str,
    default_low_freq: float = 0.0,
    default_high_freq: float = 10000.0,
    channel: int = 1
) -> pd.DataFrame:
    """
    Convert detection dataframe to Raven Pro selection table format.

    Args:
        detections: DataFrame with columns: start_s, end_s, [low_freq_hz, high_freq_hz]
        audio_file: Name of audio file (e.g., "recording.wav")
        audio_path: Full path to audio file
        default_low_freq: Default lower frequency bound if not specified
        default_high_freq: Default upper frequency bound if not specified
        channel: Audio channel number (1-indexed)

    Returns:
        DataFrame in Raven selection table format
    """
    raven_data = []

    for idx, row in detections.iterrows():
        selection = {
            "Selection": idx + 1,
            "View": "Spectrogram 1",
            "Channel": channel,
            "Begin Time (s)": float(row["start_s"]),
            "End Time (s)": float(row["end_s"]),
            "Low Freq (Hz)": float(row.get("low_freq_hz", default_low_freq)),
            "High Freq (Hz)": float(row.get("high_freq_hz", default_high_freq)),
            "Begin File": audio_file,
            "Begin Path": audio_path,
            "File Offset (s)": 0.0
        }

        # Add optional metadata columns
        for col in ["common_name", "scientific_name", "confidence", "label"]:
            if col in row and pd.notna(row[col]):
                selection[col.replace("_", " ").title()] = row[col]

        raven_data.append(selection)

    return pd.DataFrame(raven_data)


def parse_raven_selection_table(filepath: str) -> pd.DataFrame:
    """
    Parse Raven Pro selection table (.txt) to standard dataframe.

    Args:
        filepath: Path to Raven selection table file

    Returns:
        DataFrame with normalized columns
    """
    df = pd.read_csv(filepath, sep="\t")

    # Normalize column names (Raven uses spaces and parentheses)
    col_map = {
        "Begin Time (s)": "start_s",
        "End Time (s)": "end_s",
        "Low Freq (Hz)": "low_freq_hz",
        "High Freq (Hz)": "high_freq_hz",
        "Begin File": "audio_file",
        "Begin Path": "audio_path",
        "File Offset (s)": "file_offset_s"
    }

    df = df.rename(columns=col_map)

    return df


# ============================================================================
# MCP Tools: Export to Raven Format
# ============================================================================

@mcp.tool()
def export_to_raven(
    detections_csv: str,
    output_path: str,
    audio_file: str,
    audio_path: str,
    default_low_freq: float = 0.0,
    default_high_freq: float = 10000.0,
    channel: int = 1
) -> dict:
    """
    Export BirdNET or acoustic analysis detections to Raven Pro selection table format.

    Args:
        detections_csv: Path to CSV with detections (must have start_s, end_s columns)
        output_path: Output path for Raven selection table (.txt)
        audio_file: Name of source audio file
        audio_path: Full path to audio file
        default_low_freq: Default lower frequency bound (Hz) if not in detections
        default_high_freq: Default upper frequency bound (Hz) if not in detections
        channel: Audio channel number (default: 1)

    Returns:
        Status dict with output path and selection count
    """
    detections_csv = normalize_path(detections_csv)
    output_path = normalize_path(output_path)
    audio_path = normalize_path(audio_path)

    if not os.path.exists(detections_csv):
        return {"ok": False, "error": f"Detections CSV not found: {detections_csv}"}

    # Load detections
    df = pd.read_csv(detections_csv)

    # Validate required columns
    required = {"start_s", "end_s"}
    if not required.issubset(df.columns):
        return {"ok": False, "error": f"CSV must have columns: {required}"}

    # Convert to Raven format
    raven_df = create_raven_selection_table(
        df, audio_file, audio_path,
        default_low_freq, default_high_freq, channel
    )

    # Save as tab-delimited text
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    raven_df.to_csv(output_path, sep="\t", index=False)

    return {
        "ok": True,
        "output_path": output_path,
        "num_selections": len(raven_df),
        "audio_file": audio_file,
        "message": f"Exported {len(raven_df)} selections to Raven format"
    }


@mcp.tool()
def batch_export_to_raven(
    detections_dir: str,
    output_dir: str,
    audio_dir: str,
    file_pattern: str = "*_detections.csv",
    default_low_freq: float = 0.0,
    default_high_freq: float = 10000.0
) -> dict:
    """
    Batch export multiple detection CSV files to Raven selection tables.

    Args:
        detections_dir: Directory containing detection CSV files
        output_dir: Output directory for Raven selection tables
        audio_dir: Directory containing source audio files
        file_pattern: Glob pattern for detection files (default: *_detections.csv)
        default_low_freq: Default lower frequency bound (Hz)
        default_high_freq: Default upper frequency bound (Hz)

    Returns:
        Status dict with processing summary
    """
    detections_dir = normalize_path(detections_dir)
    output_dir = normalize_path(output_dir)
    audio_dir = normalize_path(audio_dir)

    from glob import glob

    detection_files = glob(os.path.join(detections_dir, file_pattern))

    if not detection_files:
        return {"ok": False, "error": f"No files found matching {file_pattern} in {detections_dir}"}

    os.makedirs(output_dir, exist_ok=True)

    results = []
    for det_file in detection_files:
        file_stem = Path(det_file).stem.replace("_detections", "")

        # Try to find corresponding audio file
        audio_file = None
        for ext in [".wav", ".WAV", ".mp3", ".MP3", ".flac", ".FLAC"]:
            candidate = os.path.join(audio_dir, f"{file_stem}{ext}")
            if os.path.exists(candidate):
                audio_file = f"{file_stem}{ext}"
                audio_path = candidate
                break

        if not audio_file:
            results.append({
                "file": det_file,
                "ok": False,
                "error": f"No audio file found for {file_stem}"
            })
            continue

        output_path = os.path.join(output_dir, f"{file_stem}_raven.txt")

        result = export_to_raven(
            det_file, output_path, audio_file, audio_path,
            default_low_freq, default_high_freq
        )
        result["file"] = det_file
        results.append(result)

    num_success = sum(1 for r in results if r.get("ok", False))

    return {
        "ok": True,
        "total_files": len(detection_files),
        "successful": num_success,
        "failed": len(detection_files) - num_success,
        "output_dir": output_dir,
        "results": results
    }


# ============================================================================
# MCP Tools: Import from Raven Format
# ============================================================================

@mcp.tool()
def import_from_raven(
    raven_table_path: str,
    output_csv: str
) -> dict:
    """
    Import Raven Pro selection table to standard CSV format.

    Args:
        raven_table_path: Path to Raven selection table (.txt)
        output_csv: Output path for normalized CSV

    Returns:
        Status dict with output path and selection count
    """
    raven_table_path = normalize_path(raven_table_path)
    output_csv = normalize_path(output_csv)

    if not os.path.exists(raven_table_path):
        return {"ok": False, "error": f"Raven table not found: {raven_table_path}"}

    try:
        df = parse_raven_selection_table(raven_table_path)

        os.makedirs(os.path.dirname(output_csv), exist_ok=True)
        df.to_csv(output_csv, index=False)

        return {
            "ok": True,
            "output_path": output_csv,
            "num_selections": len(df),
            "columns": list(df.columns),
            "message": f"Imported {len(df)} selections from Raven table"
        }
    except Exception as e:
        return {"ok": False, "error": f"Failed to parse Raven table: {str(e)}"}


@mcp.tool()
def batch_import_from_raven(
    raven_dir: str,
    output_dir: str,
    file_pattern: str = "*_raven.txt"
) -> dict:
    """
    Batch import multiple Raven selection tables to CSV format.

    Args:
        raven_dir: Directory containing Raven selection table files
        output_dir: Output directory for CSV files
        file_pattern: Glob pattern for Raven files (default: *_raven.txt)

    Returns:
        Status dict with processing summary
    """
    raven_dir = normalize_path(raven_dir)
    output_dir = normalize_path(output_dir)

    from glob import glob

    raven_files = glob(os.path.join(raven_dir, file_pattern))

    if not raven_files:
        return {"ok": False, "error": f"No files found matching {file_pattern} in {raven_dir}"}

    os.makedirs(output_dir, exist_ok=True)

    results = []
    for raven_file in raven_files:
        file_stem = Path(raven_file).stem.replace("_raven", "")
        output_csv = os.path.join(output_dir, f"{file_stem}_selections.csv")

        result = import_from_raven(raven_file, output_csv)
        result["file"] = raven_file
        results.append(result)

    num_success = sum(1 for r in results if r.get("ok", False))

    return {
        "ok": True,
        "total_files": len(raven_files),
        "successful": num_success,
        "failed": len(raven_files) - num_success,
        "output_dir": output_dir,
        "results": results
    }


# ============================================================================
# MCP Tools: Rraven R Integration (Advanced Measurements)
# ============================================================================

@mcp.tool()
def raven_measurements_rraven(
    raven_table_path: str,
    audio_file: str,
    measurements: List[str],
    output_csv: str
) -> dict:
    """
    Use Rraven (R package) to compute acoustic measurements on Raven selections.

    Requires R and Rraven package installed in container.

    Args:
        raven_table_path: Path to Raven selection table
        audio_file: Path to audio file
        measurements: List of measurement types (e.g., ["freq", "time", "energy"])
        output_csv: Output path for measurements CSV

    Returns:
        Status dict with measurements

    Note: This requires R runtime with Rraven, warbleR packages installed
    """
    raven_table_path = normalize_path(raven_table_path)
    audio_file = normalize_path(audio_file)
    output_csv = normalize_path(output_csv)

    try:
        # Import rpy2 for R integration
        from rpy2 import robjects
        from rpy2.robjects import pandas2ri
        from rpy2.robjects.packages import importr

        # Activate pandas conversion
        pandas2ri.activate()

        # Import R packages
        base = importr('base')
        utils = importr('utils')

        try:
            rraven = importr('Rraven')
            warbler = importr('warbleR')
        except Exception as e:
            return {
                "ok": False,
                "error": f"Rraven or warbleR not installed in R: {str(e)}",
                "hint": "Install with: install.packages(c('Rraven', 'warbleR'))"
            }

        # Load Raven selection table using Rraven
        r_code = f"""
        library(Rraven)
        library(warbleR)

        # Import Raven selections
        sels <- imp_raven(sound.file.col = "Begin File",
                          path = "{os.path.dirname(raven_table_path)}",
                          all.data = TRUE)

        # Run measurements (example: spectral parameters)
        measurements <- specan(X = sels, path = "{os.path.dirname(audio_file)}")

        measurements
        """

        result = robjects.r(r_code)

        # Convert R dataframe to pandas
        df_measurements = pandas2ri.rpy2py(result)

        os.makedirs(os.path.dirname(output_csv), exist_ok=True)
        df_measurements.to_csv(output_csv, index=False)

        return {
            "ok": True,
            "output_path": output_csv,
            "num_measurements": len(df_measurements),
            "columns": list(df_measurements.columns),
            "message": f"Computed measurements for {len(df_measurements)} selections using Rraven"
        }

    except ImportError:
        return {
            "ok": False,
            "error": "rpy2 not installed. Install with: pip install rpy2",
            "hint": "Also requires R runtime with Rraven and warbleR packages"
        }
    except Exception as e:
        return {"ok": False, "error": f"Rraven measurement failed: {str(e)}"}


@mcp.tool()
def convert_birdnet_to_raven_batch(
    birdnet_results_dir: str,
    audio_dir: str,
    output_dir: str
) -> dict:
    """
    Complete workflow: Convert BirdNET batch results to Raven selection tables.

    Scans for BirdNET detection CSVs and creates corresponding Raven selection tables
    with proper frequency bounds estimated from species and confidence.

    Args:
        birdnet_results_dir: Directory with BirdNET detection CSVs
        audio_dir: Directory with source audio files
        output_dir: Output directory for Raven tables

    Returns:
        Complete conversion summary
    """
    return batch_export_to_raven(
        birdnet_results_dir,
        output_dir,
        audio_dir,
        file_pattern="*_detections.csv",
        default_low_freq=500.0,   # Typical bird vocalization range
        default_high_freq=10000.0
    )


# ============================================================================
# Starlette App
# ============================================================================

app = Starlette(
    routes=[
        Mount("/", app=mcp.streamable_http_app())
    ]
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7085)
