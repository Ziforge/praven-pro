"""
Smart Review Selection for Praven Pro

Automatically selects the best representative detections for manual review,
drastically reducing review workload while maintaining quality.

Instead of reviewing thousands of detections, review only the top 1-3 per species.
"""

import pandas as pd
from typing import Dict, Optional, List
from pathlib import Path


class SmartReviewSelector:
    """Selects best representative detections for efficient manual review."""

    def __init__(self, detections_per_species: int = 3):
        """
        Initialize review selector.

        Args:
            detections_per_species: How many top detections to select per species
        """
        self.detections_per_species = detections_per_species

    def select_best_for_review(
        self,
        validated_df: pd.DataFrame,
        confidence_col: str = 'confidence',
        species_col: str = 'common_name',
        status_col: str = 'status'
    ) -> Dict[str, pd.DataFrame]:
        """
        Select best representative detections for review.

        Strategy:
        1. ACCEPT: Already validated, no review needed
        2. REJECT: Already validated, no review needed
        3. REVIEW: Select top N per species for manual check

        Args:
            validated_df: DataFrame with validation results
            confidence_col: Column with confidence scores
            species_col: Column with species names
            status_col: Column with validation status

        Returns:
            Dictionary with:
                - 'review_required': Small set for manual review
                - 'auto_validated': Already decided (accept/reject)
                - 'review_summary': Summary statistics
        """
        # Separate into categories
        auto_accept = validated_df[validated_df[status_col] == 'ACCEPT'].copy()
        auto_reject = validated_df[validated_df[status_col] == 'REJECT'].copy()
        needs_review = validated_df[validated_df[status_col] == 'REVIEW'].copy()

        print(f"\nSmart Review Selection")
        print(f"=" * 80)
        print(f"Total detections: {len(validated_df):,}")
        print(f"  Auto-accepted: {len(auto_accept):,} (no review needed)")
        print(f"  Auto-rejected: {len(auto_reject):,} (no review needed)")
        print(f"  Needs review: {len(needs_review):,}")

        if len(needs_review) == 0:
            print(f"\n✅ No review needed - all detections auto-validated!")
            return {
                'review_required': pd.DataFrame(),
                'auto_validated': pd.concat([auto_accept, auto_reject]),
                'review_summary': {
                    'total': len(validated_df),
                    'auto_validated': len(auto_accept) + len(auto_reject),
                    'review_required': 0,
                    'species_to_review': 0
                }
            }

        # Select best representatives for review
        review_candidates = self._select_best_representatives(
            needs_review,
            confidence_col,
            species_col
        )

        print(f"\n📋 Review Workload Reduction:")
        print(f"  Before: {len(needs_review):,} detections to review")
        print(f"  After:  {len(review_candidates):,} detections to review")
        print(f"  Reduction: {100 * (1 - len(review_candidates)/len(needs_review)):.1f}%")

        species_count = needs_review[species_col].nunique()
        print(f"\n  Species with REVIEW status: {species_count}")
        print(f"  Top {self.detections_per_species} per species selected")

        # Create summary
        summary = {
            'total': len(validated_df),
            'auto_validated': len(auto_accept) + len(auto_reject),
            'review_required': len(review_candidates),
            'species_to_review': species_count,
            'reduction_percent': 100 * (1 - len(review_candidates)/len(needs_review)) if len(needs_review) > 0 else 0
        }

        return {
            'review_required': review_candidates,
            'auto_validated': pd.concat([auto_accept, auto_reject]),
            'review_summary': summary
        }

    def _select_best_representatives(
        self,
        review_df: pd.DataFrame,
        confidence_col: str,
        species_col: str
    ) -> pd.DataFrame:
        """
        Select best representative detections for each species.

        Selection criteria (in order):
        1. Highest confidence score
        2. Fewest validation warnings
        3. Best temporal/habitat match
        4. Earliest detection (likely most representative)

        Args:
            review_df: Detections needing review
            confidence_col: Confidence score column
            species_col: Species name column

        Returns:
            DataFrame with top representatives
        """
        selected = []

        # Group by species
        for species, group in review_df.groupby(species_col):
            # Calculate quality score
            group = group.copy()

            # Base score: confidence
            # Handle potential duplicate confidence columns
            if isinstance(group[confidence_col], pd.DataFrame):
                conf_values = group[confidence_col].iloc[:, 0]
            else:
                conf_values = group[confidence_col]

            group['quality_score'] = conf_values.astype(float)

            # Bonus: fewer rejection reasons means cleaner detection
            if 'rejection_reason' in group.columns:
                # Detections with no specific warnings get bonus
                no_warnings = group['rejection_reason'].isna() | (group['rejection_reason'] == '')
                group.loc[no_warnings, 'quality_score'] = group.loc[no_warnings, 'quality_score'] + 0.1

            # Bonus: valid temporal window
            if 'temporal_valid' in group.columns:
                group.loc[group['temporal_valid'] == True, 'quality_score'] = group.loc[group['temporal_valid'] == True, 'quality_score'] + 0.05

            # Bonus: valid habitat
            if 'habitat_valid' in group.columns:
                group.loc[group['habitat_valid'] == True, 'quality_score'] = group.loc[group['habitat_valid'] == True, 'quality_score'] + 0.05

            # Sort by quality score
            group_sorted = group.sort_values('quality_score', ascending=False)

            # Select top N
            top_detections = group_sorted.head(self.detections_per_species)

            selected.append(top_detections)

        return pd.concat(selected) if selected else pd.DataFrame()

    def export_review_set(
        self,
        review_df: pd.DataFrame,
        output_dir: str,
        base_name: str = "review_priority"
    ) -> Dict[str, str]:
        """
        Export prioritized review set.

        Args:
            review_df: Review candidates DataFrame
            output_dir: Output directory
            base_name: Base filename

        Returns:
            Dictionary of exported file paths
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        exports = {}

        # Export priority review CSV
        review_path = output_dir / f"{base_name}.csv"
        review_df.to_csv(review_path, index=False)
        exports['review_csv'] = str(review_path)

        # Export by species (for organized review)
        species_dir = output_dir / "review_by_species"
        species_dir.mkdir(exist_ok=True)

        for species, group in review_df.groupby('common_name'):
            # Clean filename
            safe_name = species.replace(' ', '_').replace('/', '_')
            species_path = species_dir / f"{safe_name}.csv"
            group.to_csv(species_path, index=False)

        exports['species_dir'] = str(species_dir)

        # Export summary
        summary_path = output_dir / f"{base_name}_summary.txt"
        with open(summary_path, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("Praven Pro - Prioritized Review Summary\n")
            f.write("=" * 80 + "\n\n")

            f.write(f"Total detections to review: {len(review_df)}\n\n")

            f.write("Species requiring review:\n")
            f.write("-" * 80 + "\n")

            species_counts = review_df['common_name'].value_counts()
            for species, count in species_counts.items():
                f.write(f"  {species:40s} {count:3d} detections\n")

            f.write("\n" + "=" * 80 + "\n")
            f.write("Review Instructions:\n")
            f.write("=" * 80 + "\n\n")

            f.write("1. Review the priority detections in review_priority.csv\n")
            f.write("2. For each species, check the top representatives\n")
            f.write("3. If top detections are VALID → Accept whole species\n")
            f.write("4. If top detections are INVALID → Reject whole species\n")
            f.write("5. If uncertain → Review more detections for that species\n\n")

            f.write("Individual species files available in: review_by_species/\n")

        exports['summary'] = str(summary_path)

        print(f"\n✅ Exported review files:")
        print(f"   Priority review: {review_path}")
        print(f"   By species: {species_dir}")
        print(f"   Summary: {summary_path}")

        return exports


def apply_species_decisions(
    validated_df: pd.DataFrame,
    review_decisions: Dict[str, str],
    species_col: str = 'common_name'
) -> pd.DataFrame:
    """
    Apply species-level decisions to all detections.

    After reviewing top representatives, apply decision to all detections
    of that species.

    Args:
        validated_df: Original validated DataFrame
        review_decisions: Dict mapping species -> decision ('accept' or 'reject')
        species_col: Species column name

    Returns:
        Updated DataFrame with review decisions applied

    Example:
        decisions = {
            'Graylag Goose': 'accept',  # Reviewed top 3, all valid
            'Lesser Spotted Woodpecker': 'reject',  # Reviewed top 3, all invalid
        }
        final_df = apply_species_decisions(df, decisions)
    """
    df = validated_df.copy()

    applied_count = 0
    for species, decision in review_decisions.items():
        mask = (df[species_col] == species) & (df['status'] == 'REVIEW')

        if decision.lower() == 'accept':
            df.loc[mask, 'status'] = 'ACCEPT'
            df.loc[mask, 'review_decision'] = 'Accepted after manual review'
            applied_count += mask.sum()

        elif decision.lower() == 'reject':
            df.loc[mask, 'status'] = 'REJECT'
            df.loc[mask, 'review_decision'] = 'Rejected after manual review'
            applied_count += mask.sum()

    print(f"\n✅ Applied {len(review_decisions)} species-level decisions")
    print(f"   Updated {applied_count:,} detections")

    return df


if __name__ == "__main__":
    print("Smart Review Selector - Demo")
    print("=" * 80)
    print("\nThis module reduces review workload by selecting only the best")
    print("representative detections for each species.")
    print("\nInstead of reviewing thousands, review only 1-3 per species!")
