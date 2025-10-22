# Praven Pro - Future Enhancements

Potential features and improvements for future releases.

---

## Planned Features

### 1. Automatic Habitat Type Detection

**Priority:** High
**Status:** Planned for v2.2

**Description:**
Automatically determine habitat type from GPS coordinates using land cover databases. Support hybrid habitats (e.g., wetland-forest transition zones).

**Implementation:**
- Use land cover APIs (e.g., ESA WorldCover, CORINE Land Cover)
- Input: GPS coordinates (lat/lon)
- Output: Primary habitat + hybrid habitat percentages
- Example: "wetland (70%), forest (30%)"

**Technical Details:**
```python
# New module: praven/api/habitat_client.py
class HabitatClient:
    def get_habitat_from_coords(self, lat, lon):
        """Determine habitat type from coordinates."""
        # Query land cover database
        # Return: {primary: "wetland", hybrid: ["forest": 0.3]}
```

**Benefits:**
- Eliminates manual habitat classification errors
- Captures habitat complexity (transition zones)
- More accurate habitat validation
- Automated workflow

**API Options:**
1. ESA WorldCover (10m resolution, free)
2. CORINE Land Cover (Europe, 100m resolution)
3. OpenStreetMap land use data
4. Google Earth Engine

---

### 2. Automatic Weather Data Integration

**Priority:** High
**Status:** Planned for v2.2

**Description:**
Automatically fetch local weather conditions based on GPS coordinates and date/time from the detection data. This would eliminate manual weather input and provide more accurate validation.

**Implementation:**
- Use weather API (OpenWeatherMap, WeatherAPI, or NOAA) to fetch historical weather data
- Input: GPS coordinates (lat/lon) from GUI or detection metadata
- Retrieve: Temperature, precipitation, fog/visibility, wind conditions
- Cache weather data by location + date to minimize API calls
- Fallback to manual input if API unavailable

**Benefits:**
- Eliminates manual weather input errors
- More accurate temporal validation (weather-dependent activity patterns)
- Automated workflow requires less user input
- Historical weather data for retrospective studies

**Technical Details:**
```python
# New module: praven/api/weather_client.py
class WeatherClient:
    def get_historical_weather(self, lat, lon, datetime):
        """Fetch weather conditions for specific location and time."""
        # Check cache first
        # Query weather API
        # Return: {rain, fog, temp, wind, ...}
```

**API Options:**
1. OpenWeatherMap (free tier: 1,000 calls/day)
2. WeatherAPI (free tier: 1M calls/month)
3. NOAA (free, US-focused)
4. Open-Meteo (free, no API key required)

**User Experience:**
```bash
# Before (manual weather input)
python validate.py detections.csv --lat 63.341 --lon 10.215 \
  --habitat wetland --rain 0.3 --fog 0.5

# After (automatic weather fetching)
python validate.py detections.csv --lat 63.341 --lon 10.215 \
  --habitat wetland --auto-weather

# Or web GUI: checkbox "Fetch weather automatically"
```

---

## Proposed Enhancements

### 2. Migration Timing Windows

**Priority:** Medium
**Status:** Research phase

**Description:**
Incorporate species-specific migration timing to improve seasonal validation accuracy.

**Implementation:**
- Add migration windows to taxonomic rules
- Validate detections against expected presence dates
- Flag out-of-season detections for review

**Example:**
```json
{
  "Common Redstart": {
    "migration": {
      "spring_arrival": "2025-04-15",
      "fall_departure": "2025-09-30",
      "winter_range": "africa"
    }
  }
}
```

---

### 3. Subspecies-Level Rules

**Priority:** Low
**Status:** Future consideration

**Description:**
Expand rules to handle subspecies with different ranges or behaviors.

**Example:**
- Hooded Crow (European) vs Carrion Crow (Asian)
- Different habitat preferences or ranges

**Challenge:**
- BirdNET doesn't always differentiate subspecies
- Would require subspecies identification in input data

---

### 4. Confidence Score Calibration

**Priority:** Medium
**Status:** Research phase

**Description:**
Calibrate BirdNET confidence scores based on validation results to improve auto-accept thresholds.

**Implementation:**
- Analyze relationship between BirdNET confidence and validation success
- Adjust acceptance thresholds per species or family
- Learn from user review decisions

---

### 5. Interactive Dashboard

**Priority:** Medium
**Status:** Planned for v2.3

**Description:**
Web-based dashboard for real-time validation monitoring and manual review.

**Features:**
- Live validation progress
- Interactive spectrogram viewer for review detections
- One-click accept/reject decisions
- Species-level decision application
- Annotation and note-taking

---

### 6. Batch Processing API

**Priority:** Low
**Status:** Future consideration

**Description:**
RESTful API for processing multiple studies simultaneously.

**Use Case:**
- Large-scale monitoring programs
- Automated pipeline integration
- Cloud deployment

---

### 7. Regional eBird Frequency Data

**Priority:** Medium
**Status:** Research phase

**Description:**
Incorporate eBird frequency data to weight species likelihood.

**Implementation:**
- Use eBird frequency/abundance data
- Adjust validation thresholds based on species rarity
- Flag uncommon species for extra review

---

### 8. Audio Quality Filtering

**Priority:** Low
**Status:** Future consideration

**Description:**
Pre-filter low-quality audio before biological validation.

**Implementation:**
- SNR (signal-to-noise ratio) thresholding
- Spectrogram quality assessment
- Filter out recordings with high background noise

---

### 9. Multi-Language Support

**Priority:** Low
**Status:** Future consideration

**Description:**
Support for non-English species names and documentation.

**Languages:**
- Norwegian (Gaulossen study region)
- German, French, Spanish (European monitoring)

---

### 10. Automated Report Generation

**Priority:** Medium
**Status:** Planned for v2.2

**Description:**
Generate PDF reports with validation results, maps, and charts.

**Features:**
- LaTeX-based report generation
- Species distribution maps
- Validation statistics charts
- Summary tables
- Export to scientific publication format

---

## Technical Debt

### Code Refactoring
- [ ] Separate validation rules into modular plugins
- [ ] Improve error handling in API clients
- [ ] Add comprehensive unit tests (current coverage: ~60%)
- [ ] Type hints for all public APIs

### Performance Optimization
- [ ] Parallel processing for large datasets
- [ ] Database backend for large taxonomic rules (currently JSON)
- [ ] Optimize eBird cache queries

### Documentation
- [ ] Video tutorials for web interface
- [ ] API reference documentation (Sphinx)
- [ ] Contributing guidelines

---

## Community Requests

Track feature requests from users here.

### Request Template
```
Feature: [Name]
Requested by: [User/Organization]
Priority: [High/Medium/Low]
Description: [What they need]
Use case: [Why they need it]
Status: [Under review/Planned/Declined]
```

---

## Version Roadmap

### v2.2 (Q1 2026)
- Automatic weather data integration
- Automated PDF report generation
- Performance optimizations for large datasets

### v2.3 (Q2 2026)
- Interactive web dashboard
- Migration timing windows
- Confidence score calibration

### v3.0 (Future)
- Subspecies-level rules
- Multi-language support
- Cloud API deployment

---

## Contributing

Interested in implementing any of these features? Contact ghredpath@hotmail.com or open a GitHub issue.

---

## Notes

This document is a living roadmap. Features may be reprioritized based on:
- User feedback
- Scientific validation results
- Community contributions
- Available development resources
