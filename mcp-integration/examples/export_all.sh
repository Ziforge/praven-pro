#!/bin/bash
# Batch export all detection CSVs to Raven Pro selection tables

API_URL="http://localhost:8080"

echo "📦 Batch exporting detections to Raven Pro format..."

curl -X POST "$API_URL/raven/export_batch" \
  -H "Content-Type: application/json" \
  -d '{
    "detections_dir": "/workspace/shared/results/csvs",
    "output_dir": "/workspace/shared/results/raven_tables",
    "audio_dir": "/workspace/shared/audio",
    "file_pattern": "*_detections.csv",
    "default_low_freq": 500.0,
    "default_high_freq": 8000.0
  }' | python3 -m json.tool

echo ""
echo "✅ Batch export complete!"
echo "📁 Check results/raven_tables/ for output files"
