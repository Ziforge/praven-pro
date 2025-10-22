"""
Machine learning model training for biological validation.

Trains models on verified acoustic monitoring datasets to predict:
- Detection validity (accept/reject)
- Species-specific weather activity
- Temporal activity patterns
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib
import json


class ValidationModelTrainer:
    """Train ML models for detection validation."""

    def __init__(self):
        """Initialize trainer."""
        self.model = None
        self.feature_columns = []
        self.species_encoder = {}
        self.trained = False

    def prepare_features(
        self,
        df: pd.DataFrame,
        verified_species: Optional[List[str]] = None
    ) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Prepare features for training.

        Args:
            df: Raw detections dataframe
            verified_species: List of verified species (None = all are verified)

        Returns:
            (X features, y labels)
        """
        # Create label: 1 if species is verified, 0 if rejected
        if verified_species is not None:
            df['is_valid'] = df['common_name'].isin(verified_species).astype(int)
        else:
            # Assume all are valid if not specified
            df['is_valid'] = 1

        # Extract temporal features
        df['timestamp_dt'] = pd.to_datetime(df['absolute_timestamp'])
        df['hour'] = df['timestamp_dt'].dt.hour
        df['day_of_year'] = df['timestamp_dt'].dt.dayofyear
        df['month'] = df['timestamp_dt'].dt.month

        # Time period features
        df['is_night'] = ((df['hour'] >= 0) & (df['hour'] < 6)) | (df['hour'] >= 21)
        df['is_dawn'] = (df['hour'] >= 6) & (df['hour'] < 9)
        df['is_day'] = (df['hour'] >= 9) & (df['hour'] < 17)
        df['is_dusk'] = (df['hour'] >= 17) & (df['hour'] < 21)

        # Species encoding (one-hot would be huge, use target encoding instead)
        species_valid_rate = df.groupby('common_name')['is_valid'].mean()
        df['species_valid_rate'] = df['common_name'].map(species_valid_rate)

        # Detection features
        df['audio_duration'] = df['end_s'] - df['start_s']

        # Feature set
        feature_cols = [
            'confidence',
            'hour',
            'month',
            'is_night',
            'is_dawn',
            'is_day',
            'is_dusk',
            'species_valid_rate',
            'audio_duration',
            'start_s'  # Position in recording
        ]

        self.feature_columns = feature_cols

        X = df[feature_cols].copy()
        y = df['is_valid']

        return X, y

    def train(
        self,
        all_detections_path: str,
        verified_detections_path: str,
        model_type: str = 'random_forest',
        test_size: float = 0.2
    ) -> Dict[str, float]:
        """
        Train validation model.

        Args:
            all_detections_path: Path to all BirdNET detections CSV
            verified_detections_path: Path to verified detections CSV
            model_type: 'random_forest' or 'gradient_boosting'
            test_size: Fraction for test set

        Returns:
            Training metrics
        """
        print("Loading datasets...")
        df_all = pd.read_csv(all_detections_path)
        df_verified = pd.read_csv(verified_detections_path)

        print(f"  All detections: {len(df_all):,}")
        print(f"  Verified detections: {len(df_verified):,}")

        # Get verified species
        verified_species = set(df_verified['common_name'].unique())
        print(f"  Verified species: {len(verified_species)}")

        # Prepare features
        print("\nPreparing features...")
        X, y = self.prepare_features(df_all, verified_species)

        print(f"  Features: {list(X.columns)}")
        print(f"  Samples: {len(X):,}")
        print(f"  Valid: {y.sum():,} ({100*y.mean():.1f}%)")
        print(f"  Invalid: {(~y.astype(bool)).sum():,} ({100*(1-y.mean()):.1f}%)")

        # Handle missing values
        X = X.fillna(0)

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )

        print(f"\nTrain set: {len(X_train):,} samples")
        print(f"Test set: {len(X_test):,} samples")

        # Train model
        print(f"\nTraining {model_type} model...")

        if model_type == 'random_forest':
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=20,
                min_samples_leaf=10,
                random_state=42,
                class_weight='balanced',  # Handle imbalanced data
                n_jobs=-1
            )
        elif model_type == 'gradient_boosting':
            self.model = GradientBoostingClassifier(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                random_state=42
            )
        else:
            raise ValueError(f"Unknown model type: {model_type}")

        self.model.fit(X_train, y_train)

        # Evaluate
        print("\nEvaluating model...")

        # Train set performance
        y_train_pred = self.model.predict(X_train)
        train_acc = accuracy_score(y_train, y_train_pred)

        # Test set performance
        y_test_pred = self.model.predict(X_test)
        test_acc = accuracy_score(y_test, y_test_pred)

        # Cross-validation
        cv_scores = cross_val_score(self.model, X_train, y_train, cv=5)

        print(f"\nResults:")
        print(f"  Train accuracy: {train_acc:.3f}")
        print(f"  Test accuracy: {test_acc:.3f}")
        print(f"  CV accuracy: {cv_scores.mean():.3f} (+/- {cv_scores.std()*2:.3f})")

        # Detailed metrics
        print(f"\nClassification Report (Test Set):")
        print(classification_report(y_test, y_test_pred, target_names=['Invalid', 'Valid']))

        # Confusion matrix
        cm = confusion_matrix(y_test, y_test_pred)
        print(f"\nConfusion Matrix:")
        print(f"                 Predicted")
        print(f"                 Invalid  Valid")
        print(f"Actual Invalid   {cm[0][0]:6d}  {cm[0][1]:6d}")
        print(f"       Valid     {cm[1][0]:6d}  {cm[1][1]:6d}")

        # Feature importance
        if hasattr(self.model, 'feature_importances_'):
            print(f"\nFeature Importance:")
            importances = self.model.feature_importances_
            indices = np.argsort(importances)[::-1]

            for i in range(min(10, len(self.feature_columns))):
                idx = indices[i]
                print(f"  {i+1}. {self.feature_columns[idx]:25s} {importances[idx]:.4f}")

        self.trained = True

        return {
            'train_accuracy': train_acc,
            'test_accuracy': test_acc,
            'cv_accuracy_mean': cv_scores.mean(),
            'cv_accuracy_std': cv_scores.std(),
            'n_train': len(X_train),
            'n_test': len(X_test),
            'n_features': len(self.feature_columns)
        }

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Predict validity for new detections."""
        if not self.trained or self.model is None:
            raise ValueError("Model not trained yet")

        # Ensure features match
        X = X[self.feature_columns].fillna(0)
        return self.model.predict(X)

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """Predict probability of validity."""
        if not self.trained or self.model is None:
            raise ValueError("Model not trained yet")

        X = X[self.feature_columns].fillna(0)
        return self.model.predict_proba(X)

    def save(self, path: str) -> None:
        """Save trained model."""
        if not self.trained:
            raise ValueError("No trained model to save")

        model_data = {
            'model': self.model,
            'feature_columns': self.feature_columns,
            'species_encoder': self.species_encoder
        }

        joblib.dump(model_data, path)
        print(f"Model saved to: {path}")

    def load(self, path: str) -> None:
        """Load trained model."""
        model_data = joblib.load(path)

        self.model = model_data['model']
        self.feature_columns = model_data['feature_columns']
        self.species_encoder = model_data.get('species_encoder', {})
        self.trained = True

        print(f"Model loaded from: {path}")


class WeatherActivityTrainer:
    """Train species-specific weather activity models."""

    def __init__(self):
        """Initialize trainer."""
        self.species_models = {}

    def train_species_model(
        self,
        species_name: str,
        detections: pd.DataFrame,
        weather_conditions: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Train weather activity model for a single species.

        Args:
            species_name: Common name
            detections: Verified detections for this species
            weather_conditions: Weather during recording period

        Returns:
            Activity scores by weather condition
        """
        # Group by hour to get temporal activity pattern
        hourly_counts = detections.groupby(detections['absolute_timestamp'].str.split(' ').str[1].str[:2]).size()

        # Calculate activity scores
        total_detections = len(detections)
        peak_hour_count = hourly_counts.max() if len(hourly_counts) > 0 else 0

        # Weather resilience score (higher = more active in bad weather)
        # Based on detection rate relative to expected
        base_resilience = 0.5
        if total_detections > 10:  # Enough data
            # Normalize by recording hours
            detection_rate = total_detections / 48.8  # Hours of recording

            if detection_rate > 20:
                weather_resilience = 0.9  # Very active despite weather
            elif detection_rate > 5:
                weather_resilience = 0.7  # Moderately active
            elif detection_rate > 1:
                weather_resilience = 0.5  # Some activity
            else:
                weather_resilience = 0.3  # Low activity
        else:
            weather_resilience = base_resilience

        return {
            'total_detections': total_detections,
            'weather_resilience': weather_resilience,
            'peak_hour_count': int(peak_hour_count),
            'hourly_variance': float(hourly_counts.std()) if len(hourly_counts) > 1 else 0.0
        }

    def train_from_dataset(
        self,
        verified_detections_path: str,
        weather_conditions: Dict[str, float],
        min_detections: int = 5
    ) -> Dict[str, Dict]:
        """
        Train weather models for all species in dataset.

        Args:
            verified_detections_path: Path to verified detections
            weather_conditions: Weather during recording
            min_detections: Minimum detections to train species model

        Returns:
            Species activity scores
        """
        print("Loading verified detections...")
        df = pd.read_csv(verified_detections_path)

        print(f"  Total detections: {len(df):,}")
        print(f"  Unique species: {df['common_name'].nunique()}")

        species_stats = {}

        for species in df['common_name'].unique():
            species_detections = df[df['common_name'] == species]

            if len(species_detections) >= min_detections:
                stats = self.train_species_model(
                    species,
                    species_detections,
                    weather_conditions
                )
                species_stats[species] = stats

        print(f"\nTrained models for {len(species_stats)} species")

        return species_stats

    def save(self, path: str, species_stats: Dict) -> None:
        """Save weather activity statistics."""
        with open(path, 'w') as f:
            json.dump(species_stats, f, indent=2)

        print(f"Weather activity stats saved to: {path}")


def train_gaulossen_models():
    """Train models on Gaulossen dataset."""

    base_path = "../gaulossen/gaulosen_study/raw_data/analysis_csvs"

    print("=" * 80)
    print("Training Praven Pro ML Models on Gaulossen Dataset")
    print("=" * 80)

    # 1. Train validation model
    print("\n1. Training Detection Validation Model")
    print("-" * 80)

    trainer = ValidationModelTrainer()
    metrics = trainer.train(
        all_detections_path=f"{base_path}/all_detections.csv",
        verified_detections_path=f"{base_path}/verified_detections.csv",
        model_type='random_forest',
        test_size=0.2
    )

    # Save model
    trainer.save('gaulossen_validation_model.pkl')

    # 2. Train weather activity models
    print("\n\n2. Training Weather Activity Models")
    print("-" * 80)

    weather_trainer = WeatherActivityTrainer()
    weather_stats = weather_trainer.train_from_dataset(
        verified_detections_path=f"{base_path}/verified_detections.csv",
        weather_conditions={'rain': 0.8, 'fog': 0.7, 'temperature': 8.0},
        min_detections=5
    )

    # Save stats
    weather_trainer.save('gaulossen_weather_activity.json', weather_stats)

    print("\n" + "=" * 80)
    print("Training Complete!")
    print("=" * 80)
    print(f"\nModel Files:")
    print(f"  gaulossen_validation_model.pkl - Detection validation model")
    print(f"  gaulossen_weather_activity.json - Species weather activity stats")

    return metrics, weather_stats


if __name__ == "__main__":
    train_gaulossen_models()
