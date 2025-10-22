# Praven Pro 2.2 - BirdNET Biological Validation

**Automated biological validation for BirdNET acoustic monitoring using taxonomic rules**

[![Version](https://img.shields.io/badge/version-2.2-blue.svg)](https://github.com/Ziforge/praven-pro)
[![Families](https://img.shields.io/badge/families-40-green.svg)](praven/data/taxonomic_rules.json)
[![License](https://img.shields.io/badge/license-Non--Commercial-orange.svg)](LICENSE)

## Overview

Praven Pro automatically validates BirdNET detections using **biological rules**, not machine learning. The system catches false positives that BirdNET misses by checking if detections are biologically plausible:

- ✅ **Temporal validation:** Diurnal woodpeckers at night? Reject!
- ✅ **Habitat validation:** Oceanic birds 100m inland? Reject!
- ✅ **Geographic validation:** Non-native species? Flag for review!
- ✅ **Taxonomic rules:** Family-level biology for 40 bird families!

## Features

### Automated Validation Pipeline

```
BirdNET CSV → Praven Validator → Accept/Review/Reject
                    ↓
        ┌───────────┼───────────┐
        │           │           │
   Geographic   Temporal    Habitat
   Validator    Validator   Validator
        ↓           ↓           ↓
  eBird API    Species DB   Habitat DB
  GBIF API     (diurnal/    (preferences)
               nocturnal)
```

### Validation Checks

1. **Geographic Range Validation**
   - Queries eBird API for species occurrence at coordinates + date
   - Checks GBIF occurrence records within radius
   - Auto-rejects oceanic species inland, non-native species

2. **Temporal Validation**
   - Time-of-day checking (diurnal vs nocturnal species)
   - Seasonal occurrence patterns
   - Migration timing windows

3. **Habitat Matching**
   - Species habitat preferences (wetland, forest, oceanic, etc.)
   - Auto-rejects habitat mismatches (e.g., forest species in wetlands)

4. **Weather Activity ML Model**
   - Trained on verified field data
   - Predicts species activity in rain/fog conditions
   - Confidence scoring adjustment

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

### One-Line Validation

Validate any BirdNET CSV file with a single command:

```bash
python validate.py your_detections.csv \
  --lat 63.341 --lon 10.215 \
  --habitat wetland \
  --date 2025-10-13
```

**Output:** Automatically creates `accepted.csv`, `rejected.csv`, `review.csv`, and `summary.txt`

### Python API

```python
from praven.validator import BiologicalValidator
from praven.config import ValidationConfig

# Initialize validator (auto-preloads eBird data)
config = ValidationConfig(
    location=(63.341, 10.215),  # Gaulosen coordinates
    date="2025-10-13",
    habitat_type="wetland",
    weather_conditions={"rain": 0.8, "fog": 0.7}
)

validator = BiologicalValidator(config)

# Validate BirdNET detection
result = validator.validate_detection(
    species="Lesser Spotted Woodpecker",
    timestamp="2025-10-13 23:45:00",
    confidence=0.85
)

print(result.status)  # "REJECT"
print(result.reason)  # "Nocturnal impossibility: diurnal species at 23:45"
```

### Gaulossen Study Results

Tested on the Gaulossen Nature Reserve dataset (October 2025):
- ✅ **6,805 detections** processed automatically
- ✅ **Smart review:** 6,202 detections → 192 selected for manual verification
- ✅ **Species validation:** 82.2% pass rate (74/90 species)
- ✅ **Known rejections:** Lesser Spotted Woodpecker (nocturnal impossibility), European Storm-Petrel (oceanic habitat mismatch), and others

[Full study →](https://ziforge.github.io/gaulosen-study/)

**⚠️ Current Limitations:** This system is a proof-of-concept validated on a single wetland study. Extensive development is required for broader real-world deployment, including:
- **Limited species coverage:** Only 40 bird families (primarily European species)
- **Incomplete weather data:** Temperature, precipitation, visibility, wind, clouds only - missing humidity, barometric pressure, snow/ice conditions
- **No seasonal migration models:** Lacks comprehensive phenology databases for regional migration timing variations
- **Single habitat type validation:** Tested only on wetland ecosystem, not forests, grasslands, urban areas, etc.
- **Limited geographic scope:** Validated only in Norway (63°N), untested across latitudes, continents, and climate zones
- **No call type validation:** Cannot distinguish song vs. flight calls vs. alarm calls
- **Independent testing needed:** Requires validation on multiple datasets from different researchers and locations
- **Peer review required:** Validation methodology and biological rules need formal scientific peer review

## Module Structure

```
praven-pro/
├── praven/
│   ├── __init__.py
│   ├── validator.py          # Main validation engine
│   ├── api/
│   │   ├── ebird_client.py   # eBird API wrapper
│   │   ├── gbif_client.py    # GBIF API wrapper
│   │   └── cache.py          # API response caching
│   ├── rules/
│   │   ├── geographic.py     # Geographic range validation
│   │   ├── temporal.py       # Time-of-day, seasonality
│   │   ├── habitat.py        # Habitat matching
│   │   └── weather.py        # Weather-activity ML model
│   ├── models/
│   │   ├── weather_model.py  # Random Forest weather model
│   │   └── training.py       # Model training pipeline
│   ├── data/
│   │   ├── species_db.json   # Species metadata (diurnal/nocturnal)
│   │   └── habitat_db.json   # Habitat preferences
│   └── config.py             # Configuration management
├── examples/
│   ├── validate_birdnet_csv.py
│   └── train_weather_model.py
├── tests/
│   └── test_validator.py
├── requirements.txt
└── README.md
```

## API Keys

### eBird API
1. Register at https://ebird.org/api/keygen
2. Set environment variable: `export EBIRD_API_KEY="your-key"`

### GBIF API
- No API key required (open access)

## Example: Validate Gaulossen Study

```python
from praven.validator import BiologicalValidator
import pandas as pd

# Load BirdNET results
birdnet_df = pd.read_csv("BirdNET_results.txt", sep="\t")

validator = BiologicalValidator.from_config({
    "location": (63.341, 10.215),
    "date_range": ("2025-10-13", "2025-10-15"),
    "habitat_type": "wetland",
    "weather": {"rain": 0.8, "fog": 0.7}
})

# Validate all detections
results = validator.validate_dataframe(birdnet_df)

# Filter by status
accepted = results[results.status == "ACCEPT"]
rejected = results[results.status == "REJECT"]
needs_review = results[results.status == "REVIEW"]

print(f"Accepted: {len(accepted)}")
print(f"Rejected: {len(rejected)}")
print(f"Needs Review: {len(needs_review)}")

# Export rejection reasons
rejected[["species", "timestamp", "rejection_reason"]].to_csv("rejected.csv")
```

## Performance Metrics (Gaulossen Dataset)

**Original Manual Validation:**
- Stage 1 (Audio Quality): 90 → 82 species (91.1% pass)
- Stage 2 (Biological): 82 → 74 species (90.2% pass)
- **Overall: 82.2% pass rate**

**Automated Validation (Target):**
- Auto-accept high confidence + all checks pass: ~60%
- Auto-reject clear violations: ~15%
- Flagged for human review: ~25%
- **Goal: 95%+ accuracy on auto-accept/reject decisions**

## Known Rejections (Gaulossen Study)

The system identified these biologically implausible detections:

1. **Lesser Spotted Woodpecker** (14 detections)
   - Reason: Nocturnal impossibility (diurnal species detected at night)

2. **European Storm-Petrel** (4 detections)
   - Reason: Habitat mismatch (oceanic species 100m inland)

3. **Manx Shearwater** (3 detections)
   - Reason: Habitat mismatch (pelagic species inland)

4. **Bar-headed Goose** (1 detection)
   - Reason: Geographic range (non-native to Norway)

5. **Western Capercaillie** (1 detection)
   - Reason: Habitat mismatch (old-growth forest species in wetland)

## Training Custom Weather Models

```python
from praven.models.training import WeatherModelTrainer

# Load your verified dataset
trainer = WeatherModelTrainer()
trainer.load_verified_data("gaulossen_verified.csv")

# Train model on weather-activity patterns
model = trainer.train(
    features=["rain_intensity", "fog_density", "temperature", "hour"],
    target="detection_valid"
)

# Save model
model.save("custom_weather_model.pkl")

# Use in validator
validator = BiologicalValidator(
    config=config,
    custom_weather_model="custom_weather_model.pkl"
)
```

## Citation

```
Redpath, G. (2025). Praven Pro: Automated Biological Validation for
BirdNET Acoustic Monitoring. GitHub. https://github.com/Ziforge/praven-pro
```

## License

**Non-Commercial Use Only**

Praven Pro is free for academic research, educational purposes, and non-profit conservation work.

**Commercial use requires a separate license.** For commercial licensing inquiries, please contact:
- **Email:** ghredpath@hotmail.com
- **Subject:** Praven Pro Commercial License Request

See [LICENSE](LICENSE) for full terms.

---

## Documentation

### Getting Started
- [Installation Guide](INSTALL.md) - Setup and dependencies
- [Quick Start Guide](QUICKSTART.md) - Usage examples
- [Web Interface Screenshots](docs/SCREENSHOTS.md) - GUI examples

### Technical Documentation
- [Technical Summary](docs/TECHNICAL_SUMMARY.md) - System specifications
- [System Architecture](docs/PRAVEN_2.0_SUMMARY.md) - Design documentation
- [Process Flow Diagrams](docs/DIAGRAMS.md) - Visual workflow diagrams

### User Guides
- [Smart Review Guide](docs/guides/SMART_REVIEW_GUIDE.md) - Prioritize detections for manual review
- [Complete Documentation Index](docs/README.md) - All documentation

### Scientific Validation
- [Validation Methodology](docs/scientific/SCIENTIFIC_VALIDATION_RESULTS.md) - Blind test (1,000 samples)
- [Gaulossen Case Study](docs/results/GAULOSSEN_RESULTS.md) - Real-world validation (6,805 detections)

---

## Contact

- **GitHub:** https://github.com/Ziforge/praven-pro
- **Related Study:** https://ziforge.github.io/gaulosen-study/
- **Email:** ghredpath@hotmail.com
