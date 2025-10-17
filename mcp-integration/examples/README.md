# MCP API Examples

This directory contains practical examples for using the Praven Pro MCP API.

## Prerequisites

1. **Start the MCP services:**
   ```bash
   cd mcp-integration
   docker compose up -d
   ```

2. **Verify services are running:**
   ```bash
   bash examples/check_health.sh
   ```

## Python Examples

### 1. Export Single File
Convert one detection CSV to Raven Pro format:

```bash
python3 examples/export_single_file.py
```

**What it does:**
- Reads BirdNET detection CSV
- Converts to Raven Pro selection table format (tab-delimited .txt)
- Adds frequency bounds and file paths

### 2. Batch Export
Export all detection CSVs at once:

```bash
python3 examples/batch_export.py
```

**What it does:**
- Finds all `*_detections.csv` files
- Converts each to Raven Pro format
- Processes multiple files in parallel

### 3. Import from Raven
Import refined Raven tables back to CSV:

```bash
python3 examples/import_from_raven.py
```

**What it does:**
- Reads Raven Pro selection table
- Converts back to standard CSV format
- Useful after manual refinement in Raven Pro

### 4. Complete Workflow
Interactive example showing the full analysis pipeline:

```bash
python3 examples/workflow_example.py
```

**What it does:**
- Guides you through all steps
- BirdNET analysis → Raven export → Manual review → Import refined data
- Shows realistic bioacoustics workflow

## Shell Script Examples

### Check Health
Verify MCP services are running:

```bash
bash examples/check_health.sh
```

### Batch Export (curl)
Export all detections using curl:

```bash
bash examples/export_all.sh
```

## Customizing Examples

All examples use `/workspace/shared/` paths (Docker container paths). These map to:

| Container Path | Host Path |
|---------------|-----------|
| `/workspace/shared/audio` | `praven-pro/audio_files/` |
| `/workspace/shared/results` | `praven-pro/results/` |

To modify for your files, edit the paths in each example script.

## API Endpoints

The examples use these API endpoints:

- `POST /raven/export` - Export single CSV to Raven
- `POST /raven/export_batch` - Batch export multiple CSVs
- `POST /raven/import` - Import Raven table to CSV
- `GET /health` - Check API status

**Full API documentation:** See [`../README.md`](../README.md)

## Troubleshooting

### "Connection refused"
Services aren't running. Start them:
```bash
cd mcp-integration
docker compose up -d
```

### "File not found"
Check that paths exist inside the container:
```bash
docker exec -it praven-raven-mcp ls /workspace/shared/results/csvs
```

### "Permission denied"
Fix permissions on results directory:
```bash
chmod -R 777 results/
```

## Integration into Your Code

Copy any example script and modify it for your needs:

```python
import requests

def export_my_data():
    response = requests.post(
        "http://localhost:8080/raven/export",
        json={
            "detections_csv": "/workspace/shared/results/csvs/my_file.csv",
            "output_path": "/workspace/shared/results/raven_tables/my_file.txt",
            "audio_file": "my_file.wav",
            "audio_path": "/workspace/shared/audio/my_file.wav",
            "default_low_freq": 500.0,
            "default_high_freq": 8000.0,
        }
    )
    return response.json()
```

## Next Steps

1. Try running `workflow_example.py` for a guided tour
2. Modify examples for your specific files
3. Integrate into your existing analysis pipelines
4. See main documentation for advanced features (R/Rraven measurements)
