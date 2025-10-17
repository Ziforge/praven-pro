# Praven Pro - Dependencies and System Requirements

This document lists all dependencies and system requirements for Praven Pro.

## System Requirements

### Operating System
- **macOS** 10.14+ (recommended)
- **Linux** (Ubuntu 20.04+, Debian 10+)
- **Windows** 10/11 with WSL2 recommended

### Python Version
- **Python 3.8 - 3.12** (tested and supported)
- Python 3.12 recommended for latest features
- Python 3.8-3.11 also fully supported

### Disk Space
- **Minimum:** 2GB free space
- **Recommended:** 5GB+ free space (for models and results)
- BirdNET models: ~100MB (downloaded on first run)

### Memory (RAM)
- **Minimum:** 4GB RAM
- **Recommended:** 8GB+ RAM for large audio files
- **For files >1 hour:** 16GB+ RAM recommended

### System Dependencies

#### macOS
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install ffmpeg for audio file support
brew install ffmpeg
```

#### Ubuntu/Debian Linux
```bash
# Update package list
sudo apt-get update

# Install Python and audio dependencies
sudo apt-get install python3 python3-pip python3-venv ffmpeg libsndfile1 portaudio19-dev

# For visualization support
sudo apt-get install python3-tk
```

#### Windows
```bash
# Install ffmpeg
# Download from: https://ffmpeg.org/download.html
# Or use Chocolatey:
choco install ffmpeg

# Or use scoop:
scoop install ffmpeg
```

## Python Dependencies

### Core Audio Processing
- `librosa>=0.10.0` - Audio analysis and feature extraction
- `soundfile>=0.12.0` - Audio file I/O
- `audioread>=3.0.0` - Audio file format support
- `pydub>=0.25.0` - Audio manipulation
- `ffmpeg-python>=0.2.0` - FFmpeg Python bindings

### BirdNET and Machine Learning
- `birdnetlib==0.18.0` - BirdNET species identification
- `tensorflow>=2.16.0` - Deep learning framework (updated for Python 3.12+)

**Note:** TensorFlow 2.16+ is required for Python 3.12 compatibility. Earlier Python versions (3.8-3.11) can use TensorFlow 2.15.

### Data Processing and Analysis
- `numpy>=1.24.0` - Numerical computing
- `pandas>=2.0.0` - Data analysis and manipulation
- `scipy>=1.10.0` - Scientific computing

### Visualization
- `matplotlib>=3.7.0` - Plotting and visualization
- `seaborn>=0.12.0` - Statistical data visualization

### Jupyter Notebook Support
- `jupyter>=1.0.0` - Jupyter metapackage
- `notebook>=7.0.0` - Jupyter Notebook interface
- `ipykernel>=6.25.0` - IPython kernel for Jupyter
- `ipywidgets>=8.0.0` - Interactive widgets

### Utilities
- `tqdm>=4.65.0` - Progress bars for loops

## Installation

### Quick Install

```bash
# Clone repository
git clone https://github.com/Ziforge/praven-pro.git
cd praven-pro

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install all dependencies
pip install -r requirements.txt
```

### Step-by-Step Install

```bash
# 1. Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# 2. Upgrade pip
pip install --upgrade pip

# 3. Install core dependencies
pip install librosa soundfile audioread birdnetlib tensorflow

# 4. Install data processing
pip install numpy pandas scipy

# 5. Install visualization
pip install matplotlib seaborn

# 6. Install Jupyter
pip install jupyter notebook ipykernel ipywidgets

# 7. Install utilities
pip install pydub ffmpeg-python tqdm
```

## Dependency Resolution Issues

### Common Issues and Solutions

#### Issue 1: TensorFlow Version (Python 3.12)
**Error:** `Could not find a version that satisfies the requirement tensorflow==2.15.0`

**Solution:** Update to TensorFlow 2.16+:
```bash
pip install tensorflow>=2.16.0
```

#### Issue 2: watchdog Build Error
**Error:** `Building wheel for watchdog failed`

**Solution:** Install pre-built wheel:
```bash
pip install watchdog --only-binary :all:
```

#### Issue 3: NumPy Compatibility
**Error:** `module 'numpy' has no attribute 'X'`

**Solution:** Ensure compatible NumPy version:
```bash
pip install "numpy>=1.24.0,<3.0.0"
```

#### Issue 4: FFmpeg Not Found
**Error:** `FileNotFoundError: [Errno 2] No such file or directory: 'ffmpeg'`

**Solution:** Install system ffmpeg (see System Dependencies above)

## Optional Dependencies

### For Advanced Users

#### MCP Integration (Docker-based API)
- Docker Desktop or Docker Engine
- Docker Compose
- 8GB RAM minimum for containers
- 10GB disk space for images

#### R/Rraven Integration
See `mcp-integration/README.md` for R package requirements.

## Verification

### Test Installation

```bash
# Activate virtual environment
source venv/bin/activate

# Test imports
python -c "import librosa, soundfile, birdnetlib, tensorflow, numpy, pandas, scipy, matplotlib, seaborn; print('✅ All packages imported successfully!')"
```

### Check Versions

```bash
# List installed packages
pip list

# Check specific package versions
pip show birdnetlib tensorflow librosa
```

### System Check Script

```bash
# Run system check
python -c "
import sys
print(f'Python: {sys.version}')

import tensorflow as tf
print(f'TensorFlow: {tf.__version__}')

import librosa
print(f'librosa: {librosa.__version__}')

import birdnetlib
print(f'birdnetlib: {birdnetlib.__version__}')

print('✅ All core packages loaded successfully!')
"
```

## Development Dependencies (Optional)

For contributors:

```bash
# Testing
pip install pytest pytest-cov

# Code formatting
pip install black isort flake8

# Type checking
pip install mypy
```

## Troubleshooting

### Memory Issues
If you encounter out-of-memory errors:
1. Reduce `MAX_DETECTIONS_PER_FILE` in Cell 1
2. Process fewer files at once
3. Close other applications
4. Use a machine with more RAM

### Slow Performance
If analysis is slow:
1. Ensure you're using location context (LAT/LON) to filter species
2. Increase `MIN_CONF` threshold to reduce false positives
3. Use SSD storage for audio files
4. Consider using MCP integration for batch processing

### GPU Support (Optional)
For faster TensorFlow operations:
```bash
# Install TensorFlow with GPU support
pip install tensorflow[and-cuda]  # For NVIDIA GPUs
```

**Note:** GPU support requires CUDA-capable GPU and NVIDIA drivers.

## License Notes

All dependencies are open-source and compatible with MIT license:
- TensorFlow: Apache 2.0
- librosa: ISC License
- BirdNET: Custom (academic/research friendly)
- Others: MIT, BSD, or Apache licenses

## Support

For dependency issues:
- Check [GitHub Issues](https://github.com/Ziforge/praven-pro/issues)
- Consult package documentation
- Create new issue with `dependencies` label

## Updates

Dependencies are actively maintained. Check `requirements.txt` for latest versions.

Last updated: 2025-10-17
