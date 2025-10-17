# Troubleshooting Guide

This guide covers common issues and their solutions when setting up and using Praven Pro.

## Installation Issues

### Issue 1: TensorFlow Version Error (Python 3.12)

**Error Message:**
```
ERROR: Could not find a version that satisfies the requirement tensorflow==2.15.0
```

**Cause:** Python 3.12 requires TensorFlow 2.16 or later.

**Solution:**
```bash
pip install tensorflow>=2.16.0
```

Or update `requirements.txt` to use `tensorflow>=2.16.0` instead of `tensorflow==2.15.0`.

**Status:** ✅ Fixed in requirements.txt (as of 2025-10-17)

---

### Issue 2: watchdog Build Error

**Error Message:**
```
Building wheel for watchdog (pyproject.toml) did not run successfully
error: arm-none-eabi-gcc: command failed
```

**Cause:** System has ARM embedded GCC (for microcontrollers) in PATH that conflicts with Python package compilation.

**Solution 1 - Install pre-built wheel:**
```bash
pip install watchdog --only-binary :all:
```

**Solution 2 - Set correct compiler:**
```bash
export CC=clang
export CXX=clang++
pip install watchdog
```

**Solution 3 - Install without watchdog dependency (if not needed for Jupyter):**
```bash
pip install --no-deps librosa soundfile audioread birdnetlib tensorflow
pip install numpy pandas scipy matplotlib seaborn tqdm
```

---

### Issue 3: FFmpeg Not Found

**Error Message:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'ffmpeg'
```

**Cause:** FFmpeg system dependency not installed.

**Solution by OS:**

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

**Windows:**
```bash
# Using Chocolatey
choco install ffmpeg

# Or download from https://ffmpeg.org/download.html
```

---

### Issue 4: NumPy/Pandas Import Errors

**Error Message:**
```
ImportError: cannot import name 'X' from 'numpy'
```

**Cause:** Version incompatibility between packages.

**Solution:**
```bash
# Reinstall with compatible versions
pip install --upgrade numpy pandas scipy
```

---

## BirdNET Analysis Issues

### Issue 5: No Detections Found

**Symptoms:** Analysis runs but reports 0 detections.

**Possible Causes:**

1. **Confidence threshold too high**
   - Solution: Lower `MIN_CONF` from 0.25 to 0.15 in Cell 1

2. **Wrong location coordinates**
   - Solution: Verify LAT/LON are correct for your recording location

3. **Wrong recording date**
   - Solution: Ensure DATE matches when recordings were made (affects species list)

4. **Audio file issues**
   - Solution: Check audio file plays correctly in media player
   - Verify sample rate is reasonable (44.1kHz or 48kHz)

---

### Issue 6: Very Large Files Cause Memory Errors

**Error Message:**
```
MemoryError: Unable to allocate array
```

**Cause:** Insufficient RAM for large audio files.

**Solutions:**

1. **Limit visualizations:**
   ```python
   MAX_DETECTIONS_PER_FILE = 50  # Only visualize first 50
   ```

2. **Process files separately:**
   - Move files to `audio_files/` one at a time
   - Run notebook multiple times

3. **Skip visualization cell:**
   - Run Cells 1-2 for analysis only
   - Skip Cell 3 to save memory

4. **Increase system RAM or use machine with more memory**

---

## Filename Parsing Issues

### Issue 7: Timestamps Not Extracted

**Symptoms:** Script can't parse timestamps from audio filenames.

**Common Filename Patterns:**

```python
# Pattern 1: DeviceID_YYYYMMDD_HHMMSS.WAV
"245AAA0563ED3DA7_20251013_113753.WAV"

# Pattern 2: Simple date-time
"recording_20251013_113753.wav"

# Pattern 3: Audiomoth format
"20251013_113753.WAV"
```

**Solution:** Update regex pattern in your script to match your filename format.

**Example fix for hex device IDs:**
```python
# Original (only matches digits)
pattern = r'(\d+)_(\d{8})_(\d{6})\.WAV'

# Fixed (matches hex device IDs)
pattern = r'([A-F0-9]+)_(\d{8})_(\d{6})\.WAV'
```

---

## Jupyter Notebook Issues

### Issue 8: Jupyter Won't Start

**Error Message:**
```
jupyter: command not found
```

**Solution:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall Jupyter
pip install jupyter notebook
```

---

### Issue 9: Kernel Dies During Analysis

**Symptoms:** Jupyter kernel crashes while processing large files.

**Solutions:**

1. **Restart kernel and clear outputs**
   - Kernel → Restart & Clear Output

2. **Process fewer files at once**

3. **Check system resources:**
   ```bash
   # macOS/Linux
   top

   # Check available memory
   free -h  # Linux
   vm_stat  # macOS
   ```

---

### Issue 10: Notebook Shows "Untrusted"

**Symptoms:** Red "Not Trusted" badge in Jupyter.

**Solution:**
```bash
jupyter trust notebooks/bird_audio_batch_analysis.ipynb
```

---

## Performance Issues

### Issue 11: Analysis Very Slow

**Symptoms:** Taking much longer than expected.

**Solutions:**

1. **Use location context (faster species filtering):**
   ```python
   LAT = 63.4305  # Your latitude
   LON = 10.3951  # Your longitude
   DATE = "2025-05-15"  # Recording date
   ```

2. **Increase confidence threshold (fewer detections to process):**
   ```python
   MIN_CONF = 0.35  # Higher = faster but may miss some birds
   ```

3. **Use SSD storage** for audio files (not external HDD)

4. **Close other applications** to free RAM

---

## Output File Issues

### Issue 12: Can't Open Raven Tables

**Symptoms:** Raven Pro can't open exported selection tables.

**Solution:** Ensure files are tab-delimited and have correct headers:
```
Selection	View	Channel	Begin Time (s)	End Time (s)	Low Freq (Hz)	High Freq (Hz)
```

---

### Issue 13: Audacity Won't Import Labels

**Symptoms:** Labels don't appear in Audacity.

**Solution:**
1. Open audio file in Audacity first
2. File → Import → Labels...
3. Select corresponding `*_labels.txt` file
4. Ensure label file format: `start\tend\tlabel`

---

## Docker/MCP Issues

### Issue 14: Docker Services Won't Start

**Error Message:**
```
Cannot connect to the Docker daemon
```

**Solution:**
```bash
# Start Docker Desktop (macOS/Windows)
# Or start Docker daemon (Linux)
sudo systemctl start docker
```

---

### Issue 15: Port Already in Use

**Error Message:**
```
Bind for 0.0.0.0:8080 failed: port is already allocated
```

**Solution:** Edit `mcp-integration/docker-compose.yml`:
```yaml
ports:
  - "8081:8080"  # Use different port
```

---

## Getting Help

### Check Logs

**For Jupyter issues:**
```bash
jupyter notebook list
jupyter --version
```

**For Python package issues:**
```bash
pip list
pip show birdnetlib tensorflow librosa
```

**For Docker/MCP issues:**
```bash
docker compose logs
docker ps -a
```

### Create Issue on GitHub

If you encounter an issue not covered here:

1. Go to: https://github.com/Ziforge/praven-pro/issues
2. Click "New Issue"
3. Include:
   - Error message (full text)
   - Python version (`python --version`)
   - Operating system
   - Steps to reproduce

### Useful Commands

**Test imports:**
```python
python -c "import librosa, soundfile, birdnetlib, tensorflow; print('OK')"
```

**Check audio file:**
```python
import soundfile as sf
info = sf.info('your_audio.wav')
print(f"Duration: {info.duration}s, Sample rate: {info.samplerate}Hz")
```

**Verify BirdNET models:**
```python
from birdnetlib.analyzer import Analyzer
analyzer = Analyzer()  # Should download models if missing
```

---

## Additional Resources

- **DEPENDENCIES.md** - Complete list of dependencies and versions
- **README.md** - Main documentation
- **mcp-integration/README.md** - Advanced MCP workflow
- **BirdNET Documentation:** https://github.com/kahst/BirdNET-Analyzer
- **Raven Pro Manual:** https://ravensoundsoftware.com/

---

Last updated: 2025-10-17
