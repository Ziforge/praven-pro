# Praven Pro - System Diagrams

This document contains all system architecture and process flow diagrams using Mermaid notation for GitHub rendering.

---

## 1. Overall Validation Pipeline

```mermaid
flowchart TD
    A[BirdNET Detection CSV<br/>6,805 raw detections] --> B[Praven Pro Validator]
    B --> C[Temporal Validation]
    B --> D[Habitat Validation]
    B --> E[Geographic Validation]
    C --> F[Taxonomic Rules Engine]
    D --> F
    E --> F
    F --> G{Validation Decision}
    G -->|High Confidence| H[ACCEPT<br/>581 detections]
    G -->|Uncertain| I[REVIEW<br/>6,201 detections]
    G -->|Violations| J[REJECT<br/>23 detections]
    I --> K[Smart Review Selection<br/>Top 3 per species]
    K --> L[Priority Review<br/>192 samples]

    style H fill:#90EE90
    style J fill:#FFB6C6
    style I fill:#FFE4B5
    style L fill:#87CEEB
```

---

## 2. Temporal Validation Logic

```mermaid
flowchart TD
    A[Detection at time T] --> B[Get species info from<br/>taxonomic database]
    B --> C{Family: Picidae<br/>Woodpeckers}
    C --> D[Rule: Strictly diurnal<br/>Activity: 06:00 - 20:00]
    D --> E{Is T in<br/>06:00-20:00?}
    E -->|YES| F[PASS]
    E -->|NO| G[REJECT<br/>Nocturnal detection<br/>of diurnal species]

    style F fill:#90EE90
    style G fill:#FFB6C6
```

---

## 3. Habitat Validation Logic

```mermaid
flowchart TD
    A[Detection in habitat H] --> B[Get species habitat<br/>preferences from DB]
    B --> C[European Storm-Petrel<br/>Oceanic: 1.0 required<br/>Wetland: 0.0 never<br/>Forest: 0.0 never]
    C --> D{Habitat Score H<br/>>= 0.3?}
    D -->|YES| E[PASS]
    D -->|NO| F[REJECT<br/>Oceanic species<br/>detected inland]

    style E fill:#90EE90
    style F fill:#FFB6C6
```

---

## 4. Smart Review Selection Process

```mermaid
flowchart TD
    A[6,201 Detections<br/>needing REVIEW] --> B[Group by species<br/>64 unique species]
    B --> C[For each species:<br/>Calculate quality score]
    C --> D[Quality Score =<br/>confidence + bonuses]
    D --> E[+0.10 if no warnings<br/>+0.05 if temporal valid<br/>+0.05 if habitat valid]
    E --> F[Sort by quality score<br/>highest first]
    F --> G[Select top 3<br/>per species]
    G --> H[192 priority detections<br/>64 species × 3]

    style H fill:#87CEEB
```

---

## 5. Review Workflow

```mermaid
flowchart TD
    A[Researcher opens<br/>PRIORITY_REVIEW.csv] --> B[For each species:<br/>Review top 3 detections]
    B --> C[Check spectrograms]
    C --> D{Quality?}
    D -->|All 3 valid| E[ACCEPT<br/>species - all detections]
    D -->|Mixed| F[Review more<br/>from review.csv]
    D -->|All 3 invalid| G[REJECT<br/>species - all detections]

    style E fill:#90EE90
    style G fill:#FFB6C6
    style F fill:#FFE4B5
```

---

## 6. Data Flow

```mermaid
flowchart LR
    A[INPUT:<br/>BirdNET CSV +<br/>Study metadata] --> B[PROCESSING]
    B --> C[Load & validate]
    C --> D[Temporal rules]
    D --> E[Habitat rules]
    E --> F[Geographic check]
    F --> G[Taxonomic rules]
    G --> H[OUTPUT FILES]
    H --> I[full.csv]
    H --> J[accepted.csv]
    H --> K[rejected.csv]
    H --> L[review.csv]
    H --> M[PRIORITY_REVIEW.csv]
    H --> N[summary.txt]
    H --> O[dashboard.html]

    style M fill:#87CEEB
```

---

## 7. eBird Data Management

```mermaid
flowchart TD
    A[Program starts] --> B{Cache<br/>exists?}
    B -->|NO| C[Download from eBird]
    B -->|YES| D{Cache age<br/>< 7 days?}
    D -->|YES| E[Use cached data]
    D -->|NO| C
    C --> F[Save to cache]
    F --> G[Proceed with validation]
    E --> G

    style E fill:#90EE90
```

---

## 8. System Architecture

```mermaid
graph TB
    subgraph UI[USER INTERFACES]
        CLI[CLI<br/>validate.py]
        WEB[Web App<br/>:5001]
        API[Python API]
    end

    UI --> PIPE[ValidationPipeline]
    PIPE --> VAL[BiologicalValidator]

    subgraph VALIDATORS
        TEMP[TemporalValidator]
        HAB[HabitatValidator]
        GEO[GeographicValidator]
        TAX[TaxonomicValidator]
    end

    VAL --> VALIDATORS
    VALIDATORS --> REV[SmartReviewSelector]

    style PIPE fill:#87CEEB
    style VAL fill:#DDA0DD
```

---

## 9. Taxonomic Rule Application

```mermaid
flowchart TD
    A[Detection:<br/>Downy Woodpecker] --> B[Parse common name<br/>Find: Woodpecker]
    B --> C[Lookup family<br/>Family: Picidae]
    C --> D[Load family rules:<br/>- diurnal: true<br/>- nocturnal: false<br/>- habitat: forest 0.95]
    D --> E[Apply rules to detection]
    E --> F[Validation result]

    style F fill:#87CEEB
```

---

## 10. Quality Score Calculation

```mermaid
flowchart TD
    A[Detection:<br/>Graylag Goose<br/>Confidence: 0.85<br/>Time: 14:30 valid<br/>Habitat: Wetland match<br/>Warnings: None] --> B[Base: 0.85<br/>confidence]
    B --> C[+0.10<br/>no warnings]
    C --> D[+0.05<br/>temporal valid]
    D --> E[+0.05<br/>habitat valid]
    E --> F[Final Score: 1.05]
    F --> G[Used for ranking<br/>within species to<br/>select top 3]

    style F fill:#FFD700
    style G fill:#87CEEB
```

---

## 11. Complete Workflow Integration

```mermaid
graph LR
    subgraph Input
        CSV[BirdNET CSV]
        META[Study Metadata<br/>Location, Date, Habitat]
    end

    CSV --> LOAD[Load & Parse]
    META --> LOAD

    LOAD --> CACHE{eBird Cache<br/>Check}
    CACHE -->|Stale| DL[Download Fresh]
    CACHE -->|Valid| VAL
    DL --> VAL[Validate All<br/>Detections]

    VAL --> SPLIT{Classification}
    SPLIT -->|Auto| ACC[ACCEPT: 581]
    SPLIT -->|Issues| REJ[REJECT: 23]
    SPLIT -->|Uncertain| REV[REVIEW: 6,201]

    REV --> SMART[Smart Review<br/>Selection]
    SMART --> PRIOR[Priority: 192<br/>Top 3/species]

    ACC --> OUT[Export Results]
    REJ --> OUT
    PRIOR --> OUT

    OUT --> FILES[7 Output Files]

    style PRIOR fill:#87CEEB
    style FILES fill:#90EE90
```

---

## Diagram Legend

**Colors:**
- 🟢 Green: Accepted/Valid results
- 🔴 Pink: Rejected/Invalid results
- 🟡 Tan: Review required
- 🔵 Blue: Priority/Important outputs
- 🟣 Purple: Core processing components
- 🟠 Gold: Calculated metrics

**Node Shapes:**
- Rectangle: Process/Action
- Diamond: Decision point
- Rounded: Input/Output
- Cylinder: Data storage
