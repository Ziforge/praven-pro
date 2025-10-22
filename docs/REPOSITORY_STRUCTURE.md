# Praven Pro - Repository Structure

Complete organizational structure of the Praven Pro codebase.

---

## Repository Layout

```
praven-pro/
│
├── README.md                       # Project overview, badges, quick start
├── LICENSE                         # Non-commercial license terms
├── INSTALL.md                      # Installation instructions
├── QUICKSTART.md                   # Usage examples
├── COMPLETION_SUMMARY.md           # Development completion notes
├── REPOSITORY_STRUCTURE.md         # This file
│
├── docs/                           # All documentation
│   ├── README.md                   # Documentation index
│   ├── DIAGRAMS.md                 # Mermaid flow diagrams (GitHub-rendered)
│   ├── PROCESS_FLOW.md             # ASCII process flows
│   ├── SCREENSHOTS.md              # GUI screenshot guide
│   ├── TECHNICAL_SUMMARY.md        # System specifications
│   ├── PRAVEN_2.0_SUMMARY.md       # Architecture documentation
│   ├── EXTENSIONS_SUMMARY.md       # Feature implementations
│   ├── FUTURE_ENHANCEMENTS.md      # Roadmap and planned features
│   │
│   ├── guides/                     # User guides
│   │   └── SMART_REVIEW_GUIDE.md   # Review workflow (97% reduction)
│   │
│   ├── scientific/                 # Scientific validation
│   │   └── SCIENTIFIC_VALIDATION_RESULTS.md  # Blind test results
│   │
│   ├── results/                    # Case studies
│   │   └── GAULOSSEN_RESULTS.md    # Real-world validation
│   │
│   └── images/                     # Screenshots and diagrams
│       └── (screenshots captured separately)
│
├── praven/                         # Core Python package
│   ├── __init__.py
│   ├── validator.py                # Main BiologicalValidator class
│   ├── config.py                   # ValidationConfig class
│   ├── pipeline.py                 # ValidationPipeline automation
│   ├── review_selector.py          # SmartReviewSelector (top 3/species)
│   ├── visualization.py            # Dashboard HTML generation
│   │
│   ├── api/                        # External API clients
│   │   ├── __init__.py
│   │   ├── ebird_client.py         # eBird API wrapper
│   │   ├── ebird_preloader.py      # Auto-caching with 7-day TTL
│   │   └── gbif_client.py          # GBIF occurrence data
│   │
│   ├── rules/                      # Validation modules
│   │   ├── __init__.py
│   │   ├── geographic.py           # Range checking (eBird/GBIF)
│   │   ├── temporal.py             # Time-of-day validation
│   │   ├── habitat.py              # Habitat matching
│   │   └── taxonomic.py            # Family-level rules
│   │
│   └── data/                       # Reference databases
│       ├── species_db.json         # 62 manually curated species
│       └── taxonomic_rules.json    # 40 families, 4,000+ species
│
├── data/                           # Example data and outputs
│   ├── examples/                   # Sample CSV outputs
│   │   ├── gaulossen_auto_accepted.csv
│   │   ├── gaulossen_auto_rejected.csv
│   │   ├── gaulossen_needs_review.csv
│   │   └── gaulossen_automated_validation.csv
│   │
│   └── validation_output/          # Generated reports
│       └── validation_dashboard.html
│
├── validation/                     # Test datasets
│   ├── gaulossen_ground_truth.csv  # Expert-verified labels
│   └── gaulossen_all_detections.csv # BirdNET raw output
│
├── smart_review_demo/              # Smart review example outputs
│   ├── praven_results_*_full.csv
│   ├── praven_results_*_accepted.csv
│   ├── praven_results_*_rejected.csv
│   ├── praven_results_*_review.csv
│   ├── praven_results_*_PRIORITY_REVIEW.csv  # Top 3 per species
│   └── praven_results_*_summary.txt
│
├── validate.py                     # CLI interface
├── web_app.py                      # Web interface (Flask, port 5001)
│
├── setup.py                        # PyPI packaging (Python 2.x compatible)
├── pyproject.toml                  # Modern Python packaging
├── MANIFEST.in                     # Package data files
├── requirements.txt                # Python dependencies
│
└── cache/                          # Auto-managed eBird cache
    └── ebird_*.json                # 7-day TTL regional data
```

---

## File Organization Principles

### 1. Root Directory
Keep minimal: README, LICENSE, core scripts, packaging files only.

### 2. Documentation (`docs/`)
Organized by type:
- **guides/**: User-facing how-to documentation
- **scientific/**: Validation methodology and results
- **results/**: Case studies and real-world applications
- **images/**: Screenshots and visual assets

### 3. Code (`praven/`)
Modular structure:
- **api/**: External service integrations (eBird, GBIF)
- **rules/**: Validation logic (temporal, habitat, taxonomic)
- **data/**: Reference databases (JSON format)

### 4. Data (`data/`, `validation/`)
Separate example data from test data:
- **data/examples/**: Cleaned outputs for demonstration
- **validation/**: Ground truth data for testing
- **cache/**: Auto-managed temporary files

---

## Key Files

### User Interfaces

**`validate.py`** - Command-line interface
```bash
python validate.py input.csv --lat X --lon Y --habitat TYPE
```

**`web_app.py`** - Web interface
```bash
python web_app.py
# Access at http://localhost:5001
```

### Core Validation

**`praven/validator.py`**
- `BiologicalValidator` class
- Main validation engine
- Integrates all validation modules

**`praven/pipeline.py`**
- `ValidationPipeline` class
- End-to-end automation
- CSV input → validated output

**`praven/review_selector.py`**
- `SmartReviewSelector` class
- Top 3 per species selection
- Quality scoring algorithm

### Documentation

**`README.md`** - Start here
- Project overview
- Quick start examples
- Links to all documentation

**`docs/README.md`** - Documentation index
- Organized by topic
- Quick links to all guides

**`docs/DIAGRAMS.md`** - Visual workflows
- Mermaid diagrams (GitHub-rendered)
- System architecture
- Process flows

---

## Data Files

### Taxonomic Rules Database

**`praven/data/taxonomic_rules.json`**
- 40 bird families
- Activity patterns (diurnal/nocturnal/crepuscular)
- Habitat preferences (oceanic, forest, wetland, etc.)
- Example:
```json
{
  "Picidae": {
    "common_name": "Woodpeckers",
    "diurnal": true,
    "nocturnal": false,
    "habitat_preferences": {
      "forest": 0.95,
      "woodland": 0.85,
      "urban": 0.30
    }
  }
}
```

### Species Database

**`praven/data/species_db.json`**
- 62 manually curated species
- Detailed biological rules
- Override family-level rules when needed

---

## Output Files

Praven Pro generates 7 output files per validation:

1. **`*_full.csv`** - All detections with validation results
2. **`*_accepted.csv`** - Auto-accepted (high confidence + all checks pass)
3. **`*_rejected.csv`** - Auto-rejected (biological violations)
4. **`*_review.csv`** - All detections needing manual review
5. **`*_PRIORITY_REVIEW.csv`** - Top 3 per species (smart review)
6. **`*_summary.txt`** - Statistics and recommendations
7. **`*_dashboard.html`** - Interactive visualization

---

## Cache Management

**`cache/ebird_*.json`**
- Automatically created on first run
- 7-day TTL (time-to-live)
- Auto-refreshes when stale
- Format: `ebird_{lat}_{lon}_{radius}km.json`

**Cache Policy:**
- Check age on every program run
- If >= 7 days old: download fresh data
- If < 7 days old: use cached data
- No manual cache management required

---

## Development Files

### Packaging

**`setup.py`** - Traditional packaging
- Python 2.x/3.x compatible
- PyPI upload support
- Entry points: `praven` and `praven-web`

**`pyproject.toml`** - Modern packaging
- PEP 517/518 compliant
- Dependency specification
- Metadata

**`MANIFEST.in`** - Package data
- Includes JSON databases
- Includes documentation files

### Dependencies

**`requirements.txt`**
```
pandas>=1.5.0
numpy>=1.20.0
requests>=2.25.0
scikit-learn>=1.0.0
pydantic>=2.0.0
```

**Optional:**
```
flask>=2.0.0              # Web interface
plotly>=5.0.0             # Visualization
```

---

## Version Control

### Ignored Files (.gitignore)
```
cache/                    # Auto-managed eBird cache
*.pyc                     # Python bytecode
__pycache__/              # Python cache
.DS_Store                 # macOS files
*.egg-info/               # Build artifacts
dist/                     # Distribution builds
build/                    # Build directory
```

### Tracked Files
- All source code (`.py`)
- All documentation (`.md`)
- Reference databases (`.json`)
- Example data (`.csv` in `data/examples/`)
- License and packaging files

---

## Future Structure Changes

Planned for v2.2:
- `praven/api/weather_client.py` - Weather API integration
- `praven/api/habitat_client.py` - Habitat detection from GPS
- `docs/videos/` - Tutorial videos
- `tests/` - Comprehensive test suite

---

## Quick Navigation

**Want to...**
- Get started? → `README.md`
- Install? → `INSTALL.md`
- See examples? → `QUICKSTART.md`
- Understand the system? → `docs/TECHNICAL_SUMMARY.md`
- See validation results? → `docs/scientific/SCIENTIFIC_VALIDATION_RESULTS.md`
- Learn smart review? → `docs/guides/SMART_REVIEW_GUIDE.md`
- View diagrams? → `docs/DIAGRAMS.md`
- Contribute? → `docs/FUTURE_ENHANCEMENTS.md`

---

## Contact

- Repository: https://github.com/Ziforge/praven-pro
- Issues: https://github.com/Ziforge/praven-pro/issues
- Email: ghredpath@hotmail.com
