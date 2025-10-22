# Praven Pro - Process Flow Diagrams

## 1. Overall Validation Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                     BirdNET Detection CSV                       │
│                  (6,805 raw detections)                         │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Praven Pro Validator                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Temporal   │  │   Habitat    │  │  Geographic  │         │
│  │  Validation  │  │  Validation  │  │  Validation  │         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
│         │                 │                  │                  │
│         └─────────────────┴──────────────────┘                  │
│                           │                                     │
│                           ▼                                     │
│                  ┌─────────────────┐                           │
│                  │  Taxonomic      │                           │
│                  │  Rules Engine   │                           │
│                  └────────┬────────┘                           │
└──────────────────────────┬────────────────────────────────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │  Validation Decision   │
              └────────┬───────────────┘
                       │
         ┌─────────────┼─────────────┐
         │             │             │
         ▼             ▼             ▼
    ┌────────┐    ┌────────┐   ┌────────┐
    │ ACCEPT │    │ REVIEW │   │ REJECT │
    │  581   │    │ 6,201  │   │   23   │
    └────────┘    └───┬────┘   └────────┘
                      │
                      ▼
         ┌─────────────────────────┐
         │  Smart Review Selection │
         │   (Top 3 per species)   │
         └────────┬────────────────┘
                  │
                  ▼
         ┌─────────────────┐
         │ Priority Review │
         │   192 samples   │
         └─────────────────┘
```

## 2. Temporal Validation Logic

```
Detection at time T
         │
         ▼
┌────────────────────┐
│ Get species info   │
│ from taxonomic DB  │
└────────┬───────────┘
         │
         ▼
┌──────────────────────────────────┐
│  Family: Picidae (Woodpeckers)   │
│  Rule: Strictly diurnal          │
│  Activity: 06:00 - 20:00         │
└────────┬─────────────────────────┘
         │
         ▼
    Is T in [06:00, 20:00]?
         │
    ┌────┴────┐
    │         │
   YES       NO
    │         │
    ▼         ▼
  PASS     REJECT
           "Nocturnal detection
            of diurnal species"
```

## 3. Habitat Validation Logic

```
Detection in habitat H
         │
         ▼
┌──────────────────────┐
│ Get species habitat  │
│ preferences from DB  │
└──────────┬───────────┘
           │
           ▼
┌───────────────────────────────┐
│ European Storm-Petrel         │
│ Preferences:                  │
│   Oceanic:  1.0 (required)    │
│   Wetland:  0.0 (never)       │
│   Forest:   0.0 (never)       │
└────────┬──────────────────────┘
         │
         ▼
  Score(H) >= 0.3?
         │
    ┌────┴────┐
    │         │
   YES       NO
    │         │
    ▼         ▼
  PASS     REJECT
           "Oceanic species
            detected inland"
```

## 4. Smart Review Selection

```
6,201 Detections needing REVIEW
         │
         ▼
┌────────────────────────┐
│ Group by species       │
│ (64 unique species)    │
└───────┬────────────────┘
        │
        ▼
For each species:
┌─────────────────────────────────┐
│ Calculate quality score:        │
│   = confidence                  │
│   + 0.10 (if no warnings)       │
│   + 0.05 (if temporal valid)    │
│   + 0.05 (if habitat valid)     │
└───────┬─────────────────────────┘
        │
        ▼
┌─────────────────────────┐
│ Sort by quality score   │
│ (highest first)         │
└───────┬─────────────────┘
        │
        ▼
┌─────────────────────────┐
│ Select top 3            │
└───────┬─────────────────┘
        │
        ▼
     192 priority
    detections
  (64 species × 3)
```

## 5. Review Workflow

```
Researcher opens PRIORITY_REVIEW.csv
         │
         ▼
┌──────────────────────────┐
│ For each species:        │
│ Review top 3 detections  │
└────────┬─────────────────┘
         │
         ▼
  Check spectrograms
         │
    ┌────┴────┐
    │         │
All 3      Mixed      All 3
valid               invalid
    │         │         │
    ▼         ▼         ▼
ACCEPT    Review    REJECT
species    more     species
  all      from       all
detections review  detections
           .csv
```

## 6. Data Flow

```
INPUT:
  BirdNET CSV + Study metadata
         │
         ▼
PROCESSING:
  ┌──────────────────┐
  │ Load & validate  │
  ├──────────────────┤
  │ Temporal rules   │
  ├──────────────────┤
  │ Habitat rules    │
  ├──────────────────┤
  │ Geographic check │
  ├──────────────────┤
  │ Taxonomic rules  │
  └────────┬─────────┘
           │
           ▼
OUTPUT FILES:
  ├─ full.csv (all results)
  ├─ accepted.csv (auto-validated)
  ├─ rejected.csv (biological violations)
  ├─ review.csv (all uncertain)
  ├─ PRIORITY_REVIEW.csv (top 3/species)
  ├─ summary.txt (statistics)
  └─ dashboard.html (visualization)
```

## 7. eBird Data Management

```
Program starts
      │
      ▼
┌────────────────┐
│ Check cache    │
│ exists?        │
└───┬────────────┘
    │
 ┌──┴──┐
NO    YES
 │      │
 │      ▼
 │  ┌──────────────┐
 │  │ Check age    │
 │  │ < 7 days?    │
 │  └──┬───────────┘
 │     │
 │  ┌──┴──┐
 │ NO    YES
 │  │      │
 │  │      ▼
 │  │  Use cached
 │  │  data
 │  │
 ▼  ▼
Download
from eBird
   │
   ▼
Save to
cache
   │
   ▼
Proceed with
validation
```

## 8. System Architecture

```
┌─────────────────────────────────────────────┐
│              USER INTERFACES                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │   CLI    │  │   Web    │  │  Python  │  │
│  │ validate │  │   App    │  │   API    │  │
│  │   .py    │  │  :5001   │  │          │  │
│  └─────┬────┘  └─────┬────┘  └─────┬────┘  │
└────────┼─────────────┼─────────────┼────────┘
         │             │             │
         └─────────────┴─────────────┘
                       │
         ┌─────────────▼─────────────┐
         │    ValidationPipeline     │
         └─────────────┬─────────────┘
                       │
         ┌─────────────▼─────────────┐
         │   BiologicalValidator     │
         │  ┌────────────────────┐   │
         │  │ TemporalValidator  │   │
         │  ├────────────────────┤   │
         │  │ HabitatValidator   │   │
         │  ├────────────────────┤   │
         │  │GeographicValidator │   │
         │  ├────────────────────┤   │
         │  │ TaxonomicValidator │   │
         │  └────────────────────┘   │
         └─────────────┬─────────────┘
                       │
         ┌─────────────▼─────────────┐
         │     SmartReviewSelector   │
         └───────────────────────────┘
```

## 9. Taxonomic Rule Application

```
Detection: "Downy Woodpecker"
         │
         ▼
┌────────────────────┐
│ Parse common name  │
│ Find: "Woodpecker" │
└────────┬───────────┘
         │
         ▼
┌────────────────────┐
│ Lookup family      │
│ Family: Picidae    │
└────────┬───────────┘
         │
         ▼
┌──────────────────────────────┐
│ Load family rules:           │
│  - diurnal: true             │
│  - nocturnal: false          │
│  - habitat: forest (0.95)    │
└────────┬─────────────────────┘
         │
         ▼
Apply rules to detection
         │
         ▼
    Validation
     result
```

## 10. Quality Score Calculation

```
Detection:
  Species: Graylag Goose
  Confidence: 0.85
  Time: 14:30 (valid)
  Habitat: Wetland (match)
  Warnings: None

Quality Score Calculation:
┌───────────────────────────┐
│ Base: 0.85 (confidence)   │
├───────────────────────────┤
│ +0.10 (no warnings)       │
├───────────────────────────┤
│ +0.05 (temporal valid)    │
├───────────────────────────┤
│ +0.05 (habitat valid)     │
├───────────────────────────┤
│ = 1.05 (final score)      │
└───────────────────────────┘

Used for ranking within species
to select top 3 representatives
```
