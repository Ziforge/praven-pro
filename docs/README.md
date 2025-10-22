# Praven Pro Documentation

Complete documentation for Praven Pro 2.1 - BirdNET validation system.

---

## Quick Links

- [Main README](../README.md) - Project overview and quick start
- [Installation Guide](../INSTALL.md) - Setup instructions
- [Quick Start Guide](../QUICKSTART.md) - Usage examples

---

## Scientific Documentation

### Validation & Results
- [Scientific Validation Results](scientific/SCIENTIFIC_VALIDATION_RESULTS.md) - Blind test results (1,000 samples)
- [Gaulossen Case Study](results/GAULOSSEN_RESULTS.md) - Real-world validation (6,805 detections)
- [Technical Summary](TECHNICAL_SUMMARY.md) - System specifications and methodology

### Implementation Details
- [Praven 2.0 Architecture](PRAVEN_2.0_SUMMARY.md) - Core system design
- [Extensions Summary](EXTENSIONS_SUMMARY.md) - Feature implementations

---

## User Guides

### Workflows
- [Smart Review Guide](guides/SMART_REVIEW_GUIDE.md) - Reduce review workload by 97%
- [Process Flow Diagrams](PROCESS_FLOW.md) - ASCII flow diagrams
- [Visual Diagrams](DIAGRAMS.md) - Mermaid diagrams for GitHub

### Screenshots & Examples
- [Web Interface Screenshots](SCREENSHOTS.md) - GUI examples
- [Example Data](../data/examples/) - Sample validation outputs

---

## Reference

### System Architecture

**Core Components:**
1. BiologicalValidator - Rule-based validation engine
2. SmartReviewSelector - Workload reduction (top 3 per species)
3. eBird Preloader - Automatic data caching
4. Taxonomic Rules Engine - 40 families, 4,000+ species

**Interfaces:**
- Command Line: `validate.py`
- Web Interface: `web_app.py` (port 5001)
- Python API: `from praven import BiologicalValidator`

**Data Flow:**
```
BirdNET CSV → Validation → Classification → Smart Review → Output
```

---

## Documentation Index

### By Topic

**Getting Started:**
1. [Installation](../INSTALL.md)
2. [Quick Start](../QUICKSTART.md)
3. [Web Interface Screenshots](SCREENSHOTS.md)

**Understanding the System:**
1. [Technical Summary](TECHNICAL_SUMMARY.md)
2. [System Architecture](PRAVEN_2.0_SUMMARY.md)
3. [Visual Diagrams](DIAGRAMS.md)

**Using Praven Pro:**
1. [Smart Review Workflow](guides/SMART_REVIEW_GUIDE.md)
2. [Process Flows](PROCESS_FLOW.md)
3. [Example Data](../data/examples/)

**Scientific Validation:**
1. [Validation Methodology](scientific/SCIENTIFIC_VALIDATION_RESULTS.md)
2. [Case Study Results](results/GAULOSSEN_RESULTS.md)
3. [Extensions & Features](EXTENSIONS_SUMMARY.md)

---

## File Organization

```
praven-pro/
├── README.md                  # Project overview
├── INSTALL.md                 # Installation guide
├── QUICKSTART.md              # Usage examples
├── LICENSE                    # Non-commercial license
│
├── docs/
│   ├── README.md              # This file
│   ├── DIAGRAMS.md            # Mermaid diagrams
│   ├── PROCESS_FLOW.md        # ASCII flow diagrams
│   ├── SCREENSHOTS.md         # Web interface screenshots
│   ├── TECHNICAL_SUMMARY.md   # Technical specifications
│   ├── PRAVEN_2.0_SUMMARY.md  # Architecture documentation
│   ├── EXTENSIONS_SUMMARY.md  # Feature implementations
│   │
│   ├── guides/
│   │   └── SMART_REVIEW_GUIDE.md
│   │
│   ├── scientific/
│   │   └── SCIENTIFIC_VALIDATION_RESULTS.md
│   │
│   └── results/
│       └── GAULOSSEN_RESULTS.md
│
├── data/
│   ├── examples/              # Sample CSV outputs
│   └── validation_output/     # Generated reports
│
├── praven/
│   ├── validator.py           # Core validation
│   ├── review_selector.py     # Smart review
│   ├── pipeline.py            # Automation
│   ├── visualization.py       # Dashboard generation
│   └── data/
│       ├── species_db.json    # 62 curated species
│       └── taxonomic_rules.json # 40 families
│
├── validate.py                # CLI interface
└── web_app.py                 # Web interface (port 5001)
```

---

## Usage Patterns

### Command Line
```bash
# Basic validation
python validate.py input.csv --lat 63.341 --lon 10.215 --habitat wetland

# With weather conditions
python validate.py input.csv --lat 63.341 --lon 10.215 --habitat wetland \
  --rain 0.3 --fog 0.5 --date 2025-10-15
```

### Python API
```python
from praven import BiologicalValidator, ValidationConfig

config = ValidationConfig(
    location=(63.341, 10.215),
    habitat_type="wetland",
    date="2025-10-15"
)

validator = BiologicalValidator(config)
result = validator.validate_detection("Graylag Goose", "2025-10-15 14:30", 0.95)
```

### Web Interface
```bash
python web_app.py
# Open browser: http://localhost:5001
```

---

## Key Metrics

**Gaulossen Dataset Results:**
- Original detections: 6,201
- Smart review selection: 192 detections (top 3 per species)
- Species-level pass rate: 82.2% (74/90 species)

**Taxonomic Coverage:**
- Families: 40 bird families
- Primarily European species

---

## Contact & Support

- Repository: https://github.com/Ziforge/praven-pro
- Issues: https://github.com/Ziforge/praven-pro/issues
- Email: ghredpath@hotmail.com

**License:** Non-commercial use only. Commercial licensing available.
