# Screenshot Capture Instructions

The web interface is now running at **http://localhost:5001**

Follow these instructions to capture the required screenshots.

---

## Prerequisites

- Web interface running (already started)
- Browser open to http://localhost:5001
- Screenshot tool ready (macOS: Cmd+Shift+4, or use Grab/Screenshot app)

---

## Required Screenshots

### 1. Landing Page (web_interface_landing.png)

**What to capture:**
- Full browser window showing the Praven Pro web interface
- Purple gradient header
- "🐦 Praven Pro" title
- Full form with all fields visible:
  - BirdNET CSV File upload
  - Latitude/Longitude fields
  - Habitat Type dropdown (showing "Auto-detect from GPS")
  - Date field
  - Rain and Fog fields (with "Auto-fetch from GPS" placeholders)
  - Validate button

**Steps:**
1. Make sure no fields are filled
2. Capture full browser window
3. Save as: `docs/images/web_interface_landing.png`

---

### 2. Form with Auto-Detection Highlighted (web_interface_auto_detect.png)

**What to capture:**
- Same as landing page but highlighting the auto-detection features

**Steps:**
1. Click on Habitat dropdown to show "Auto-detect from GPS" option selected
2. Capture showing the dropdown and help text
3. Save as: `docs/images/web_interface_auto_detect.png`

---

### 3. Weather Auto-Fetch Fields (web_interface_weather_auto.png)

**What to capture:**
- Zoom in on the Rain and Fog fields
- Show the placeholders "Auto-fetch from GPS"
- Show the help text "Leave blank to auto-fetch from GPS + date"

**Steps:**
1. Scroll to weather fields section
2. Capture the Rain and Fog fields with help text visible
3. Save as: `docs/images/web_interface_weather_auto.png`

---

### 4. File Upload (web_interface_upload.png)

**What to capture:**
- File upload field with a file selected

**Steps:**
1. Click "Choose File" and select a CSV file (e.g., `validation/gaulossen_all_detections.csv`)
2. Show the filename appearing in the upload field
3. Save as: `docs/images/web_interface_upload.png`

---

### 5. Filled Form Ready to Submit (web_interface_filled.png)

**What to capture:**
- Form filled with sample data ready to validate

**Steps:**
1. Fill in the form:
   - File: gaulossen_all_detections.csv
   - Latitude: 63.341
   - Longitude: 10.215
   - Habitat: (leave as "Auto-detect from GPS")
   - Date: 2025-10-15
   - Rain: (leave blank for auto-fetch)
   - Fog: (leave blank for auto-fetch)
2. Capture full form before clicking Validate
3. Save as: `docs/images/web_interface_filled.png`

---

### 6. Validation Results Page (web_interface_results.png)

**What to capture:**
- Results page showing validation statistics

**Steps:**
1. Click "Validate BirdNET Data" button
2. Wait for validation to complete
3. Capture the results showing:
   - Success message
   - Statistics (total, accepted, rejected, review)
   - Download links
4. Save as: `docs/images/web_interface_results.png`

**Note:** This will actually run validation, so make sure the Gaulossen CSV is available.

---

### 7. Console Output Showing Auto-Detection (terminal_auto_detection.png)

**What to capture:**
- Terminal window showing the auto-detection messages

**Steps:**
1. Open the terminal where `python web_app.py` is running
2. Show the Flask output including any auto-detection messages
3. Capture showing:
   - "🌍 Auto-detecting habitat from GPS coordinates..."
   - "   Detected: oceanic (50%), grassland (33%), urban (17%)"
   - "🌤️  Auto-fetching weather data..."
   - "   Fetched: X°C, rain X, fog X"
4. Save as: `docs/images/terminal_auto_detection.png`

---

### 8. CLI Auto-Detection Example (cli_auto_detection.png)

**What to capture:**
- Terminal showing CLI usage with auto-detection

**Steps:**
1. Open new terminal window
2. Run: `python validate.py validation/gaulossen_all_detections.csv --lat 63.341 --lon 10.215 --date 2025-10-15`
3. Capture the output showing auto-detection messages
4. Save as: `docs/images/cli_auto_detection.png`

---

### 9. CLI Help Menu (cli_help.png)

**What to capture:**
- Full CLI help output

**Steps:**
1. Run: `python validate.py --help`
2. Capture full output showing examples with auto-detection
3. Save as: `docs/images/cli_help.png`

---

## File Organization

After capturing, verify all screenshots are saved to:

```
docs/images/
├── web_interface_landing.png
├── web_interface_auto_detect.png
├── web_interface_weather_auto.png
├── web_interface_upload.png
├── web_interface_filled.png
├── web_interface_results.png
├── terminal_auto_detection.png
├── cli_auto_detection.png
└── cli_help.png
```

---

## Image Specifications

- **Format:** PNG (lossless)
- **Resolution:** Native retina (don't scale down)
- **Compression:** Optimize after capture (use ImageOptim or similar)
- **Naming:** Lowercase, underscores, descriptive

---

## After Capturing

Once all screenshots are captured:

1. Update `docs/SCREENSHOTS.md` with actual image links
2. Replace placeholder text with `![Description](images/filename.png)`
3. Verify all images display correctly in the markdown

---

## Quick macOS Screenshot Commands

- **Full window:** Cmd+Shift+4, then Space, then click window
- **Selection:** Cmd+Shift+4, then drag to select area
- **Entire screen:** Cmd+Shift+3

Screenshots save to Desktop by default.

---

## Need Help?

If the web interface isn't working:
1. Check terminal for errors
2. Restart: `python web_app.py`
3. Verify port 5001 is not in use: `lsof -i :5001`
