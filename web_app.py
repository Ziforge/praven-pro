#!/usr/bin/env python3
"""
Praven Pro Web Interface

Simple Flask web app for uploading BirdNET CSVs and getting validation results.
No installation required - just run and access at http://localhost:5000
"""

from flask import Flask, render_template_string, request, send_file, jsonify
import pandas as pd
from pathlib import Path
import tempfile
import os
from datetime import datetime

from praven.validator import BiologicalValidator
from praven.config import ValidationConfig
from praven.pipeline import ValidationPipeline
from praven.visualization import generate_dashboard

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# HTML template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Praven Pro - BirdNET Validation</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            max-width: 800px;
            margin: 50px auto;
            background: white;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }
        h1 {
            color: #2c3e50;
            margin: 0 0 10px 0;
            font-size: 36px;
        }
        .subtitle {
            color: #7f8c8d;
            margin: 0 0 30px 0;
            font-size: 16px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
            color: #34495e;
        }
        input[type="text"], input[type="number"], select, input[type="file"] {
            width: 100%;
            padding: 12px;
            border: 2px solid #ecf0f1;
            border-radius: 5px;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        input:focus, select:focus {
            outline: none;
            border-color: #3498db;
        }
        .row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }
        .button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 30px;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            width: 100%;
            margin-top: 20px;
            transition: transform 0.2s;
        }
        .button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        .button:disabled {
            background: #bdc3c7;
            cursor: not-allowed;
            transform: none;
        }
        .status {
            margin-top: 20px;
            padding: 15px;
            border-radius: 5px;
            display: none;
        }
        .status.success {
            background: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
        }
        .status.error {
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24;
        }
        .status.processing {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            color: #856404;
        }
        .results {
            margin-top: 30px;
            display: none;
        }
        .result-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 15px;
        }
        .result-card h3 {
            margin-top: 0;
            color: #2c3e50;
        }
        .download-btn {
            display: inline-block;
            background: #27ae60;
            color: white;
            padding: 10px 20px;
            border-radius: 5px;
            text-decoration: none;
            margin-right: 10px;
            margin-top: 10px;
        }
        .download-btn:hover {
            background: #229954;
        }
        .help-text {
            font-size: 12px;
            color: #7f8c8d;
            margin-top: 5px;
        }
        .badge {
            display: inline-block;
            padding: 5px 10px;
            border-radius: 3px;
            font-size: 14px;
            font-weight: bold;
            margin: 5px;
        }
        .badge.green { background: #27ae60; color: white; }
        .badge.red { background: #e74c3c; color: white; }
        .badge.orange { background: #f39c12; color: white; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🐦 Praven Pro</h1>
        <p class="subtitle">Automated BirdNET Biological Validation</p>

        <form id="validation-form" enctype="multipart/form-data">
            <div class="form-group">
                <label>BirdNET CSV File *</label>
                <input type="file" name="file" id="file" accept=".csv" required>
                <p class="help-text">Upload your BirdNET detection results (CSV format)</p>
            </div>

            <div class="row">
                <div class="form-group">
                    <label>Latitude *</label>
                    <input type="number" name="lat" step="any" placeholder="63.341" required>
                </div>
                <div class="form-group">
                    <label>Longitude *</label>
                    <input type="number" name="lon" step="any" placeholder="10.215" required>
                </div>
            </div>

            <div class="form-group">
                <label>
                    <input type="checkbox" id="auto-habitat-check" name="auto_habitat" checked>
                    Auto-detect habitat from GPS?
                </label>
                <select name="habitat" id="habitat-select" disabled style="margin-top: 10px;">
                    <option value="">Auto-detect from GPS</option>
                    <option value="wetland">Wetland</option>
                    <option value="forest">Forest</option>
                    <option value="grassland">Grassland</option>
                    <option value="oceanic">Oceanic</option>
                    <option value="urban">Urban</option>
                    <option value="agricultural">Agricultural</option>
                </select>
                <p class="help-text">Check to auto-detect, or uncheck to specify manually</p>
            </div>

            <p class="help-text" style="margin-top: 20px;">
                📅 Date &amp; time will be extracted from your CSV file<br>
                🌤️ Weather will be automatically fetched based on GPS coordinates and detection timestamps
            </p>

            <button type="submit" class="button" id="submit-btn">Validate BirdNET Data</button>
        </form>

        <div id="status" class="status"></div>

        <div id="results" class="results"></div>
    </div>

    <script>
        // Handle habitat auto-detection checkbox
        const autoHabitatCheck = document.getElementById('auto-habitat-check');
        const habitatSelect = document.getElementById('habitat-select');

        autoHabitatCheck.addEventListener('change', function() {
            if (this.checked) {
                habitatSelect.disabled = true;
                habitatSelect.value = '';
            } else {
                habitatSelect.disabled = false;
            }
        });

        document.getElementById('validation-form').addEventListener('submit', async (e) => {
            e.preventDefault();

            const statusDiv = document.getElementById('status');
            const resultsDiv = document.getElementById('results');
            const submitBtn = document.getElementById('submit-btn');

            // Show processing status
            statusDiv.className = 'status processing';
            statusDiv.style.display = 'block';
            statusDiv.innerHTML = '⏳ Processing... This may take a few minutes for large files.';
            submitBtn.disabled = true;
            resultsDiv.style.display = 'none';

            // Prepare form data
            const formData = new FormData(e.target);

            try {
                const response = await fetch('/validate', {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();

                if (data.success) {
                    // Show success
                    statusDiv.className = 'status success';
                    statusDiv.innerHTML = '✅ Validation complete!';

                    // Show results
                    resultsDiv.style.display = 'block';
                    resultsDiv.innerHTML = `
                        <div class="result-card">
                            <h3>Validation Results</h3>
                            <div>
                                <span class="badge green">Accepted: ${data.stats.accepted}</span>
                                <span class="badge red">Rejected: ${data.stats.rejected}</span>
                                <span class="badge orange">Review: ${data.stats.review}</span>
                            </div>
                            <p><strong>Total Detections:</strong> ${data.stats.total}</p>
                            <p><strong>Species Count:</strong> ${data.stats.species_count}</p>
                        </div>

                        <div class="result-card">
                            <h3>Download Results</h3>
                            <a href="/download/${data.session_id}/accepted.csv" class="download-btn">📥 Accepted</a>
                            <a href="/download/${data.session_id}/rejected.csv" class="download-btn">📥 Rejected</a>
                            <a href="/download/${data.session_id}/review.csv" class="download-btn">📥 Review</a>
                            <a href="/download/${data.session_id}/dashboard.html" class="download-btn">📊 Dashboard</a>
                        </div>
                    `;
                } else {
                    statusDiv.className = 'status error';
                    statusDiv.innerHTML = '❌ Error: ' + (data.error || 'Unknown error');
                }
            } catch (error) {
                statusDiv.className = 'status error';
                statusDiv.innerHTML = '❌ Error: ' + error.message;
            } finally {
                submitBtn.disabled = false;
            }
        });
    </script>
</body>
</html>
"""

# Store temp results
temp_results = {}


@app.route('/')
def index():
    """Home page with upload form."""
    return render_template_string(HTML_TEMPLATE)


@app.route('/validate', methods=['POST'])
def validate():
    """Process uploaded CSV and validate."""
    try:
        # Get file
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'})

        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'})

        # Get parameters
        lat = float(request.form.get('lat'))
        lon = float(request.form.get('lon'))

        # Check auto-habitat checkbox
        auto_habitat = request.form.get('auto_habitat') == 'on'

        # Get habitat (only if not auto-detecting)
        habitat = None
        if not auto_habitat:
            habitat = request.form.get('habitat')

        # Save uploaded file
        temp_dir = Path(tempfile.mkdtemp())
        input_path = temp_dir / file.filename
        file.save(input_path)

        # Extract date from CSV
        import pandas as pd
        df = pd.read_csv(input_path, nrows=1)  # Read just first row

        # Try to find date in common columns
        date = None
        if 'recording_date' in df.columns:
            date = str(df['recording_date'].iloc[0])
        elif 'absolute_timestamp' in df.columns:
            timestamp = str(df['absolute_timestamp'].iloc[0])
            date = timestamp.split()[0]  # Extract date part
        elif 'filename' in df.columns:
            # Extract from filename (e.g., "245AAA0563ED3DA7_20251013_113753.WAV")
            filename = str(df['filename'].iloc[0])
            import re
            match = re.search(r'(\d{8})', filename)  # Find 8-digit date (YYYYMMDD)
            if match:
                date_str = match.group(1)
                date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"

        if not date:
            date = "2025-01-01"  # Fallback default

        # Create config (always auto-fetch weather from GPS + date)
        config = ValidationConfig(
            location=(lat, lon),
            date=date,
            habitat_type=habitat,
            weather_conditions=None,  # Always auto-fetch
            auto_detect_habitat=auto_habitat,
            auto_detect_weather=True  # Always enabled
        )

        # Run validation
        pipeline = ValidationPipeline(config)
        pipeline.validator.ebird_preloader = None  # Disable eBird for web (faster)

        output_files = pipeline.process_birdnet_csv(
            input_path=str(input_path),
            output_dir=str(temp_dir),
            export_formats=['csv']
        )

        # Generate dashboard
        results_df = pd.read_csv(output_files['full_csv'])
        dashboard_path = temp_dir / "dashboard.html"
        generate_dashboard(
            results_df,
            str(dashboard_path),
            config={'location': (lat, lon), 'date': date, 'habitat_type': habitat}
        )

        # Calculate stats
        stats = {
            'total': len(results_df),
            'accepted': (results_df['status'] == 'ACCEPT').sum(),
            'rejected': (results_df['status'] == 'REJECT').sum(),
            'review': (results_df['status'] == 'REVIEW').sum(),
            'species_count': results_df['common_name'].nunique()
        }

        # Store session
        session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        temp_results[session_id] = temp_dir

        return jsonify({
            'success': True,
            'session_id': session_id,
            'stats': stats
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/download/<session_id>/<filename>')
def download(session_id, filename):
    """Download result file."""
    if session_id not in temp_results:
        return "Session not found", 404

    temp_dir = temp_results[session_id]

    # Map friendly names to actual files
    file_mapping = {
        'accepted.csv': list(temp_dir.glob('*_accepted.csv')),
        'rejected.csv': list(temp_dir.glob('*_rejected.csv')),
        'review.csv': list(temp_dir.glob('*_review.csv')),
        'dashboard.html': [temp_dir / 'dashboard.html']
    }

    if filename not in file_mapping:
        return "File not found", 404

    files = file_mapping[filename]
    if not files or not files[0].exists():
        return "File not found", 404

    return send_file(files[0], as_attachment=True)


if __name__ == '__main__':
    print("=" * 80)
    print("Praven Pro Web Interface")
    print("=" * 80)
    print("\nStarting server...")
    print("Open in browser: http://localhost:5001")
    print("\nPress Ctrl+C to stop\n")

    app.run(debug=True, host='0.0.0.0', port=5001)
