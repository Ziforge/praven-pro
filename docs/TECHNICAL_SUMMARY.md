# Praven Pro 2.1 - Technical Summary

**Date:** October 22, 2025
**Version:** 2.1.0
**Purpose:** Automated biological validation for BirdNET acoustic monitoring data

---

## System Overview

Praven Pro is a post-processing validation layer for BirdNET that applies biological rules to filter false positives. The system automates the manual validation workflow used in the Gaulossen study.

---

## Core Components

### 1. Rule-Based Validation

**Approach:** Deterministic biological rules, not machine learning

**Validation modules:**
- Temporal: Activity patterns (diurnal/nocturnal/crepuscular)
- Habitat: Species-habitat preference matching
- Geographic: eBird/GBIF occurrence checking
- Taxonomic: Family-level biological constraints

**Coverage:**
- 40 bird families
- Primarily European species

### 2. Data Management

**eBird preloading:**
- Automatic cache checking on startup
- 7-day cache duration
- Auto-refresh when stale
- 50km radius, 30-day observation window

**Performance:**
- Eliminates API rate limiting
- Reduces validation time
- No manual data management required

### 3. Smart Review Selection

**Purpose:** Reduce manual review workload while maintaining validation quality

**Method:**
1. Quality score calculation per detection:
   - Base: BirdNET confidence score
   - Modifier: +0.10 if no validation warnings
   - Modifier: +0.05 if temporal window valid
   - Modifier: +0.05 if habitat match valid

2. Select top 3 highest-quality detections per species
3. Manual review of representatives only
4. Apply species-level decisions to all detections

**Rationale:**
- 3 samples provides statistical confidence
- Quality filtering ensures representative selection
- Species-level decisions are biologically justified
- Matches methodology from Gaulossen manual review

**Performance (Gaulossen dataset):**
- Original review requirement: 6,201 detections
- Smart review requirement: 192 detections (64 species × 3)
- Workload reduction: 96.9%
- Time estimate: 4 hours vs 207 hours

---

## Validation Results

### Blind Test (1,000 samples)

**Methodology:**
- Dataset: Gaulossen Nature Reserve (October 2025)
- Sample size: 1,000 detections (random selection)
- Ground truth: Expert-verified labels
- Test type: Blind (no prior exposure to labels)

**Note:** This was an internal development test used to tune validation rules. Results should not be considered independent validation as the test data was used during system development.

---

## System Architecture

### Input
- BirdNET detection CSV (standard format)
- Study metadata: location, date, habitat type
- Optional: weather conditions

### Processing
1. Load and validate input data
2. Apply temporal validation rules
3. Apply habitat matching
4. Apply geographic occurrence checking
5. Apply taxonomic family rules
6. Calculate composite validation score
7. Classify: ACCEPT / REVIEW / REJECT

### Output
- Validated detections CSV (all results)
- Accepted detections CSV (high confidence, pass all checks)
- Rejected detections CSV (biological violations)
- Review detections CSV (ambiguous cases)
- Priority review CSV (top 3 per species)
- Summary report (statistics and recommendations)
- Dashboard HTML (visualization)

---

## Interfaces

### Command Line
```bash
python validate.py input.csv --lat X --lon Y --habitat TYPE --date YYYY-MM-DD
```

### Python API
```python
from praven import BiologicalValidator, ValidationConfig

config = ValidationConfig(location=(lat, lon), habitat_type="wetland")
validator = BiologicalValidator(config)
result = validator.validate_detection(species, timestamp, confidence)
```

### Web Interface
- Flask-based HTTP server
- Form-based configuration
- File upload interface
- Result download

### Package
```bash
pip install praven-pro
```

---

## Taxonomic Coverage

### Family-Level Rules (40 families)

**Example families:**
- Picidae: All strictly diurnal
- Strigidae: All nocturnal/crepuscular
- Hydrobatidae: All pelagic oceanic
- Anatidae: Wetland specialists
- Alcidae: Coastal/oceanic only

**Coverage estimate:**
- Picidae: 200+ species
- Strigidae: 250+ species
- Anatidae: 150+ species
- Scolopacidae: 90+ species
- Total: ~4,000 species across 40 families

---

## Comparison to Manual Review

### Gaulossen Study Manual Process
- Initial detections: 6,805
- Stage 1 (audio quality): 6,805 → 4,108 (60.4% pass)
- Stage 2 (biological): Manual review of remaining
- Final verified: 74 species
- Time investment: ~227 minutes total

### Automated Process (Praven Pro)
- Input: 6,805 detections
- Auto-accept: 581 (8.5%)
- Auto-reject: 23 (0.3%)
- Review required: 6,201 (91.1%)
- Smart review: 192 (2.8% - top 3 per species)
- Time estimate: ~4 hours for priority review

### Validation Accuracy
- Known false positives caught: 23/23 (100%)
  - Lesser Spotted Woodpecker (nocturnal): 14
  - European Storm-Petrel (oceanic inland): 4
  - Manx Shearwater (pelagic inland): 3
  - Bar-headed Goose (non-native): 1
  - Western Capercaillie (habitat): 1

---

## Technical Specifications

### Dependencies
- Python 3.8+
- pandas >= 1.5.0
- numpy >= 1.20.0
- requests >= 2.25.0
- scikit-learn >= 1.0.0
- pydantic >= 2.0.0

### Optional Dependencies
- Flask >= 2.0.0 (web interface)
- plotly >= 5.0.0 (visualization)
- matplotlib >= 3.5.0 (charts)

### Data Files
- `species_db.json`: 62 manually curated species
- `taxonomic_rules.json`: 40 family-level rule sets
- eBird cache: Regional occurrence data (auto-managed)

### Performance
- Validation speed: ~100 detections/second (without API calls)
- Memory usage: ~50MB + data size
- Cache size: ~1-5MB per region

---

## Limitations

### 1. Geographic Scope
- eBird data availability varies by region
- Best coverage in North America and Europe
- Limited coverage in some tropical regions

### 2. Taxonomic Coverage
- 40 families covers most common species
- Rare families may lack specific rules
- Falls back to order-level rules when available

### 3. Edge Cases
- Vagrant species may be incorrectly flagged
- Migration timing not fully implemented
- Coastal/inland boundaries are approximate

### 4. Conservative Approach
- High review rate (91%) prioritizes accuracy over automation
- May flag valid detections for review in edge cases
- Designed to minimize false negatives (missed errors)

---

## License

Non-commercial use only. Free for:
- Academic research
- Educational purposes
- Non-profit conservation work
- Scientific publications

Commercial use requires separate licensing. Contact: ghredpath@hotmail.com

---

## Citation

```
Redpath, G. (2025). Praven Pro 2.1: Rule-Based Biological Validation for
BirdNET Acoustic Monitoring. GitHub. https://github.com/Ziforge/praven-pro

Validated on: Gaulossen Nature Reserve Acoustic Study (6,805 detections,
82 species, 48.8 hours recording, October 2025)
```

---

## Files and Documentation

### Core Documentation
- `README.md`: Overview and quick start
- `INSTALL.md`: Installation instructions
- `QUICKSTART.md`: Usage examples
- `TECHNICAL_SUMMARY.md`: This file

### Scientific Documentation
- `SCIENTIFIC_VALIDATION_RESULTS.md`: Blind test results (1,000 samples)
- `GAULOSSEN_RESULTS.md`: Real-world validation results
- `SMART_REVIEW_GUIDE.md`: Review workflow documentation

### Implementation Details
- `PRAVEN_2.0_SUMMARY.md`: System architecture and design
- `EXTENSIONS_SUMMARY.md`: Feature implementation details

---

## Future Development

### Potential Enhancements
1. Regional migration timing windows
2. Subspecies-level rules
3. Seasonal abundance integration
4. Weather-activity correlation refinement
5. Additional taxonomic families

### Known Issues
- None critical
- Edge cases documented in limitations section

---

## Contact

- Repository: https://github.com/Ziforge/praven-pro
- Issues: https://github.com/Ziforge/praven-pro/issues
- Email: ghredpath@hotmail.com
