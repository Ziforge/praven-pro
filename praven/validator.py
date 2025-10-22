"""
Main biological validation engine for BirdNET detections.
"""

from typing import Dict, Optional, List
from datetime import datetime
import pandas as pd

from .config import ValidationConfig, ValidationResult, WeatherConditions
from .api import eBirdClient, GBIFClient
from .api.ebird_preloader import eBirdPreloader
from .rules import GeographicValidator, TemporalValidator, HabitatValidator
from .models import WeatherActivityModel


class BiologicalValidator:
    """Main validator integrating all validation rules."""

    def __init__(
        self,
        config: ValidationConfig,
        custom_weather_model: Optional[str] = None,
        enable_ebird_preload: bool = True
    ):
        """
        Initialize biological validator.

        Automatically preloads eBird data for study region on startup.
        Cache is auto-updated if older than 7 days.

        Args:
            config: Validation configuration
            custom_weather_model: Path to custom weather model (optional)
            enable_ebird_preload: Enable automatic eBird data preloading (default: True)
        """
        self.config = config

        # Initialize eBird preloader (auto-checks/updates cache)
        self.ebird_preloader = None
        if enable_ebird_preload and config.location:
            print("\n" + "=" * 80)
            print("eBird Data Preloader")
            print("=" * 80)

            self.ebird_preloader = eBirdPreloader(
                api_key=config.ebird_api_key,
                cache_dir=f"{config.cache_dir}/ebird_regional"
            )

            # Auto-preload for study location (checks cache every run)
            try:
                self.ebird_preloader.preload_region(
                    lat=config.location[0],
                    lon=config.location[1],
                    radius_km=50,  # 50km radius
                    days_back=30,  # Last 30 days
                    auto_update=True  # Auto-refresh stale cache
                )
            except Exception as e:
                print(f"  WARNING: eBird preload failed: {e}")
                print(f"  Continuing without eBird data...")
                self.ebird_preloader = None

            print("=" * 80 + "\n")

        # Initialize API clients
        self.ebird = None
        if config.ebird_api_key:
            self.ebird = eBirdClient(
                api_key=config.ebird_api_key,
                cache_dir=config.cache_dir,
                cache_ttl_hours=config.cache_ttl_hours
            )

        self.gbif = GBIFClient(
            cache_dir=config.cache_dir,
            cache_ttl_hours=config.cache_ttl_hours
        )

        # Initialize validators
        self.geographic_validator = GeographicValidator(
            ebird_client=self.ebird,
            gbif_client=self.gbif,
            config=config
        )

        self.temporal_validator = TemporalValidator()
        self.habitat_validator = HabitatValidator()

        # Initialize weather model
        self.weather_model = WeatherActivityModel(custom_weather_model)

    @classmethod
    def from_config(cls, config_dict: Dict) -> 'BiologicalValidator':
        """
        Create validator from configuration dictionary.

        Args:
            config_dict: Configuration dictionary

        Returns:
            BiologicalValidator instance
        """
        config = ValidationConfig(**config_dict)
        return cls(config)

    def validate_detection(
        self,
        species: str,
        timestamp: str,
        confidence: float,
        scientific_name: Optional[str] = None
    ) -> ValidationResult:
        """
        Validate a single BirdNET detection.

        Args:
            species: Common name of species
            timestamp: Detection timestamp (YYYY-MM-DD HH:MM:SS)
            confidence: BirdNET confidence score (0-1)
            scientific_name: Scientific name (optional, for GBIF)

        Returns:
            ValidationResult with detailed validation info
        """
        lat, lon = self.config.location
        date = self.config.date

        # Extract time from timestamp if it includes date
        if ' ' in timestamp:
            date_part, time_part = timestamp.split(' ', 1)
            date = date_part
        else:
            time_part = timestamp

        # Initialize result
        result = ValidationResult(
            species=species,
            timestamp=timestamp,
            confidence=confidence,
            status="REVIEW",  # Default to review
            geographic_valid=True,
            temporal_valid=True,
            habitat_valid=True
        )

        rejection_reasons = []
        review_notes = []

        # 1. Habitat Validation
        habitat_valid, habitat_reason, habitat_score = self.habitat_validator.validate(
            species_name=species,
            habitat_type=self.config.habitat_type,
            min_threshold=0.3
        )

        result.habitat_valid = habitat_valid

        if not habitat_valid:
            rejection_reasons.append(habitat_reason)

        # Check native region
        native_valid, native_reason = self.habitat_validator.check_native_region(
            species_name=species,
            region="Europe"
        )

        if not native_valid:
            result.habitat_valid = False
            rejection_reasons.append(native_reason)

        # 2. Temporal Validation
        temporal_valid, temporal_warnings = self.temporal_validator.is_species_active(
            species_name=species,
            timestamp=time_part,
            date=date
        )

        result.temporal_valid = temporal_valid

        if not temporal_valid:
            rejection_reasons.extend(temporal_warnings)

        # 3. Geographic Validation (if API available)
        geo_metadata = {}
        if self.ebird or self.gbif:
            geo_valid, geo_warning, geo_metadata = self.geographic_validator.validate(
                species_name=species,
                scientific_name=scientific_name,
                lat=lat,
                lon=lon,
                date=date,
                radius_km=self.config.geographic_radius_km,
                require_both=False  # Accept if either API confirms
            )

            result.geographic_valid = geo_valid

            if geo_warning:
                review_notes.append(geo_warning)

            # Add eBird/GBIF metadata
            result.ebird_frequency = geo_metadata.get('ebird_frequency')
            result.gbif_occurrences = geo_metadata.get('gbif_occurrence_count')

        # 4. Weather Activity Score
        if self.config.weather_conditions:
            weather = WeatherConditions(**self.config.weather_conditions)
            weather_score = self.weather_model.predict_activity_score(
                species_name=species,
                weather_conditions=weather.to_features()
            )
            result.weather_score = weather_score

            if weather_score < 0.3:
                review_notes.append(
                    f"Low weather activity score: {weather_score:.2f} "
                    f"(species less likely active in these conditions)"
                )

        # 5. Calculate Overall Score
        scores = []

        # Habitat contribution (0.3 weight)
        scores.append(habitat_score * 0.3)

        # Temporal contribution (0.2 weight)
        scores.append(1.0 * 0.2 if result.temporal_valid else 0.0)

        # Geographic contribution (0.3 weight)
        if geo_metadata:
            geo_conf = self.geographic_validator.get_occurrence_confidence(geo_metadata)
            scores.append(geo_conf * 0.3)
        else:
            scores.append(0.5 * 0.3)  # Neutral if no geo data

        # BirdNET confidence contribution (0.2 weight)
        scores.append(confidence * 0.2)

        result.overall_score = sum(scores)

        # 6. Determine Final Status
        if rejection_reasons:
            # Hard rejections (habitat mismatch, temporal impossibility)
            result.status = "REJECT"
            result.rejection_reason = "; ".join(rejection_reasons)

        elif result.overall_score >= 0.7 and confidence >= 0.7:
            # High confidence - auto-accept
            result.status = "ACCEPT"

        elif result.overall_score < 0.4 or confidence < self.config.min_confidence:
            # Low confidence - needs review
            result.status = "REVIEW"
            review_notes.append(
                f"Low overall score: {result.overall_score:.2f} "
                f"or low BirdNET confidence: {confidence:.2f}"
            )

        else:
            # Medium confidence - needs review
            result.status = "REVIEW"

        result.review_notes = review_notes

        return result

    def validate_dataframe(
        self,
        df: pd.DataFrame,
        species_col: str = "Common name",
        time_col: str = "Begin Time (s)",
        confidence_col: str = "Confidence",
        scientific_col: Optional[str] = "Scientific name"
    ) -> pd.DataFrame:
        """
        Validate entire BirdNET results dataframe.

        Args:
            df: BirdNET results dataframe
            species_col: Column name for species
            time_col: Column name for timestamp
            confidence_col: Column name for confidence score
            scientific_col: Column name for scientific name (optional)

        Returns:
            DataFrame with validation results added
        """
        results = []

        print(f"Validating {len(df)} detections...")

        for idx, row in df.iterrows():
            species = row[species_col]
            timestamp = str(row[time_col])
            confidence = float(row[confidence_col])

            scientific_name = None
            if scientific_col and scientific_col in df.columns:
                scientific_name = row[scientific_col]

            result = self.validate_detection(
                species=species,
                timestamp=timestamp,
                confidence=confidence,
                scientific_name=scientific_name
            )

            results.append(result.to_dict())

            # Progress indication
            if (idx + 1) % 100 == 0:
                print(f"  Processed {idx + 1}/{len(df)} detections...")

        # Convert results to DataFrame
        results_df = pd.DataFrame(results)

        # Merge with original data
        output_df = pd.concat([df.reset_index(drop=True), results_df], axis=1)

        # Print summary
        status_counts = results_df['status'].value_counts()
        print("\nValidation Summary:")
        print(f"  ACCEPT: {status_counts.get('ACCEPT', 0)}")
        print(f"  REJECT: {status_counts.get('REJECT', 0)}")
        print(f"  REVIEW: {status_counts.get('REVIEW', 0)}")

        return output_df

    def get_validation_stats(self, results_df: pd.DataFrame) -> Dict:
        """
        Get validation statistics from results.

        Args:
            results_df: DataFrame with validation results

        Returns:
            Statistics dictionary
        """
        stats = {
            'total_detections': len(results_df),
            'accepted': len(results_df[results_df['status'] == 'ACCEPT']),
            'rejected': len(results_df[results_df['status'] == 'REJECT']),
            'needs_review': len(results_df[results_df['status'] == 'REVIEW']),
            'auto_pass_rate': 0.0,
            'auto_reject_rate': 0.0,
            'review_rate': 0.0
        }

        if stats['total_detections'] > 0:
            stats['auto_pass_rate'] = stats['accepted'] / stats['total_detections']
            stats['auto_reject_rate'] = stats['rejected'] / stats['total_detections']
            stats['review_rate'] = stats['needs_review'] / stats['total_detections']

        # Top rejection reasons
        rejected = results_df[results_df['status'] == 'REJECT']
        if len(rejected) > 0:
            stats['rejection_reasons'] = rejected['rejection_reason'].value_counts().to_dict()

        return stats
