# BirdNET CSV Format Guide

Praven Pro works with standard BirdNET CSV output files. This guide explains the expected format and how to prepare your data.

---

## Required Columns

Praven Pro requires these core columns (flexible naming):

| Column Name | Variants Accepted | Description | Example |
|-------------|-------------------|-------------|---------|
| **Species/Common Name** | `common_name`, `Common name`, `Common_name`, `Species`, `species` | Bird species common name | `Spotted Crake` |
| **Confidence** | `Confidence`, `confidence` | Detection confidence (0.0-1.0) | `0.874` |
| **Start Time** | `start_s`, `Begin Time (s)`, `Start (s)` | Detection start time (seconds) | `15.0` |

---

## Optional Columns (Enable Auto-Detection)

These columns enable automatic date extraction (no manual input needed):

| Column Name | Description | Format | Example | Auto-Detection |
|-------------|-------------|--------|---------|----------------|
| `recording_date` | Recording date | YYYY-MM-DD | `2025-10-13` | ✅ Date auto-extracted |
| `recording_start_time` | Recording start time | HH:MM:SS | `11:37:53` | ✅ Time for weather |
| `absolute_timestamp` | Full timestamp | YYYY-MM-DD HH:MM:SS | `2025-10-13 11:38:08` | ✅ Date + time |
| `filename` | Audio file name | Various | `245AAA_20251013_113753.WAV` | ✅ Date parsed from name |

**With these columns present**, Praven Pro will:
- Extract date automatically from CSV
- Fetch weather data using GPS + extracted date/time
- No manual date entry required

---

## Standard BirdNET CSV Format

### BirdNET Analyzer (Recommended)

```csv
common_name,scientific_name,start_s,end_s,confidence,label,filename,recording_date,recording_start_time,absolute_timestamp
Spotted Crake,Porzana porzana,15.0,18.0,0.874,Porzana porzana_Spotted Crake,245AAA_20251013_113753.WAV,2025-10-13,11:37:53,2025-10-13 11:38:08
Common Snipe,Gallinago gallinago,42.0,45.0,0.923,Gallinago gallinago_Common Snipe,245AAA_20251013_113753.WAV,2025-10-13,11:37:53,2025-10-13 11:38:35
```

**✅ Fully compatible** - includes all optional columns for auto-detection

### BirdNET-Pi Export

```csv
Common name,Scientific name,Begin Time (s),End Time (s),Confidence,File
Spotted Crake,Porzana porzana,15.0,18.0,0.874,245AAA_20251013_113753.WAV
Common Snipe,Gallinago gallinago,42.0,45.0,0.923,245AAA_20251013_113753.WAV
```

**⚠️ Partially compatible** - will extract date from filename if formatted as `YYYYMMDD`

### Minimal Format (Manual Date Required)

```csv
common_name,confidence,start_s
Spotted Crake,0.874,15.0
Common Snipe,0.923,42.0
```

**⚠️ Basic compatibility** - requires manual date entry via `--date` flag

---

## How to Export from BirdNET Tools

### BirdNET Analyzer (Desktop)

1. Run analysis on audio files
2. Results automatically saved as CSV
3. Includes all required + optional columns
4. **Ready to use** - no modifications needed

### BirdNET-Pi (Raspberry Pi)

1. Web interface → Recordings
2. Select date range → Export CSV
3. Download results
4. **Ready to use** - date will be parsed from filename

### BirdNET-Lite (Python)

```python
# When calling BirdNET-Lite, ensure CSV export includes:
results_df = analyze_audio(file_path)
results_df['recording_date'] = '2025-10-13'
results_df['filename'] = os.path.basename(file_path)
results_df.to_csv('detections.csv', index=False)
```

---

## Column Name Flexibility

Praven Pro automatically maps common BirdNET column name variations:

| Standardized | Accepted Variants |
|--------------|-------------------|
| `common_name` | Common name, Common_name, common name, Species, species |
| `scientific_name` | Scientific name, Scientific_name, scientific name |
| `confidence` | Confidence |
| `start_time` | start_s, Begin Time (s), Start (s) |
| `end_time` | end_s, End Time (s), End (s) |
| `filename` | File, filename, file_name |

**No preprocessing needed** - just export from BirdNET and upload!

---

## Example CSV from Different Sources

### Full Featured (Best Practice)

```csv
common_name,scientific_name,start_s,end_s,confidence,filename,recording_date,absolute_timestamp
Spotted Crake,Porzana porzana,15.0,18.0,0.874,rec_20251013.WAV,2025-10-13,2025-10-13 11:38:08
Eurasian Bittern,Botaurus stellaris,120.0,123.0,0.612,rec_20251013.WAV,2025-10-13,2025-10-13 11:40:13
Water Rail,Rallus aquaticus,245.0,248.0,0.891,rec_20251013.WAV,2025-10-13,2025-10-13 11:42:18
```

**✅ Auto-extracts**: Date (2025-10-13), Habitat (GPS), Weather (GPS + date)

### Filename-Based Date

```csv
Common name,Confidence,Begin Time (s),File
Spotted Crake,0.874,15.0,245AAA_20251013_113753.WAV
Eurasian Bittern,0.612,120.0,245AAA_20251013_113753.WAV
```

**✅ Auto-extracts**: Date from filename (20251013 → 2025-10-13)

### Minimal (Requires Manual Date)

```csv
species,confidence,start_s
Spotted Crake,0.874,15.0
Eurasian Bittern,0.612,120.0
```

**⚠️ Requires**: `--date 2025-10-13` flag

---

## Validation Process

When you upload a CSV, Praven Pro:

1. **Reads CSV** - checks for required columns
2. **Maps column names** - handles variants automatically
3. **Extracts date** - tries:
   - `recording_date` column
   - `absolute_timestamp` column
   - `filename` column (parses YYYYMMDD pattern)
   - Manual `--date` flag (if none found)
4. **Validates format** - ensures required fields present

---

## Troubleshooting

### Error: "Missing required column: common_name"

**Cause**: CSV doesn't have a recognized species column

**Fix**: Ensure CSV has one of:
- `common_name` or `Common name`
- `species` or `Species`

**Example fix**:
```csv
# Before (not recognized)
bird_name,score,time
Spotted Crake,0.874,15.0

# After (recognized)
Common name,Confidence,Begin Time (s)
Spotted Crake,0.874,15.0
```

### Error: "Date must be in YYYY-MM-DD format"

**Cause**: Date couldn't be extracted from CSV, and no manual date provided

**Fix**: Add `--date` flag:
```bash
python validate.py detections.csv --lat 63.341 --lon 10.215 --date 2025-10-13
```

### Warning: "Could not extract date from CSV"

**Cause**: CSV doesn't have date columns, using fallback

**Fix**: Either:
1. Add `recording_date` column to CSV
2. Ensure `filename` contains date (YYYYMMDD)
3. Provide `--date` flag

---

## Best Practices

### ✅ DO:
- Use standard BirdNET Analyzer CSV format
- Include `recording_date` and `filename` columns
- Keep original BirdNET column names
- Export multiple recordings with timestamps

### ❌ DON'T:
- Rename standard columns unnecessarily
- Remove date/timestamp information
- Merge recordings from different dates without timestamps
- Use non-standard date formats

---

## Creating a Standardized CSV

If you're combining data from multiple sources:

```python
import pandas as pd

# Read various CSV formats
df1 = pd.read_csv('birdnet_export1.csv')
df2 = pd.read_csv('birdnet_export2.csv')

# Standardize column names
df1 = df1.rename(columns={
    'Common name': 'common_name',
    'Confidence': 'confidence',
    'Begin Time (s)': 'start_s',
    'File': 'filename'
})

# Add recording date
df1['recording_date'] = '2025-10-13'
df2['recording_date'] = '2025-10-14'

# Combine
combined = pd.concat([df1, df2])

# Export
combined.to_csv('standardized_detections.csv', index=False)
```

---

## Quick Reference

**Minimum required columns:**
```
common_name, confidence, start_s
```

**Recommended columns (enables auto-detection):**
```
common_name, confidence, start_s, end_s, filename, recording_date, absolute_timestamp
```

**Command to validate:**
```bash
# With auto-detection (CSV has date columns)
python validate.py detections.csv --lat 63.341 --lon 10.215

# With manual date (CSV missing date)
python validate.py detections.csv --lat 63.341 --lon 10.215 --date 2025-10-13
```

---

## Template CSV

Download a template CSV for reference:

```csv
common_name,scientific_name,start_s,end_s,confidence,filename,recording_date,absolute_timestamp
Spotted Crake,Porzana porzana,15.0,18.0,0.874,recording_20251013.WAV,2025-10-13,2025-10-13 11:38:08
```

Save this as `template.csv` and replace with your actual BirdNET detections.

---

## Summary

- **Standard BirdNET CSV formats work out-of-the-box**
- **Date auto-extraction eliminates manual input**
- **Column name flexibility handles different BirdNET versions**
- **Minimal format supported (with `--date` flag)**
- **No preprocessing needed for BirdNET Analyzer exports**

For questions or issues, see [GitHub Issues](https://github.com/Ziforge/praven-pro/issues).
