"""
Visualization Dashboard for Praven Pro Validation Results

Generates interactive HTML charts showing validation metrics and breakdowns.
"""

import pandas as pd
import json
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime


def generate_dashboard(
    results_df: pd.DataFrame,
    output_path: str = "validation_dashboard.html",
    config: Optional[Dict] = None
) -> str:
    """
    Generate interactive HTML dashboard from validation results.

    Args:
        results_df: DataFrame with validation results (must have 'status' column)
        output_path: Path to save HTML dashboard
        config: Optional configuration dict with location, date, habitat info

    Returns:
        Path to generated HTML file
    """

    # Calculate statistics
    stats = {
        'total': len(results_df),
        'accepted': (results_df['status'] == 'ACCEPT').sum(),
        'rejected': (results_df['status'] == 'REJECT').sum(),
        'review': (results_df['status'] == 'REVIEW').sum(),
        'species_count': results_df['common_name'].nunique() if 'common_name' in results_df.columns else 0
    }

    stats['accept_rate'] = 100 * stats['accepted'] / stats['total'] if stats['total'] > 0 else 0
    stats['reject_rate'] = 100 * stats['rejected'] / stats['total'] if stats['total'] > 0 else 0
    stats['review_rate'] = 100 * stats['review'] / stats['total'] if stats['total'] > 0 else 0

    # Top species
    top_species = results_df['common_name'].value_counts().head(10) if 'common_name' in results_df.columns else pd.Series()

    # Status by species (top 10)
    status_by_species = ""
    if 'common_name' in results_df.columns and 'status' in results_df.columns:
        top_species_names = results_df['common_name'].value_counts().head(10).index
        species_status = []
        for species in top_species_names:
            species_df = results_df[results_df['common_name'] == species]
            species_status.append({
                'species': species,
                'accept': (species_df['status'] == 'ACCEPT').sum(),
                'reject': (species_df['status'] == 'REJECT').sum(),
                'review': (species_df['status'] == 'REVIEW').sum()
            })

        status_by_species = "<table style='width:100%; border-collapse:collapse; margin-top:20px;'>"
        status_by_species += "<tr style='background:#f0f0f0'><th>Species</th><th>Accept</th><th>Reject</th><th>Review</th><th>Total</th></tr>"
        for item in species_status:
            total = item['accept'] + item['reject'] + item['review']
            status_by_species += f"<tr><td>{item['species']}</td><td style='color:green'>{item['accept']}</td><td style='color:red'>{item['reject']}</td><td style='color:orange'>{item['review']}</td><td><b>{total}</b></td></tr>"
        status_by_species += "</table>"

    # Rejection reasons
    rejection_table = ""
    if 'rejection_reason' in results_df.columns:
        rejected = results_df[results_df['status'] == 'REJECT']
        if len(rejected) > 0:
            reasons = rejected['rejection_reason'].value_counts().head(10)
            rejection_table = "<table style='width:100%; border-collapse:collapse; margin-top:20px;'>"
            rejection_table += "<tr style='background:#f0f0f0'><th>Rejection Reason</th><th>Count</th></tr>"
            for reason, count in reasons.items():
                reason_short = (reason[:80] + '...') if len(reason) > 80 else reason
                rejection_table += f"<tr><td>{reason_short}</td><td><b>{count}</b></td></tr>"
            rejection_table += "</table>"

    # Config info
    config_html = ""
    if config:
        config_html = f"""
        <div style='background:#f9f9f9; padding:15px; border-radius:5px; margin-bottom:20px;'>
            <h3>Study Configuration</h3>
            <p><strong>Location:</strong> {config.get('location', 'N/A')}</p>
            <p><strong>Date:</strong> {config.get('date', 'N/A')}</p>
            <p><strong>Habitat:</strong> {config.get('habitat_type', 'N/A')}</p>
            {f"<p><strong>Weather:</strong> {config.get('weather_conditions', {})}</p>" if config.get('weather_conditions') else ""}
        </div>
        """

    # Generate HTML
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Praven Pro Validation Dashboard</title>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: 'Segoe UI', Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background: #f5f5f5;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #2c3e50;
                border-bottom: 3px solid #3498db;
                padding-bottom: 10px;
            }}
            h2 {{
                color: #34495e;
                margin-top: 30px;
            }}
            .metrics {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin: 30px 0;
            }}
            .metric-card {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                border-radius: 10px;
                text-align: center;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }}
            .metric-card.green {{
                background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            }}
            .metric-card.red {{
                background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
            }}
            .metric-card.orange {{
                background: linear-gradient(135deg, #f46b45 0%, #eea849 100%);
            }}
            .metric-value {{
                font-size: 48px;
                font-weight: bold;
                margin: 10px 0;
            }}
            .metric-label {{
                font-size: 14px;
                opacity: 0.9;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
            .metric-subtitle {{
                font-size: 18px;
                margin-top: 5px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }}
            th, td {{
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }}
            th {{
                background-color: #f0f0f0;
                font-weight: bold;
            }}
            tr:hover {{
                background-color: #f5f5f5;
            }}
            .chart {{
                margin: 30px 0;
                padding: 20px;
                background: #f9f9f9;
                border-radius: 5px;
            }}
            .status-badge {{
                display: inline-block;
                padding: 5px 10px;
                border-radius: 3px;
                font-size: 12px;
                font-weight: bold;
            }}
            .status-accept {{ background: #27ae60; color: white; }}
            .status-reject {{ background: #e74c3c; color: white; }}
            .status-review {{ background: #f39c12; color: white; }}
            .timestamp {{
                color: #7f8c8d;
                font-size: 14px;
                text-align: center;
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #ecf0f1;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🐦 Praven Pro Validation Dashboard</h1>
            <p style="color:#7f8c8d; font-size:16px;">Automated BirdNET Biological Validation Results</p>

            {config_html}

            <div class="metrics">
                <div class="metric-card">
                    <div class="metric-label">Total Detections</div>
                    <div class="metric-value">{stats['total']:,}</div>
                    <div class="metric-subtitle">{stats['species_count']} species</div>
                </div>

                <div class="metric-card green">
                    <div class="metric-label">Auto-Accepted</div>
                    <div class="metric-value">{stats['accepted']:,}</div>
                    <div class="metric-subtitle">{stats['accept_rate']:.1f}%</div>
                </div>

                <div class="metric-card red">
                    <div class="metric-label">Auto-Rejected</div>
                    <div class="metric-value">{stats['rejected']:,}</div>
                    <div class="metric-subtitle">{stats['reject_rate']:.1f}%</div>
                </div>

                <div class="metric-card orange">
                    <div class="metric-label">Needs Review</div>
                    <div class="metric-value">{stats['review']:,}</div>
                    <div class="metric-subtitle">{stats['review_rate']:.1f}%</div>
                </div>
            </div>

            <h2>📊 Status Breakdown by Species (Top 10)</h2>
            {status_by_species}

            <h2>❌ Top Rejection Reasons</h2>
            {rejection_table if rejection_table else "<p>No rejections found</p>"}

            <h2>🔝 Most Detected Species</h2>
            <table>
                <tr><th>Species</th><th>Detections</th><th>% of Total</th></tr>
                {"".join(f"<tr><td>{species}</td><td><b>{count}</b></td><td>{100*count/stats['total']:.1f}%</td></tr>" for species, count in top_species.items())}
            </table>

            <div class="timestamp">
                Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Praven Pro v2.1
            </div>
        </div>
    </body>
    </html>
    """

    # Write to file
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)

    return str(output_file)


def create_dashboard_from_csv(
    csv_path: str,
    output_path: str = "validation_dashboard.html",
    config_path: Optional[str] = None
) -> str:
    """
    Create dashboard from validation results CSV.

    Args:
        csv_path: Path to validated CSV file
        output_path: Path to save HTML dashboard
        config_path: Optional path to config JSON

    Returns:
        Path to generated HTML file
    """
    # Load data
    df = pd.read_csv(csv_path)

    # Load config if provided
    config = None
    if config_path and Path(config_path).exists():
        with open(config_path) as f:
            config = json.load(f)

    # Generate dashboard
    return generate_dashboard(df, output_path, config)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python visualization.py <results.csv> [output.html]")
        print("\nGenerates interactive HTML dashboard from Praven validation results")
        sys.exit(1)

    csv_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else "validation_dashboard.html"

    if not Path(csv_path).exists():
        print(f"ERROR: File not found: {csv_path}")
        sys.exit(1)

    output = create_dashboard_from_csv(csv_path, output_path)
    print(f"✅ Dashboard created: {output}")
    print(f"   Open in browser: file://{Path(output).absolute()}")
