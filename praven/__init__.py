"""
Praven Pro - BirdNET Biological Validation Toolkit

Automated validation for BirdNET acoustic monitoring using:
- Geographic occurrence data (eBird, GBIF)
- Temporal patterns (time-of-day, seasonality)
- Habitat matching
- Weather-activity correlation

Example:
    from praven import BiologicalValidator, ValidationConfig

    config = ValidationConfig(
        location=(63.341, 10.215),
        date="2025-10-13",
        habitat_type="wetland",
        ebird_api_key="your-key"
    )

    validator = BiologicalValidator(config)

    result = validator.validate_detection(
        species="Great Snipe",
        timestamp="2025-10-13 20:00:00",
        confidence=0.85
    )

    print(result.status)  # ACCEPT, REJECT, or REVIEW
"""

__version__ = "1.0.0"

from .validator import BiologicalValidator
from .config import ValidationConfig, ValidationResult, WeatherConditions
from .api import eBirdClient, GBIFClient
from .rules import GeographicValidator, TemporalValidator, HabitatValidator
from .models import WeatherActivityModel

__all__ = [
    'BiologicalValidator',
    'ValidationConfig',
    'ValidationResult',
    'WeatherConditions',
    'eBirdClient',
    'GBIFClient',
    'GeographicValidator',
    'TemporalValidator',
    'HabitatValidator',
    'WeatherActivityModel',
]
