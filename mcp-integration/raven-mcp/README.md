# Raven Pro MCP Server

MCP server for **Raven Pro** bioacoustic analysis software integration. Provides bidirectional conversion between BirdNET/acoustic analysis formats and Raven Pro selection tables, plus advanced acoustic measurements via Rraven (R package).

## Features

- **Export to Raven**: Convert BirdNET detections → Raven selection tables
- **Import from Raven**: Parse Raven selection tables → standard CSV format
- **Batch Processing**: Process multiple files automatically
- **Rraven Integration**: Advanced acoustic measurements using R (requires R runtime)
- **Full Format Support**: Tab-delimited selection tables with frequency bounds and metadata

## MCP Tools

### Export Tools

#### `export_to_raven`
Convert detection CSV to Raven Pro selection table format.

**Parameters:**
- `detections_csv` (str): Path to CSV with detections (requires `start_s`, `end_s`)
- `output_path` (str): Output path for Raven selection table (.txt)
- `audio_file` (str): Name of source audio file
- `audio_path` (str): Full path to audio file
- `default_low_freq` (float): Lower frequency bound in Hz (default: 0.0)
- `default_high_freq` (float): Upper frequency bound in Hz (default: 10000.0)
- `channel` (int): Audio channel number (default: 1)

**Example:**
```json
{
  "detections_csv": "shared/bird_analysis/recording_001_detections.csv",
  "output_path": "shared/bird_analysis/recording_001_raven.txt",
  "audio_file": "recording_001.wav",
  "audio_path": "shared/audio/recording_001.wav",
  "default_low_freq": 500.0,
  "default_high_freq": 8000.0
}
```

#### `batch_export_to_raven`
Batch export multiple detection CSVs to Raven selection tables.

**Parameters:**
- `detections_dir` (str): Directory with detection CSV files
- `output_dir` (str): Output directory for Raven tables
- `audio_dir` (str): Directory with source audio files
- `file_pattern` (str): Glob pattern (default: `*_detections.csv`)
- `default_low_freq` (float): Lower frequency bound (default: 0.0)
- `default_high_freq` (float): Upper frequency bound (default: 10000.0)

### Import Tools

#### `import_from_raven`
Import Raven Pro selection table to standard CSV.

**Parameters:**
- `raven_table_path` (str): Path to Raven selection table (.txt)
- `output_csv` (str): Output path for normalized CSV

#### `batch_import_from_raven`
Batch import multiple Raven selection tables.

**Parameters:**
- `raven_dir` (str): Directory with Raven tables
- `output_dir` (str): Output directory for CSVs
- `file_pattern` (str): Glob pattern (default: `*_raven.txt`)

### Advanced Measurements (Rraven)

#### `raven_measurements_rraven`
Compute acoustic measurements using Rraven R package.

**Parameters:**
- `raven_table_path` (str): Path to Raven selection table
- `audio_file` (str): Path to audio file
- `measurements` (list): Measurement types (e.g., `["freq", "time", "energy"]`)
- `output_csv` (str): Output path for measurements CSV

**Requirements:** R runtime with `Rraven` and `warbleR` packages installed.

### Workflow Tools

#### `convert_birdnet_to_raven_batch`
Complete BirdNET → Raven workflow.

**Parameters:**
- `birdnet_results_dir` (str): Directory with BirdNET CSVs
- `audio_dir` (str): Directory with audio files
- `output_dir` (str): Output directory for Raven tables

## Raven Selection Table Format

Raven Pro uses **tab-delimited text files** with the following columns:

| Column | Description |
|--------|-------------|
| `Selection` | Selection ID (integer) |
| `View` | View name (e.g., "Spectrogram 1") |
| `Channel` | Audio channel (1-indexed) |
| `Begin Time (s)` | Start time in seconds |
| `End Time (s)` | End time in seconds |
| `Low Freq (Hz)` | Lower frequency bound |
| `High Freq (Hz)` | Upper frequency bound |
| `Begin File` | Source audio filename |
| `Begin Path` | Full path to audio file |
| `File Offset (s)` | Time offset (for multi-file tables) |

Additional metadata columns (e.g., `Common Name`, `Confidence`) are supported.

## Docker Service

### Ports
- **7085**: MCP/HTTP endpoint

### Volumes
- `/workspace/shared`: Shared workspace for audio files and results

### Dependencies
- Python 3.11
- R runtime with bioacoustic packages
- pandas, numpy, rpy2

## Usage Examples

### Via HTTP API (Port 8080)

**Export BirdNET results to Raven:**
```bash
curl -X POST http://localhost:8080/raven/export \
  -H "Content-Type: application/json" \
  -d '{
    "detections_csv": "shared/bird_analysis/gaulossen_001_detections.csv",
    "output_path": "shared/bird_analysis/gaulossen_001_raven.txt",
    "audio_file": "gaulossen_001.wav",
    "audio_path": "shared/audio/gaulossen_001.wav",
    "default_low_freq": 500.0,
    "default_high_freq": 8000.0
  }'
```

**Batch export:**
```bash
curl -X POST http://localhost:8080/raven/export_batch \
  -H "Content-Type: application/json" \
  -d '{
    "detections_dir": "shared/bird_analysis/csvs",
    "output_dir": "shared/bird_analysis/raven_tables",
    "audio_dir": "shared/audio",
    "default_low_freq": 500.0,
    "default_high_freq": 8000.0
  }'
```

**Import from Raven:**
```bash
curl -X POST http://localhost:8080/raven/import \
  -H "Content-Type: application/json" \
  -d '{
    "raven_table_path": "shared/bird_analysis/manual_annotations_raven.txt",
    "output_csv": "shared/bird_analysis/manual_annotations.csv"
  }'
```

### Via Direct MCP (Port 7085)

```bash
curl -X POST http://localhost:7085/run/export_to_raven \
  -H "Content-Type: application/json" \
  -d '{
    "detections_csv": "shared/bird_analysis/recording_001_detections.csv",
    "output_path": "shared/bird_analysis/recording_001_raven.txt",
    "audio_file": "recording_001.wav",
    "audio_path": "shared/audio/recording_001.wav"
  }'
```

### In Jupyter Notebook

The bird analysis notebook (`/Users/georgeredpath/Dev/bird-net-batch-analysis`) includes built-in Raven export in **Cell 2b** (optional cell after BirdNET analysis).

Simply run the cell to export all BirdNET detections to Raven format automatically.

## Using Raven Selection Tables in Raven Pro

1. **Open Raven Pro**
2. **File → Open Selection Table**
3. **Select the `*_raven.txt` file**
4. Raven will load the audio file and display all selections with time/frequency boxes

You can then:
- View spectrograms for each detection
- Run Raven's built-in measurements
- Edit/annotate selections
- Export modified tables back to CSV

## R/Rraven Setup (Optional)

For advanced acoustic measurements, install R packages:

```R
install.packages(c("Rraven", "warbleR", "seewave", "tuneR", "monitoR"))
```

The Dockerfile includes these packages automatically when building the service.

## Example Files

See `/shared/raven_examples/` for:
- `example_birdnet_detections.csv` - Sample BirdNET CSV
- `example_raven_table.txt` - Sample Raven selection table

## Troubleshooting

### "Rraven not installed" error
The R integration requires R runtime with Rraven. The Docker image includes this, but if running locally:
```bash
pip install rpy2
R -e "install.packages(c('Rraven', 'warbleR'))"
```

### Raven can't find audio files
Ensure `Begin Path` in the selection table points to the correct absolute path. Use `audio_path` parameter with full container path:
```
/workspace/shared/audio/yourfile.wav
```

### Tab delimiter issues
Raven requires **tab-delimited** files (not CSV). This server generates proper tab-delimited `.txt` files automatically.

## Integration with NTNU Project

For the Gaulossen bird recording project:

1. **Run BirdNET analysis** (Jupyter notebook Cell 2)
2. **Run Raven export** (Jupyter notebook Cell 2b)
3. **Open in Raven Pro** for manual verification/annotation
4. **Export from Raven** if you make changes
5. **Import back** using `import_from_raven` tool

This workflow allows you to combine automated BirdNET detection with expert manual review in Raven Pro.

## References

- [Raven Pro Software](https://www.ravensoundsoftware.com/)
- [Rraven R Package](https://marce10.github.io/Rraven/)
- [Cornell Lab of Ornithology](https://www.birds.cornell.edu/ccb/)

## License

MIT License - See repository root for details.
