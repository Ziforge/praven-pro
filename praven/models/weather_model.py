"""
Weather-activity correlation model.

Predicts species detection likelihood based on weather conditions.
"""

import numpy as np
from typing import Dict, Optional
from pathlib import Path


class WeatherActivityModel:
    """Simple rule-based model for weather-activity correlation."""

    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize weather activity model.

        Args:
            model_path: Path to trained model file (optional)
        """
        self.model = None
        self.is_trained = False

        if model_path and Path(model_path).exists():
            self.load(model_path)

    def predict_activity_score(
        self,
        species_name: str,
        weather_conditions: Dict[str, float]
    ) -> float:
        """
        Predict species activity score given weather conditions.

        Args:
            species_name: Common name of species
            weather_conditions: Dict with keys: rain, fog, temp, wind, clouds

        Returns:
            Activity score (0-1, higher = more likely to be active/detectable)
        """
        if self.is_trained and self.model is not None:
            # Use trained model
            return self._predict_with_model(species_name, weather_conditions)
        else:
            # Use rule-based heuristics
            return self._predict_heuristic(species_name, weather_conditions)

    def _predict_heuristic(
        self,
        species_name: str,
        weather: Dict[str, float]
    ) -> float:
        """
        Heuristic-based prediction (used when no trained model available).

        Args:
            species_name: Species name
            weather: Weather conditions

        Returns:
            Activity score (0-1)
        """
        score = 1.0  # Start with baseline

        rain = weather.get('rain', 0.0)
        fog = weather.get('fog', 0.0)
        temp = weather.get('temp', 10.0)
        wind = weather.get('wind', 0.0)

        # General weather penalties
        # Rain reduces vocal activity for most birds
        if rain > 0.0:
            rain_penalty = 0.1 + (rain * 0.3)  # 0.1 to 0.4 penalty
            score -= rain_penalty

        # Fog has less impact
        if fog > 0.0:
            fog_penalty = fog * 0.1  # Up to 0.1 penalty
            score -= fog_penalty

        # Temperature effects
        if temp < 0:
            score -= 0.2  # Cold penalty
        elif temp > 25:
            score -= 0.1  # Heat penalty

        # Wind effects
        if wind > 10:
            score -= 0.2  # High wind penalty

        # Species-specific adjustments
        waterfowl = [
            'Graylag Goose', 'Pink-footed Goose', 'Mallard',
            'Greater White-fronted Goose', 'Barnacle Goose'
        ]

        if species_name in waterfowl:
            # Waterfowl are more resilient to rain
            score += 0.2

        # Ensure score is in [0, 1]
        return max(min(score, 1.0), 0.0)

    def _predict_with_model(
        self,
        species_name: str,
        weather: Dict[str, float]
    ) -> float:
        """
        Predict using trained ML model.

        Args:
            species_name: Species name
            weather: Weather conditions

        Returns:
            Activity score (0-1)
        """
        # Placeholder for trained model prediction
        # Would use scikit-learn model here
        return self._predict_heuristic(species_name, weather)

    def train(
        self,
        training_data: Dict,
        save_path: Optional[str] = None
    ) -> Dict[str, float]:
        """
        Train model on verified detection data.

        Args:
            training_data: Dictionary with species, weather, and detection outcomes
            save_path: Optional path to save trained model

        Returns:
            Training metrics
        """
        # Placeholder for model training
        # Would implement scikit-learn Random Forest here

        print("Weather model training not yet implemented")
        print("Using rule-based heuristics instead")

        return {
            'accuracy': 0.0,
            'precision': 0.0,
            'recall': 0.0
        }

    def save(self, path: str) -> None:
        """Save trained model to file."""
        import joblib

        if self.model is not None:
            joblib.dump(self.model, path)
            print(f"Model saved to {path}")

    def load(self, path: str) -> None:
        """Load trained model from file."""
        import joblib

        if Path(path).exists():
            self.model = joblib.load(path)
            self.is_trained = True
            print(f"Model loaded from {path}")
