# Praven Pro - Example Scripts

This directory contains example scripts demonstrating advanced usage of Praven Pro.

## Scripts

### automated_batch_analysis.py

**Purpose:** Automated processing of large multi-hour audio recordings with timestamp extraction.

**Use Case:** Field recordings from autonomous recorders (AudioMoth, Wildlife Acoustics, etc.) that embed timestamps in filenames.

**Features:**
- 🕒 Automatic timestamp extraction from filenames
- 📊 Batch processing of multiple large files
- 💾 Multiple output formats (CSV, Audacity labels, Raven tables)
- ⏱️ Absolute timestamp calculation for each detection
- 📈 Progress tracking and detailed logging
- 🧠 Memory-efficient handling of multi-gigabyte files

**Expected Filename Format:**
```
DeviceID_YYYYMMDD_HHMMSS.WAV

Example:
245AAA0563ED3DA7_20251013_113753.WAV
  - Device: 245AAA0563ED3DA7
  - Date: October 13, 2025
  - Time: 11:37:53
```

**Usage:**

1. **Configure the script** (edit top of file):
   ```python
   # Your recording location
   LAT = 63.4305  # Latitude
   LON = 10.3951  # Longitude

   # BirdNET settings
   MIN_CONF = 0.25  # Confidence threshold

   # Customize filename pattern if needed
   FILENAME_PATTERN = r'([A-F0-9]+)_(\d{8})_(\d{6})\.WAV'
   ```

2. **Place audio files:**
   ```bash
   mkdir audio_files
   cp /path/to/recordings/*.WAV audio_files/
   ```

3. **Run the script:**
   ```bash
   python examples/automated_batch_analysis.py
   ```

4. **Check results:**
   ```bash
   ls -lh results/
   # results/csvs/ - Detection CSVs with absolute timestamps
   # results/raven_tables/ - Raven Pro selection tables
   # results/labels/ - Audacity label files
   # results/all_detections.csv - Master file
   # results/species_summary.csv - Species counts
   ```

**Output Files:**

Each audio file generates:
- `filename_detections.csv` - All detections with timestamps
- `filename_labels.txt` - Audacity-compatible labels
- `filename_raven.txt` - Raven Pro selection table

Plus master files:
- `all_detections.csv` - Combined detections from all files
- `file_summary.csv` - Statistics per file
- `species_summary.csv` - Species occurrence counts

**Absolute Timestamps:**

The script calculates absolute timestamps for each detection:

```
Recording start: 2025-10-13 11:37:53
Detection at: 125.3 seconds into recording
Absolute timestamp: 2025-10-13 11:40:08
```

This is crucial for:
- Correlating detections with field observations
- Analyzing temporal patterns (dawn chorus, etc.)
- Linking to environmental data (weather, temperature)

**Customizing Filename Pattern:**

If your device uses a different filename format, update the regex pattern:

```python
# AudioMoth format: YYYYMMDD_HHMMSS.WAV
FILENAME_PATTERN = r'(\d{8})_(\d{6})\.WAV'

# Wildlife Acoustics: PREFIX_YYYYMMDD_HHMMSS.WAV
FILENAME_PATTERN = r'([A-Z]+)_(\d{8})_(\d{6})\.WAV'

# Custom format with milliseconds: ID_YYYYMMDD_HHMMSS_mmm.WAV
FILENAME_PATTERN = r'(\w+)_(\d{8})_(\d{6})_\d{3}\.WAV'
```

**Performance:**

Typical processing times (on modern laptop):
- **12-hour file:** ~60 minutes
- **24-hour file:** ~120 minutes
- **4GB file:** ~50-70 minutes

Processing speed depends on:
- CPU performance
- Using location context (faster with LAT/LON)
- Confidence threshold (lower = more detections = slower)

**Memory Usage:**

The script processes files sequentially to minimize memory usage:
- **Recommended:** 8GB RAM
- **Minimum:** 4GB RAM
- Large files (>4GB) benefit from 16GB+ RAM

**Troubleshooting:**

**Issue:** "No audio files found"
```bash
# Check AUDIO_DIR path
ls audio_files/
```

**Issue:** "Could not parse timestamp from filename"
```bash
# Script will fall back to file modification time
# Or customize FILENAME_PATTERN for your format
```

**Issue:** Out of memory
```python
# Process fewer files at once
# Or increase MIN_CONF to reduce detections:
MIN_CONF = 0.35  # Higher threshold
```

**Issue:** Analysis very slow
```python
# Ensure location context is set (much faster):
LAT = YOUR_LATITUDE
LON = YOUR_LONGITUDE

# Or increase confidence threshold:
MIN_CONF = 0.30
```

## Integration with Main Workflow

This script complements the Jupyter notebook workflow:

| Workflow | Best For |
|----------|----------|
| **Jupyter Notebook** | Interactive analysis, exploration, visualization |
| **Automated Script** | Batch processing, scheduled runs, large datasets |

**Combined Approach:**
1. Use automated script to process all files
2. Import results into Jupyter for visualization and analysis
3. Export to Raven Pro for expert verification

## Example: Multi-Day Field Survey

```bash
# Day 1: Deploy recorder
# ... recording runs for 3 days ...

# Day 4: Collect recorder, copy files
cp /media/SD_CARD/*.WAV audio_files/

# Process all files
python examples/automated_batch_analysis.py

# View summary
cat results/species_summary.csv

# Open best detections in Raven Pro
# results/raven_tables/*.txt
```

## Advanced: Integration with External Data

The absolute timestamps enable correlation with external data:

```python
import pandas as pd

# Load detections
detections = pd.read_csv('results/all_detections.csv')
detections['absolute_timestamp'] = pd.to_datetime(detections['absolute_timestamp'])

# Load weather data (example)
weather = pd.read_csv('weather_data.csv')
weather['timestamp'] = pd.to_datetime(weather['timestamp'])

# Merge on timestamp (within 1-minute window)
merged = pd.merge_asof(
    detections.sort_values('absolute_timestamp'),
    weather.sort_values('timestamp'),
    left_on='absolute_timestamp',
    right_on='timestamp',
    tolerance=pd.Timedelta('1min')
)

# Analyze: Do certain species appear more in certain conditions?
print(merged.groupby('common_name')['temperature'].mean())
```

## Contributing

Have an example script to share? Submit a pull request!

Good examples:
- Species-specific analysis
- Temporal pattern analysis
- Multi-location comparison
- Integration with R/ecological analysis

## Support

For questions or issues with example scripts:
- Open an issue: https://github.com/Ziforge/praven-pro/issues
- Tag with: `examples` label
