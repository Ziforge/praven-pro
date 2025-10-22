"""
Pipeline integration for automated BirdNET validation workflow.

Automates: BirdNET CSV → Praven Validation → Filtered Results
"""

import pandas as pd
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime

from .validator import BiologicalValidator
from .config import ValidationConfig
from .review_selector import SmartReviewSelector


class ValidationPipeline:
    """Automated validation pipeline for BirdNET results."""

    def __init__(self, config: ValidationConfig, smart_review: bool = True):
        """
        Initialize pipeline.

        Args:
            config: Validation configuration
            smart_review: Enable smart review selection (default: True)
                         Reduces review workload by selecting top 3 per species
        """
        self.config = config
        self.validator = BiologicalValidator(config)
        self.review_selector = SmartReviewSelector(detections_per_species=3) if smart_review else None
        self.results = None

    def process_birdnet_csv(
        self,
        input_path: str,
        output_dir: Optional[str] = None,
        export_formats: List[str] = ['csv', 'json']
    ) -> Dict[str, str]:
        """
        Process BirdNET CSV file through validation pipeline.

        Args:
            input_path: Path to BirdNET results CSV
            output_dir: Output directory (default: same as input)
            export_formats: Export formats ('csv', 'json', 'excel')

        Returns:
            Dictionary of output file paths
        """
        print(f"Loading BirdNET results: {input_path}")
        df = self._load_birdnet_csv(input_path)

        print(f"  Loaded {len(df):,} detections")
        print(f"  Unique species: {df['common_name'].nunique()}")

        # Run validation
        print(f"\nRunning biological validation...")
        validated_df = self.validator.validate_dataframe(
            df,
            species_col='common_name',
            time_col='absolute_timestamp',
            confidence_col='confidence',
            scientific_col='scientific_name'
        )

        self.results = validated_df

        # Apply smart review selection (reduce review workload)
        review_data = None
        if self.review_selector:
            review_data = self.review_selector.select_best_for_review(validated_df)

        # Export results
        if output_dir is None:
            output_dir = str(Path(input_path).parent)

        output_files = self._export_results(
            validated_df,
            output_dir,
            export_formats,
            review_data=review_data
        )

        # Print summary
        self._print_summary(validated_df, review_data=review_data)

        return output_files

    def _load_birdnet_csv(self, path: str) -> pd.DataFrame:
        """Load BirdNET CSV file with flexible column name mapping."""
        # Try different separators
        try:
            df = pd.read_csv(path, sep=',')
        except:
            try:
                df = pd.read_csv(path, sep='\t')
            except:
                raise ValueError(f"Could not parse CSV file: {path}")

        # Map common BirdNET column name variations
        column_mapping = {
            # Common name variations
            'Common name': 'common_name',
            'Common_name': 'common_name',
            'common name': 'common_name',
            'Species': 'common_name',
            'species': 'common_name',

            # Scientific name variations
            'Scientific name': 'scientific_name',
            'Scientific_name': 'scientific_name',
            'scientific name': 'scientific_name',

            # Confidence variations
            'Confidence': 'confidence',

            # Time variations
            'Begin Time (s)': 'start_time',
            'Start (s)': 'start_time',
            'Begin Time': 'start_time',
            'Start': 'start_time',

            'End Time (s)': 'end_time',
            'End (s)': 'end_time',
            'End Time': 'end_time',
            'End': 'end_time',

            # File path variations
            'File name': 'file_name',
            'Filename': 'file_name',
            'filename': 'file_name',
        }

        # Rename columns based on mapping
        df = df.rename(columns=column_mapping)

        # Verify required columns exist
        required_cols = ['common_name', 'confidence']
        missing = [col for col in required_cols if col not in df.columns]

        if missing:
            raise ValueError(
                f"Missing required columns: {', '.join(missing)}. "
                f"Available columns: {', '.join(df.columns)}"
            )

        return df

    def _export_results(
        self,
        df: pd.DataFrame,
        output_dir: str,
        formats: List[str],
        review_data: Optional[Dict] = None
    ) -> Dict[str, str]:
        """Export validation results in multiple formats."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_name = f"praven_results_{timestamp}"

        output_files = {}

        # Export full results
        if 'csv' in formats:
            full_path = output_dir / f"{base_name}_full.csv"
            df.to_csv(full_path, index=False)
            output_files['full_csv'] = str(full_path)
            print(f"\nExported full results: {full_path}")

        if 'json' in formats:
            json_path = output_dir / f"{base_name}_full.json"
            df.to_json(json_path, orient='records', indent=2)
            output_files['full_json'] = str(json_path)

        if 'excel' in formats:
            excel_path = output_dir / f"{base_name}_full.xlsx"
            df.to_excel(excel_path, index=False, engine='openpyxl')
            output_files['full_excel'] = str(excel_path)

        # Export subsets
        accepted = df[df['status'] == 'ACCEPT']
        rejected = df[df['status'] == 'REJECT']
        review = df[df['status'] == 'REVIEW']

        if 'csv' in formats:
            accepted_path = output_dir / f"{base_name}_accepted.csv"
            rejected_path = output_dir / f"{base_name}_rejected.csv"
            review_path = output_dir / f"{base_name}_review.csv"

            accepted.to_csv(accepted_path, index=False)
            rejected.to_csv(rejected_path, index=False)
            review.to_csv(review_path, index=False)

            output_files['accepted_csv'] = str(accepted_path)
            output_files['rejected_csv'] = str(rejected_path)
            output_files['review_csv'] = str(review_path)

            print(f"Exported accepted: {accepted_path}")
            print(f"Exported rejected: {rejected_path}")
            print(f"Exported review: {review_path}")

        # Export smart review selection (top 3 per species)
        if review_data and 'review_required' in review_data:
            priority_review = review_data['review_required']
            if len(priority_review) > 0:
                priority_path = output_dir / f"{base_name}_PRIORITY_REVIEW.csv"
                priority_review.to_csv(priority_path, index=False)
                output_files['priority_review'] = str(priority_path)

                print(f"\n🎯 Smart Review Selection:")
                print(f"   Priority review (top 3/species): {priority_path}")
                print(f"   → Review only {len(priority_review):,} detections instead of {len(review):,}!")
                print(f"   → {100*(1-len(priority_review)/len(review)):.0f}% workload reduction")

        # Export summary report
        summary_path = output_dir / f"{base_name}_summary.txt"
        self._export_summary_report(df, summary_path, review_data=review_data)
        output_files['summary'] = str(summary_path)

        return output_files

    def _export_summary_report(self, df: pd.DataFrame, path: Path, review_data: Optional[Dict] = None) -> None:
        """Export text summary report."""
        stats = self.validator.get_validation_stats(df)

        with open(path, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("Praven Pro Validation Summary Report\n")
            f.write("=" * 80 + "\n\n")

            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Location: {self.config.location}\n")
            f.write(f"Date: {self.config.date}\n")
            f.write(f"Habitat: {self.config.habitat_type}\n\n")

            f.write("Validation Results\n")
            f.write("-" * 80 + "\n")
            f.write(f"Total Detections:     {stats['total_detections']:,}\n")
            f.write(f"Auto-Accepted:        {stats['accepted']:,} ({100*stats['auto_pass_rate']:.1f}%)\n")
            f.write(f"Auto-Rejected:        {stats['rejected']:,} ({100*stats['auto_reject_rate']:.1f}%)\n")
            f.write(f"Needs Review:         {stats['needs_review']:,} ({100*stats['review_rate']:.1f}%)\n\n")

            if 'rejection_reasons' in stats and stats['rejection_reasons']:
                f.write("Top Rejection Reasons\n")
                f.write("-" * 80 + "\n")
                for reason, count in list(stats['rejection_reasons'].items())[:10]:
                    f.write(f"[{count:3d}] {reason}\n")
                f.write("\n")

            # Add smart review info
            if review_data and 'review_summary' in review_data:
                summary = review_data['review_summary']
                f.write("Smart Review Selection\n")
                f.write("-" * 80 + "\n")
                f.write(f"Original review workload: {stats['needs_review']:,} detections\n")
                f.write(f"Priority review (top 3/species): {summary['review_required']:,} detections\n")
                f.write(f"Workload reduction: {summary['reduction_percent']:.0f}%\n")
                f.write(f"Species requiring review: {summary['species_to_review']}\n\n")
                f.write("Review Instructions:\n")
                f.write("  1. Open the PRIORITY_REVIEW.csv file\n")
                f.write("  2. Review the top 3 detections for each species\n")
                f.write("  3. If all 3 are valid → Accept the whole species\n")
                f.write("  4. If all 3 are invalid → Reject the whole species\n")
                f.write("  5. If uncertain → Review additional detections from review.csv\n\n")

        print(f"Exported summary: {path}")

    def _print_summary(self, df: pd.DataFrame, review_data: Optional[Dict] = None) -> None:
        """Print validation summary to console."""
        stats = self.validator.get_validation_stats(df)

        print(f"\n{'=' * 80}")
        print("Validation Complete!")
        print("=" * 80)

        print(f"\nResults:")
        print(f"  Total:        {stats['total_detections']:,} detections")
        print(f"  Accepted:     {stats['accepted']:,} ({100*stats['auto_pass_rate']:.1f}%)")
        print(f"  Rejected:     {stats['rejected']:,} ({100*stats['auto_reject_rate']:.1f}%)")
        print(f"  Needs Review: {stats['needs_review']:,} ({100*stats['review_rate']:.1f}%)")

        # Species summary
        accepted_species = df[df['status'] == 'ACCEPT']['common_name'].nunique()
        rejected_species = df[df['status'] == 'REJECT']['common_name'].nunique()

        print(f"\nSpecies:")
        print(f"  Accepted: {accepted_species} species")
        print(f"  Rejected: {rejected_species} species")

        # Smart review info
        if review_data and 'review_summary' in review_data:
            summary = review_data['review_summary']
            print(f"\n🎯 Smart Review Reduction:")
            print(f"  Original workload: {stats['needs_review']:,} detections")
            print(f"  Priority review:   {summary['review_required']:,} detections (top 3/species)")
            print(f"  Workload saved:    {summary['reduction_percent']:.0f}%")
            print(f"  → Review the PRIORITY_REVIEW.csv file instead of review.csv!")

    def batch_process(
        self,
        input_files: List[str],
        output_dir: str,
        export_formats: List[str] = ['csv']
    ) -> List[Dict[str, str]]:
        """
        Batch process multiple BirdNET CSV files.

        Args:
            input_files: List of input CSV paths
            output_dir: Output directory
            export_formats: Export formats

        Returns:
            List of output file dictionaries
        """
        all_outputs = []

        print(f"\n{'=' * 80}")
        print(f"Batch Processing {len(input_files)} Files")
        print("=" * 80)

        for i, input_file in enumerate(input_files, 1):
            print(f"\n[{i}/{len(input_files)}] Processing: {input_file}")

            try:
                outputs = self.process_birdnet_csv(
                    input_file,
                    output_dir,
                    export_formats
                )
                all_outputs.append(outputs)

            except Exception as e:
                print(f"  ERROR: {e}")
                all_outputs.append({"error": str(e)})

        print(f"\n{'=' * 80}")
        print(f"Batch Processing Complete!")
        print(f"Processed: {len(input_files)} files")
        print(f"Success: {len([o for o in all_outputs if 'error' not in o])}")
        print("=" * 80)

        return all_outputs


def create_pipeline(
    location: tuple,
    date: str,
    habitat_type: str,
    weather: Optional[dict] = None,
    ebird_api_key: Optional[str] = None
) -> ValidationPipeline:
    """
    Create validation pipeline with configuration.

    Args:
        location: (latitude, longitude)
        date: Date in YYYY-MM-DD format
        habitat_type: Habitat type
        weather: Weather conditions dictionary (optional)
        ebird_api_key: eBird API key (optional)

    Returns:
        ValidationPipeline instance
    """
    config = ValidationConfig(
        location=location,
        date=date,
        habitat_type=habitat_type,
        weather_conditions=weather,
        ebird_api_key=ebird_api_key
    )

    return ValidationPipeline(config)
