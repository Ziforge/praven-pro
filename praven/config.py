"""
Configuration management for Praven Pro validation system.
"""

import os
from typing import Tuple, Dict, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class ValidationConfig(BaseModel):
    """Configuration for biological validation."""

    # Location
    location: Tuple[float, float] = Field(
        ...,
        description="Latitude and longitude (decimal degrees)"
    )

    # Temporal
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    time_range: Optional[Tuple[str, str]] = Field(
        None,
        description="Optional time range (HH:MM, HH:MM)"
    )

    # Habitat
    habitat_type: Optional[str] = Field(
        None,
        description="Primary habitat type: wetland, forest, oceanic, grassland, urban (auto-detected if None)"
    )
    habitat_radius_m: int = Field(
        1000,
        description="Radius in meters for habitat matching and auto-detection"
    )
    auto_detect_habitat: bool = Field(
        True,
        description="Automatically detect habitat from GPS coordinates"
    )

    # Weather
    weather_conditions: Optional[Dict[str, float]] = Field(
        None,
        description="Weather conditions: {rain: 0-1, fog: 0-1, temperature: celsius} (auto-fetched if None)"
    )
    auto_detect_weather: bool = Field(
        True,
        description="Automatically fetch weather data from GPS coordinates and date"
    )

    # API settings
    ebird_api_key: Optional[str] = Field(
        None,
        description="eBird API key (or use EBIRD_API_KEY env var)"
    )

    # Validation thresholds
    min_confidence: float = Field(0.1, ge=0.0, le=1.0)
    geographic_radius_km: float = Field(50.0, description="Radius for occurrence checks")
    temporal_tolerance_days: int = Field(14, description="Days before/after for seasonality")

    # Caching
    cache_dir: str = Field("cache", description="Directory for API response caching")
    cache_ttl_hours: int = Field(24, description="Cache time-to-live in hours")

    @field_validator('date')
    @classmethod
    def validate_date(cls, v: str) -> str:
        """Validate date format."""
        try:
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")

    @field_validator('habitat_type')
    @classmethod
    def validate_habitat(cls, v: Optional[str]) -> Optional[str]:
        """Validate habitat type."""
        if v is None:
            return None  # Will be auto-detected
        valid_habitats = ['wetland', 'forest', 'oceanic', 'grassland', 'urban', 'mixed', 'unknown', 'agricultural']
        if v.lower() not in valid_habitats:
            raise ValueError(f"Habitat must be one of: {', '.join(valid_habitats)}")
        return v.lower()

    @field_validator('location')
    @classmethod
    def validate_location(cls, v: Tuple[float, float]) -> Tuple[float, float]:
        """Validate latitude and longitude."""
        lat, lon = v
        if not (-90 <= lat <= 90):
            raise ValueError("Latitude must be between -90 and 90")
        if not (-180 <= lon <= 180):
            raise ValueError("Longitude must be between -180 and 180")
        return v

    def model_post_init(self, __context) -> None:
        """Post-initialization processing."""
        # Get eBird API key from environment if not provided
        if self.ebird_api_key is None:
            self.ebird_api_key = os.getenv('EBIRD_API_KEY')

        # Auto-detect habitat if enabled and not provided
        if self.auto_detect_habitat and self.habitat_type is None:
            print(f"🌍 Auto-detecting habitat from GPS coordinates...")
            self._auto_detect_habitat()

        # Auto-fetch weather if enabled and not provided
        if self.auto_detect_weather and self.weather_conditions is None:
            print(f"🌤️  Auto-fetching weather data...")
            self._auto_fetch_weather()

    def _auto_detect_habitat(self) -> None:
        """Automatically detect habitat from GPS coordinates."""
        try:
            from .api.habitat_client import HabitatClient

            client = HabitatClient(cache_dir=os.path.join(self.cache_dir, "habitat"))
            lat, lon = self.location
            habitat_data = client.get_habitat(lat, lon, radius_m=self.habitat_radius_m)

            self.habitat_type = habitat_data['primary']
            formatted = client.format_habitat_description(habitat_data)

            print(f"   Detected: {formatted}")

            if habitat_data['primary'] == 'unknown':
                print("   ⚠️  Could not detect habitat, please specify manually")
                self.habitat_type = 'unknown'

        except Exception as e:
            print(f"   ⚠️  Habitat detection failed: {e}")
            print("   ℹ️  Please specify habitat manually")
            self.habitat_type = 'unknown'

    def _auto_fetch_weather(self) -> None:
        """Automatically fetch weather data from GPS coordinates and date."""
        try:
            from .api.weather_client import WeatherClient

            client = WeatherClient(cache_dir=os.path.join(self.cache_dir, "weather"))
            lat, lon = self.location

            # Use date + noon if no specific time provided
            weather_data = client.get_weather(lat, lon, self.date, time="12:00")

            self.weather_conditions = {
                'rain': weather_data['rain'],
                'fog': weather_data['fog'],
                'temperature': weather_data['temperature'],
                'wind_speed': weather_data['wind_speed'],
                'cloud_cover': weather_data['cloud_cover']
            }

            print(f"   Fetched: {weather_data['temperature']:.1f}°C, "
                  f"rain {weather_data['rain']:.2f}, "
                  f"fog {weather_data['fog']:.2f}")

        except Exception as e:
            print(f"   ⚠️  Weather fetch failed: {e}")
            print("   ℹ️  Using default weather conditions")
            self.weather_conditions = {
                'rain': 0.0,
                'fog': 0.0,
                'temperature': 15.0,
                'wind_speed': 5.0,
                'cloud_cover': 0.5
            }


class ValidationResult(BaseModel):
    """Result of a validation check."""

    species: str
    timestamp: str
    confidence: float
    status: str = Field(..., description="ACCEPT, REJECT, or REVIEW")

    # Validation details
    geographic_valid: bool
    temporal_valid: bool
    habitat_valid: bool
    weather_score: Optional[float] = None

    # Reasoning
    rejection_reason: Optional[str] = None
    review_notes: List[str] = Field(default_factory=list)

    # Scores
    overall_score: float = Field(0.0, ge=0.0, le=1.0)

    # Metadata
    ebird_frequency: Optional[float] = None
    gbif_occurrences: Optional[int] = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return self.model_dump()


class SpeciesMetadata(BaseModel):
    """Species-specific metadata for validation."""

    common_name: str
    scientific_name: str

    # Temporal patterns
    diurnal: bool = True
    crepuscular: bool = False
    nocturnal: bool = False

    # Migration
    resident: bool = False
    summer_visitor: bool = False
    winter_visitor: bool = False
    passage_migrant: bool = False

    # Habitat preferences (0-1 scores)
    habitat_preferences: Dict[str, float] = Field(
        default_factory=dict,
        description="Habitat suitability scores: {wetland: 0.9, forest: 0.2, ...}"
    )

    # Vocal behavior
    call_intensity_db: Optional[float] = None
    typical_call_frequency_hz: Optional[Tuple[int, int]] = None

    # Conservation status
    iucn_status: Optional[str] = None


class WeatherConditions(BaseModel):
    """Weather conditions for validation."""

    rain_intensity: float = Field(0.0, ge=0.0, le=1.0, description="0=none, 1=heavy")
    fog_density: float = Field(0.0, ge=0.0, le=1.0, description="0=clear, 1=dense")
    temperature_c: Optional[float] = None
    wind_speed_ms: Optional[float] = None
    cloud_cover: float = Field(0.0, ge=0.0, le=1.0, description="0=clear, 1=overcast")

    def to_features(self) -> Dict[str, float]:
        """Convert to feature dictionary for ML model."""
        return {
            'rain': self.rain_intensity,
            'fog': self.fog_density,
            'temp': self.temperature_c or 10.0,  # Default 10°C
            'wind': self.wind_speed_ms or 0.0,
            'clouds': self.cloud_cover
        }
