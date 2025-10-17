# Praven Pro 🐦

### **Pra**ven = Python + Raven | प्रवीण (pravīṇa) = Skilled

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![BirdNET](https://img.shields.io/badge/BirdNET-v0.18-green.svg)](https://github.com/kahst/BirdNET-Analyzer)
[![Raven Pro](https://img.shields.io/badge/Raven%20Pro-Compatible-orange.svg)](https://www.ravensoundsoftware.com/)

**A skilled bioacoustics workflow combining Python automation with Raven Pro's professional analysis tools.**

Comprehensive Jupyter notebook-based system for batch processing of bird audio recordings using **BirdNET** for automated species identification, with seamless export to **Raven Pro** selection tables for expert-level bioacoustic analysis.

**Originally developed for:** NTNU Bioacoustics Research - Gaulossen Field Recordings (May 13-15, 2025)

## Why Praven Pro?

### The Problem
Field researchers often record **hours of bird audio**, but manually analyzing it is extremely time-consuming. Listening through 10 hours of recordings to identify species and mark interesting sounds could take **40+ hours of expert time**.

### The Solution: Skilled Automation + Expert Verification

```mermaid
graph LR
    A[10 Hours of Audio] -->|Manual Analysis| B[40+ Hours of Work]
    A -->|Praven Pro| C[1 Hour Total]

    C --> C1[30 min: Automated<br/>BirdNET scanning]
    C --> C2[30 min: Expert review<br/>in Raven Pro]

    style A stroke:#2563eb,stroke-width:3px
    style B stroke:#dc2626,stroke-width:3px
    style C stroke:#16a34a,stroke-width:3px
```

**Praven Pro automates the tedious 95%** (scanning audio, marking detections, extracting features) **so you can focus your expert time on the critical 5%** (verification, analysis, interpretation).

### Best of Three Worlds

| Component | Purpose | Benefit |
|-----------|---------|---------|
| **🤖 BirdNET AI** | Automated species ID | 100x faster than manual scanning |
| **🐍 Python Analysis** | Feature extraction | Quantitative acoustic data (F0, formants) |
| **🦅 Raven Pro Export** | Expert verification | Professional tools for refinement |

### Who Should Use This?

✅ **Field Biologists** - Process field recordings efficiently
✅ **Acoustic Ecologists** - Batch process entire field seasons
✅ **Conservation Projects** - Monitor biodiversity at scale
✅ **Graduate Students** - Learn bioacoustics with real data
✅ **Raven Pro Users** - Automate pre-processing before manual review

### Real Example: Multi-Hour Recordings

**Gaulossen Field Survey (3 days, ~24 hours of audio):**

❌ **Without Praven Pro:**
- 100+ hours of manual listening
- Risk missing rare species in background
- Limited quantitative acoustic data
- Slow turnaround for reports

✅ **With Praven Pro:**
- 2 hours: Automated BirdNET processing → 200+ detections
- 2 hours: Expert verification in Raven Pro
- **Total: 4 hours instead of 100+**
- CSV data ready for statistical analysis
- Publication-ready spectrograms included

### Key Advantages

🚀 **Massive Time Savings** - Process audio 25x faster than manual analysis
🎯 **High Accuracy** - AI detection + human verification = best results
📊 **Multiple Outputs** - Audacity labels, Raven tables, CSV data, visualizations
💾 **Large File Support** - Memory-efficient processing for multi-gigabyte recordings
🔬 **Academic-Ready** - Proper citations, MIT license, reproducible workflow
🆓 **Open Source** - Free to use, modify, and share

## Features

- **Batch Processing**: Analyze multiple audio files without merging
- **BirdNET Integration**: Automatic bird species identification with confidence scores
- **Raven Pro Export**: Convert detections to Raven Pro selection tables (NEW!)
- **Proper File Management**: Each file analyzed separately with organized outputs
- **Audacity Labels**: Generate label tracks for each audio file (importable into Audacity)
- **Detailed Visualizations**:
  - Waveforms and spectrograms for each detection
  - F0 (fundamental frequency) estimation
  - Formant analysis (F1, F2, F3)
  - Species summary charts
- **Comprehensive Reports**:
  - Master CSV with all detections
  - Per-file CSVs
  - File summary with statistics
  - Detection metrics (F0, formants, spectral features)
- **Large File Support**: Memory-efficient processing for multi-hour recordings

## Workflow Overview

```mermaid
graph LR
    A[Audio Files<br/>WAV/MP3/FLAC] -->|Cell 1: Config| B[BirdNET Analysis<br/>Species ID]
    B -->|Cell 2| C[Detections CSV<br/>+ Audacity Labels]
    C -->|Cell 2b| D[Raven Pro<br/>Selection Tables]
    C -->|Cell 3| E[Visualizations<br/>F0/Formants]
    C -->|Cell 4| F[Summary<br/>Statistics]

    style A stroke:#2563eb,stroke-width:3px
    style B stroke:#16a34a,stroke-width:3px
    style C stroke:#9333ea,stroke-width:3px
    style D stroke:#ea580c,stroke-width:3px
    style E stroke:#0891b2,stroke-width:3px
    style F stroke:#dc2626,stroke-width:3px
```

## Analysis Pipeline

```mermaid
flowchart TD
    Start([Field Recordings]) --> Load[Load Audio Files]
    Load --> BirdNET{BirdNET<br/>Deep Learning}
    BirdNET -->|Confidence > 0.25| Detect[Valid Detections]
    BirdNET -->|Confidence < 0.25| Reject[Filtered Out]

    Detect --> Process[Process Each Detection]
    Process --> F0[F0 Estimation<br/>librosa.pyin]
    Process --> Formants[Formant Analysis<br/>LPC Method]
    Process --> Spec[Spectrogram<br/>Generation]

    F0 --> Outputs
    Formants --> Outputs
    Spec --> Outputs

    Outputs[Multiple Outputs] --> CSV[CSV Files<br/>Detections + Metrics]
    Outputs --> Audacity[Audacity Labels<br/>Time Regions]
    Outputs --> Raven[Raven Pro Tables<br/>Selection Tables]
    Outputs --> Viz[PNG Images<br/>Spectrograms]

    CSV --> End([Research Dataset])
    Audacity --> End
    Raven --> End
    Viz --> End

    style Start stroke:#2563eb,stroke-width:3px
    style BirdNET stroke:#16a34a,stroke-width:3px
    style Detect stroke:#9333ea,stroke-width:3px
    style Outputs stroke:#ea580c,stroke-width:3px
    style End stroke:#dc2626,stroke-width:3px
```

## Data Flow

```mermaid
graph TD
    subgraph Input["Input Layer"]
        A1[recording_001.wav]
        A2[recording_002.wav]
        A3[recording_003.wav]
    end

    subgraph Processing["Processing Layer"]
        B[BirdNET Analysis]
        C[Acoustic Feature Extraction]
    end

    subgraph Output["Output Layer"]
        D1[all_detections.csv<br/>Master CSV]
        D2[Audacity Labels<br/>Per-file .txt]
        D3[Raven Tables<br/>Per-file .txt]
        D4[Spectrograms<br/>Per-detection PNG]
        D5[Summary Charts<br/>Species counts]
    end

    A1 --> B
    A2 --> B
    A3 --> B
    B --> C
    C --> D1
    C --> D2
    C --> D3
    C --> D4
    C --> D5

    style Input stroke:#2563eb,stroke-width:3px
    style Processing stroke:#16a34a,stroke-width:3px
    style Output stroke:#ea580c,stroke-width:3px
```

## Raven Pro Integration

```mermaid
sequenceDiagram
    participant User
    participant Jupyter as Jupyter Notebook
    participant BirdNET
    participant Praven as Praven Converter
    participant Raven as Raven Pro

    User->>Jupyter: Cell 2: Run BirdNET Analysis
    Jupyter->>BirdNET: Process audio files
    BirdNET-->>Jupyter: Return detections
    Jupyter->>Jupyter: Save detections CSV

    User->>Jupyter: Cell 2b: Export to Raven
    Jupyter->>Praven: Convert detections
    Note over Praven: Add frequency bounds<br/>Format as tab-delimited<br/>Include file paths
    Praven-->>Jupyter: Raven selection tables
    Jupyter->>Jupyter: Save .txt files

    User->>Raven: Open selection table
    Raven->>Raven: Load audio + selections
    Note over Raven: View spectrograms<br/>Run measurements<br/>Manual refinement
    Raven-->>User: Professional analysis

    rect rgb(37, 99, 235, 0.1)
        Note over Jupyter,Praven: Python Automation
    end
    rect rgb(234, 88, 12, 0.1)
        Note over Raven: Professional Analysis
    end
```

## Project Structure

```
praven-pro/
├── audio_files/          # Place your WAV/MP3 files here
├── results/              # All outputs go here
│   ├── labels/          # Audacity label files (one per audio file)
│   ├── raven_tables/    # Raven Pro selection tables (NEW!)
│   ├── visualizations/  # Spectrogram/waveform plots
│   ├── csvs/            # Per-file detection CSVs
│   ├── all_detections.csv
│   ├── file_summary.csv
│   ├── detections_with_metrics.csv
│   └── species_summary.png
├── notebooks/
│   └── bird_audio_batch_analysis.ipynb
├── requirements.txt
└── README.md
```

## Setup Instructions

### 1. Prerequisites

- **Python 3.8-3.11** (BirdNET requires TensorFlow which works best with these versions)
- **Jupyter Notebook or JupyterLab**
- **macOS, Linux, or Windows**

### 2. Installation

Clone or download this repository, then install dependencies:

```bash
cd praven-pro

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Add Your Audio Files

Place your audio recordings in the `audio_files/` directory:

```bash
cp /path/to/your/recordings/*.wav audio_files/
```

Supported formats: WAV, MP3, FLAC, OGG, M4A

### 4. Launch Jupyter

```bash
jupyter notebook notebooks/bird_audio_batch_analysis.ipynb
```

or

```bash
jupyter lab
# Then navigate to notebooks/bird_audio_batch_analysis.ipynb
```

## Usage

### Quick Start

1. **Open the notebook** in Jupyter
2. **Cell 1: Configuration**
   - Set `AUDIO_DIR` (default: `../audio_files`)
   - Set `FILE_PATTERN` (e.g., `*.wav`, `*.mp3`, or `*` for all)
   - Configure BirdNET parameters (location, date, confidence threshold)
   - Adjust F0 range for your target species
   - Run the cell
3. **Cell 2: BirdNET Analysis**
   - Processes each file individually
   - Generates Audacity labels and per-file CSVs
   - Run the cell (this will take time for large files)
4. **Cell 3: Visualizations**
   - Creates spectrograms with F0 overlay
   - Estimates formants (F1, F2, F3)
   - Run the cell
5. **Cell 4: Summary Statistics**
   - View species counts and file breakdown
   - Generate species summary chart
   - Run the cell

### Configuration Options

#### BirdNET Settings (Cell 1)

```python
MIN_CONF = 0.25  # Confidence threshold (0.0-1.0)
                 # Higher = fewer false positives, may miss some birds
                 # Lower = more detections, more false positives

# Location context (helps filter to regionally appropriate species)
LAT = 63.4305    # Gaulossen latitude
LON = 10.3951    # Gaulossen longitude
DATE = "2025-05-15"  # Recording date (YYYY-MM-DD)

# Optional species filter
SPECIES_FILTER = None  # Set to list of species names to filter
# Example: ["Common Chaffinch", "Eurasian Blue Tit"]
```

#### F0 Analysis Range

Adjust based on expected bird species pitch range:

```python
F0_MIN_HZ = 500.0   # Lower bound (Hz)
F0_MAX_HZ = 8000.0  # Upper bound (Hz)

# Typical ranges:
# - Small songbirds: 2000-8000 Hz
# - Medium songbirds: 500-4000 Hz
# - Large birds/waterfowl: 100-2000 Hz
```

#### Visualization Settings

```python
PAD_BEFORE_S = 0.3  # Context before detection (seconds)
PAD_AFTER_S = 0.3   # Context after detection (seconds)
MAX_DETECTIONS_PER_FILE = None  # Limit visualizations per file (None = all)
```

## Output Files

### Labels Directory (`results/labels/`)

Audacity-compatible label files (`.txt`) for each audio file:

```
filename_labels.txt
```

**To use in Audacity:**
1. Open your audio file in Audacity
2. Go to **File → Import → Labels...**
3. Select the corresponding `_labels.txt` file
4. Labels will appear as regions on a label track

### Visualizations Directory (`results/visualizations/`)

PNG images for each detection:

```
filename_det0001_Common_Chaffinch.png
filename_det0002_Eurasian_Blue_Tit.png
```

Each image contains:
- Waveform (top)
- Spectrogram with F0 overlay (bottom)
- Acoustic metrics (F0, F1, F2, F3)

### CSV Files

#### `all_detections.csv`

Master file with all detections across all files:

| Column | Description |
|--------|-------------|
| `file_index` | File number (1, 2, 3...) |
| `filename` | Original audio filename |
| `file_stem` | Filename without extension |
| `start_s` | Detection start time (seconds) |
| `end_s` | Detection end time (seconds) |
| `common_name` | Bird species common name |
| `scientific_name` | Bird species scientific name |
| `confidence` | BirdNET confidence (0.0-1.0) |
| `label` | BirdNET internal label |

#### `file_summary.csv`

Summary statistics per file:

| Column | Description |
|--------|-------------|
| `file_index` | File number |
| `filename` | Audio filename |
| `num_detections` | Number of detections in file |
| `unique_species` | Number of unique species detected |
| `label_file` | Path to Audacity label file |

#### `detections_with_metrics.csv`

All detections with acoustic analysis metrics:

Additional columns beyond `all_detections.csv`:

| Column | Description |
|--------|-------------|
| `f0_mean` | Mean fundamental frequency (Hz) |
| `F1` | First formant estimate (Hz) |
| `F2` | Second formant estimate (Hz) |
| `F3` | Third formant estimate (Hz) |
| `visualization_path` | Path to PNG visualization |

#### Per-file CSVs (`results/csvs/`)

Individual CSV files for each audio file with detections from that file only.

### Species Summary Chart (`species_summary.png`)

Bar chart showing top 20 detected species with detection counts.

## Tips for Large Files

### Memory Management

For very large files (>1GB), the notebook processes files individually to minimize memory usage. However, visualization generation loads entire files. If you encounter memory issues:

1. **Limit visualizations:**
   ```python
   MAX_DETECTIONS_PER_FILE = 50  # Only visualize first 50 per file
   ```

2. **Process files in batches:**
   - Move files to `audio_files/` in smaller groups
   - Run the notebook multiple times
   - Results will accumulate in `results/`

3. **Skip visualization cell:**
   - Run Cells 1-2 for analysis only
   - Skip Cell 3 to save time/memory

### Processing Time

BirdNET analysis time depends on:
- File duration
- Confidence threshold (lower = more detections = slower)
- Location context (with LAT/LON = faster due to species filtering)

**Approximate times** (on modern laptop):
- 1 hour audio: 3-5 minutes analysis
- 10 hours audio: 30-50 minutes analysis
- Visualization: ~2-3 seconds per detection

## Troubleshooting

### ImportError: No module named 'birdnetlib'

```bash
pip install birdnetlib==0.18.0
```

### TensorFlow compatibility issues

BirdNET requires TensorFlow 2.x. Use Python 3.8-3.11:

```bash
python3 --version  # Should be 3.8, 3.9, 3.10, or 3.11
pip install tensorflow==2.15.0
```

### "No audio files found"

- Check `AUDIO_DIR` path in Cell 1
- Verify `FILE_PATTERN` matches your files
- Ensure files are in `audio_files/` directory

### Out of memory errors

- Reduce `MAX_DETECTIONS_PER_FILE`
- Process fewer files at once
- Close other applications
- Use a machine with more RAM

### BirdNET downloading models

First run will download ~100MB of model files. This is normal and only happens once.

## Citation & Credit

**Author:** George Redpath (2025)
**License:** MIT License

If you use this code in your research, please credit:

```bibtex
@software{redpath2025praven,
  author = {Redpath, George},
  title = {Praven Pro: Skilled Bioacoustics Analysis with Python and Raven},
  year = {2025},
  url = {https://github.com/georgeredpath/praven-pro}
}
```

Or cite using the `CITATION.cff` file in this repository.

### BirdNET Citation

This project uses BirdNET for species identification:

```
@article{kahl2021birdnet,
  title={BirdNET: A deep learning solution for avian diversity monitoring},
  author={Kahl, Stefan and Wood, Connor M and Eibl, Maximilian and Klinck, Holger},
  journal={Ecological Informatics},
  volume={61},
  pages={101236},
  year={2021},
  publisher={Elsevier}
}
```

## License

MIT License

Copyright (c) 2025 George Redpath

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Contact

For questions about this project, please contact George Redpath or open an issue on GitHub.

## Acknowledgments

- **NTNU** (Norwegian University of Science and Technology) - Acoustics research program
- **BirdNET Team** - Cornell Lab of Ornithology & Chemnitz University of Technology
