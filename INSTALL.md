# Praven Pro Installation Guide

## Quick Install

```bash
pip install praven-pro
```

## With Optional Features

```bash
# Web interface
pip install praven-pro[web]

# Visualization
pip install praven-pro[viz]

# All features
pip install praven-pro[all]
```

## From Source

```bash
git clone https://github.com/Ziforge/praven-pro.git
cd praven-pro
pip install -e .
```

## Quick Start

### Command Line

```bash
praven your_detections.csv \
  --lat 63.341 --lon 10.215 \
  --habitat wetland \
  --date 2025-10-13
```

### Web Interface

```bash
praven-web
# Open http://localhost:5000 in your browser
```

### Python API

```python
from praven import BiologicalValidator, ValidationConfig

config = ValidationConfig(
    location=(63.341, 10.215),
    date="2025-10-13",
    habitat_type="wetland"
)

validator = BiologicalValidator(config)

result = validator.validate_detection(
    species="Lesser Spotted Woodpecker",
    timestamp="2025-10-13 23:45:00",
    confidence=0.85
)

print(result.status)  # "REJECT"
print(result.reason)  # "Nocturnal impossibility..."
```

## Requirements

- Python 3.8+
- pandas >= 1.5.0
- numpy >= 1.20.0
- requests >= 2.25.0
- scikit-learn >= 1.0.0
- pydantic >= 2.0.0

## Optional Requirements

- Flask >= 2.0.0 (for web interface)
- plotly >= 5.0.0 (for advanced visualizations)
- matplotlib >= 3.5.0 (for charts)

## eBird API Key (Optional)

For enhanced geographic validation:

1. Register at https://ebird.org/api/keygen
2. Set environment variable: `export EBIRD_API_KEY="your-key"`

Without an API key, Praven will use cached data and offline validation rules.

## Troubleshooting

### ImportError: No module named 'praven'

Make sure you installed the package:
```bash
pip install praven-pro
```

### FileNotFoundError: species_db.json

The data files should be automatically included. If missing, reinstall:
```bash
pip uninstall praven-pro
pip install --no-cache-dir praven-pro
```

### eBird API Rate Limiting

Praven automatically caches eBird data and refreshes it weekly. For large datasets, disable eBird preloading:

```python
validator = BiologicalValidator(config, enable_ebird_preload=False)
```

## Getting Help

- Documentation: https://github.com/Ziforge/praven-pro
- Issues: https://github.com/Ziforge/praven-pro/issues
- Examples: See `examples/` directory

## Updating

```bash
pip install --upgrade praven-pro
```

## Uninstalling

```bash
pip uninstall praven-pro
```
