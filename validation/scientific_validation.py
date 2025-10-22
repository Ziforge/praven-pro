#!/usr/bin/env python3
"""
Scientific Validation Framework for Praven Pro

Tests Praven Pro on independent datasets with ground truth to calculate:
- Precision (of rejections)
- Recall (of false positives caught)
- F1-Score
- Accuracy
- Confusion matrix

This is a BLIND TEST - we evaluate on data Praven has never seen.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score, confusion_matrix
import json

from praven.validator import BiologicalValidator
from praven.config import ValidationConfig


class ScientificValidation:
    """Scientific validation framework for Praven Pro."""

    def __init__(self, config: ValidationConfig):
        """
        Initialize validation framework.

        Args:
            config: Validation configuration for test dataset
        """
        self.config = config
        self.validator = BiologicalValidator(config)
        self.results = None

    def load_ground_truth(
        self,
        detections_path: str,
        ground_truth_path: str
    ) -> pd.DataFrame:
        """
        Load dataset with ground truth labels.

        Args:
            detections_path: Path to BirdNET detections CSV
            ground_truth_path: Path to expert-verified labels CSV

        Returns:
            DataFrame with detections and ground truth

        Expected ground_truth format:
            - detection_id: Unique ID matching detections
            - expert_label: "valid" or "invalid"
            - expert_reason: Optional reason for rejection
        """
        print("Loading ground truth dataset...")

        detections = pd.read_csv(detections_path)
        ground_truth = pd.read_csv(ground_truth_path)

        # Merge on detection ID
        if 'detection_id' not in detections.columns:
            # Create detection IDs from index
            detections['detection_id'] = detections.index

        df = detections.merge(
            ground_truth,
            on='detection_id',
            how='inner'
        )

        print(f"  Loaded {len(df):,} detections with ground truth")
        print(f"  Valid: {(df['expert_label'] == 'valid').sum():,}")
        print(f"  Invalid: {(df['expert_label'] == 'invalid').sum():,}")

        return df

    def run_validation(
        self,
        df: pd.DataFrame,
        sample_size: int = 1000
    ) -> pd.DataFrame:
        """
        Run Praven validation on ground truth dataset.

        Args:
            df: DataFrame with ground truth labels
            sample_size: Number of detections to test (random sample)

        Returns:
            DataFrame with Praven predictions and ground truth
        """
        # Random sample for testing
        if len(df) > sample_size:
            print(f"\nRandomly sampling {sample_size} detections for blind test...")
            df_test = df.sample(n=sample_size, random_state=42)
        else:
            df_test = df.copy()

        print(f"\nRunning Praven validation on {len(df_test):,} detections...")

        # Run Praven validation
        validated = self.validator.validate_dataframe(
            df_test,
            species_col='common_name',
            time_col='absolute_timestamp',
            confidence_col='confidence',
            scientific_col='scientific_name' if 'scientific_name' in df_test.columns else None
        )

        # Add ground truth labels
        validated['expert_label'] = df_test['expert_label'].values
        validated['expert_reason'] = df_test.get('expert_reason', '').values

        self.results = validated
        return validated

    def calculate_metrics(self) -> Dict[str, float]:
        """
        Calculate scientific validation metrics.

        Returns:
            Dictionary of metrics

        Metrics:
            - Precision: Of detections Praven REJECTS, what % are actually invalid?
            - Recall: Of actually invalid detections, what % does Praven catch?
            - F1-Score: Harmonic mean of precision and recall
            - Accuracy: Overall correctness
        """
        if self.results is None:
            raise ValueError("Run validation first!")

        df = self.results

        # Convert to binary labels
        # Ground truth: 1 = valid, 0 = invalid
        y_true = (df['expert_label'] == 'valid').astype(int)

        # Praven prediction: 1 = accepted (valid), 0 = rejected (invalid)
        # We consider both REJECT and REVIEW as "needs checking"
        y_pred = (df['status'] == 'ACCEPT').astype(int)

        # Calculate metrics
        metrics = {
            'accuracy': accuracy_score(y_true, y_pred),
            'precision': precision_score(y_true, y_pred, zero_division=0),
            'recall': recall_score(y_true, y_pred, zero_division=0),
            'f1_score': f1_score(y_true, y_pred, zero_division=0)
        }

        # Confusion matrix
        cm = confusion_matrix(y_true, y_pred)

        # Rejection metrics (more relevant for Praven)
        rejected = df[df['status'] == 'REJECT']
        if len(rejected) > 0:
            rejection_precision = (rejected['expert_label'] == 'invalid').sum() / len(rejected)
            metrics['rejection_precision'] = rejection_precision
        else:
            metrics['rejection_precision'] = 0.0

        # How many actual invalids did we catch?
        actual_invalids = df[df['expert_label'] == 'invalid']
        if len(actual_invalids) > 0:
            caught = (actual_invalids['status'] == 'REJECT').sum()
            metrics['rejection_recall'] = caught / len(actual_invalids)
        else:
            metrics['rejection_recall'] = 0.0

        metrics['confusion_matrix'] = cm.tolist()

        return metrics

    def analyze_errors(self) -> Dict:
        """
        Analyze validation errors in detail.

        Returns:
            Dictionary with error analysis
        """
        if self.results is None:
            raise ValueError("Run validation first!")

        df = self.results

        # False positives: Praven accepted, but expert said invalid
        false_positives = df[
            (df['status'] == 'ACCEPT') &
            (df['expert_label'] == 'invalid')
        ]

        # False negatives: Praven rejected, but expert said valid
        false_negatives = df[
            (df['status'] == 'REJECT') &
            (df['expert_label'] == 'valid')
        ]

        # True positives: Praven rejected correctly
        true_positives = df[
            (df['status'] == 'REJECT') &
            (df['expert_label'] == 'invalid')
        ]

        analysis = {
            'false_positives': {
                'count': len(false_positives),
                'species': false_positives['common_name'].value_counts().to_dict(),
                'examples': false_positives[['common_name', 'timestamp', 'confidence', 'expert_reason']].head(10).to_dict('records')
            },
            'false_negatives': {
                'count': len(false_negatives),
                'species': false_negatives['common_name'].value_counts().to_dict(),
                'examples': false_negatives[['common_name', 'timestamp', 'confidence', 'rejection_reason']].head(10).to_dict('records')
            },
            'true_positives': {
                'count': len(true_positives),
                'species': true_positives['common_name'].value_counts().to_dict()
            }
        }

        return analysis

    def generate_report(self, output_path: str = 'validation_report.txt') -> None:
        """Generate scientific validation report."""
        if self.results is None:
            raise ValueError("Run validation first!")

        metrics = self.calculate_metrics()
        errors = self.analyze_errors()

        with open(output_path, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("Praven Pro - Scientific Validation Report\n")
            f.write("=" * 80 + "\n\n")

            f.write("Test Configuration\n")
            f.write("-" * 80 + "\n")
            f.write(f"Location: {self.config.location}\n")
            f.write(f"Habitat: {self.config.habitat_type}\n")
            f.write(f"Test size: {len(self.results):,} detections\n")
            f.write(f"Species: {self.results['common_name'].nunique()}\n\n")

            f.write("Performance Metrics\n")
            f.write("-" * 80 + "\n")
            f.write(f"Overall Accuracy:        {metrics['accuracy']:.3f}\n")
            f.write(f"Precision:               {metrics['precision']:.3f}\n")
            f.write(f"Recall:                  {metrics['recall']:.3f}\n")
            f.write(f"F1-Score:                {metrics['f1_score']:.3f}\n\n")

            f.write("Rejection Performance (Key Metric)\n")
            f.write("-" * 80 + "\n")
            f.write(f"Rejection Precision:     {metrics['rejection_precision']:.3f}\n")
            f.write(f"  (Of rejections, % actually invalid)\n")
            f.write(f"Rejection Recall:        {metrics['rejection_recall']:.3f}\n")
            f.write(f"  (Of invalid detections, % caught)\n\n")

            f.write("Confusion Matrix\n")
            f.write("-" * 80 + "\n")
            cm = np.array(metrics['confusion_matrix'])
            f.write("                    Predicted\n")
            f.write("                    Invalid  Valid\n")
            f.write(f"Actual Invalid      {cm[0][0]:6d}  {cm[0][1]:6d}\n")
            f.write(f"       Valid        {cm[1][0]:6d}  {cm[1][1]:6d}\n\n")

            f.write("Error Analysis\n")
            f.write("-" * 80 + "\n")
            f.write(f"False Positives (missed invalids): {errors['false_positives']['count']}\n")
            f.write(f"False Negatives (wrong rejections): {errors['false_negatives']['count']}\n")
            f.write(f"True Positives (correct rejections): {errors['true_positives']['count']}\n\n")

            if errors['false_negatives']['count'] > 0:
                f.write("Top False Negatives (Praven rejected but expert said valid):\n")
                for species, count in list(errors['false_negatives']['species'].items())[:10]:
                    f.write(f"  {species}: {count}\n")
                f.write("\n")

            if errors['false_positives']['count'] > 0:
                f.write("Top False Positives (Praven accepted but expert said invalid):\n")
                for species, count in list(errors['false_positives']['species'].items())[:10]:
                    f.write(f"  {species}: {count}\n")

        print(f"\nValidation report saved: {output_path}")


def create_sample_ground_truth_template():
    """Create template for ground truth labeling."""
    template = pd.DataFrame({
        'detection_id': [0, 1, 2, 3, 4],
        'expert_label': ['valid', 'invalid', 'valid', 'invalid', 'valid'],
        'expert_reason': [
            '',
            'Nocturnal woodpecker detection',
            '',
            'Oceanic species inland',
            ''
        ]
    })

    template.to_csv('ground_truth_template.csv', index=False)
    print("Created ground_truth_template.csv")
    print("\nFormat:")
    print("  detection_id: Index matching BirdNET detections")
    print("  expert_label: 'valid' or 'invalid'")
    print("  expert_reason: Optional rejection reason")


if __name__ == "__main__":
    print("=" * 80)
    print("Praven Pro - Scientific Validation Framework")
    print("=" * 80)
    print("\nThis framework tests Praven on independent data with ground truth.")
    print("\nTo use:")
    print("1. Prepare ground truth labels (expert-verified detections)")
    print("2. Run validation on 1000 blind test samples")
    print("3. Calculate precision, recall, F1-score")
    print("4. Analyze errors\n")

    create_sample_ground_truth_template()
