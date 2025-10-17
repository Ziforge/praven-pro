#!/usr/bin/env python3
"""
Generate Visualizations from BirdNET Analysis Results
Example: Create publication-quality plots from detection data

This script demonstrates how to create comprehensive visualizations
from BirdNET analysis results, including:
- Species abundance charts
- Confidence distributions
- Temporal activity patterns
- Daily summaries
- Per-species temporal patterns
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime

# ============================================================================
# CONFIGURATION - Customize for your project
# ============================================================================

# Input: Path to master detections CSV (from batch analysis)
DETECTIONS_CSV = "results/all_detections.csv"

# Output: Directory for visualizations
OUTPUT_DIR = "results/visualizations"

# Visualization settings
DPI = 300  # Resolution for saved images
TOP_N_SPECIES = 20  # Number of species to show in bar charts

# ============================================================================
# SETUP
# ============================================================================

print("📊 Generating visualizations from BirdNET analysis results...")
print()

# Load detections
if not os.path.exists(DETECTIONS_CSV):
    print(f"❌ Error: Detections file not found: {DETECTIONS_CSV}")
    print(f"   Run batch analysis first to generate this file.")
    exit(1)

df = pd.read_csv(DETECTIONS_CSV)
df['absolute_timestamp'] = pd.to_datetime(df['absolute_timestamp'])

# Create output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Set visualization style
sns.set_style('whitegrid')
plt.rcParams['figure.figsize'] = (14, 8)

print(f"📊 Loaded {len(df):,} detections from {df['common_name'].nunique()} species")
print()

# ============================================================================
# 1. SPECIES ABUNDANCE BAR CHART
# ============================================================================

print(f"📈 1. Creating species abundance chart (top {TOP_N_SPECIES})...")
fig, ax = plt.subplots(figsize=(14, 10))
species_counts = df['common_name'].value_counts().head(TOP_N_SPECIES)
species_counts.plot(kind='barh', ax=ax, color='steelblue')
ax.set_xlabel('Number of Detections', fontsize=12)
ax.set_ylabel('Species', fontsize=12)
ax.set_title(f'Top {TOP_N_SPECIES} Bird Species by Detection Count', fontsize=14, fontweight='bold')
ax.invert_yaxis()
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/01_species_abundance.png', dpi=DPI, bbox_inches='tight')
plt.close()
print(f'   ✅ Saved: {OUTPUT_DIR}/01_species_abundance.png')

# ============================================================================
# 2. CONFIDENCE DISTRIBUTION
# ============================================================================

print('📈 2. Creating confidence distribution plot...')
fig, ax = plt.subplots(figsize=(12, 6))
ax.hist(df['confidence'], bins=50, color='steelblue', edgecolor='black', alpha=0.7)
ax.axvline(df['confidence'].mean(), color='red', linestyle='--', linewidth=2,
           label=f'Mean: {df["confidence"].mean():.3f}')
ax.axvline(df['confidence'].median(), color='orange', linestyle='--', linewidth=2,
           label=f'Median: {df["confidence"].median():.3f}')
ax.set_xlabel('Confidence Score', fontsize=12)
ax.set_ylabel('Number of Detections', fontsize=12)
ax.set_title('Distribution of Detection Confidence Scores (All Species)', fontsize=14, fontweight='bold')
ax.legend(fontsize=10)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/02_confidence_distribution.png', dpi=DPI, bbox_inches='tight')
plt.close()
print(f'   ✅ Saved: {OUTPUT_DIR}/02_confidence_distribution.png')

# ============================================================================
# 3. TEMPORAL ACTIVITY (24-HOUR PATTERN)
# ============================================================================

print('📈 3. Creating temporal activity plot (24-hour pattern)...')
fig, ax = plt.subplots(figsize=(16, 6))
df['hour'] = df['absolute_timestamp'].dt.hour
hourly_counts = df.groupby('hour').size()
ax.plot(hourly_counts.index, hourly_counts.values, marker='o', linewidth=2, markersize=6, color='steelblue')
ax.fill_between(hourly_counts.index, hourly_counts.values, alpha=0.3, color='steelblue')
ax.set_xlabel('Hour of Day', fontsize=12)
ax.set_ylabel('Number of Detections', fontsize=12)
ax.set_title('Temporal Activity Pattern (All Species)', fontsize=14, fontweight='bold')
ax.set_xticks(range(0, 24))
ax.set_xlim(-0.5, 23.5)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/03_temporal_activity.png', dpi=DPI, bbox_inches='tight')
plt.close()
print(f'   ✅ Saved: {OUTPUT_DIR}/03_temporal_activity.png')

# ============================================================================
# 4. TOP SPECIES TEMPORAL PATTERNS
# ============================================================================

print('📈 4. Creating species temporal patterns (top 8)...')
top_species = df['common_name'].value_counts().head(8).index
fig, axes = plt.subplots(4, 2, figsize=(16, 12))
axes = axes.flatten()

for idx, species in enumerate(top_species):
    species_df = df[df['common_name'] == species]
    species_df['hour'] = species_df['absolute_timestamp'].dt.hour
    hourly = species_df.groupby('hour').size()

    axes[idx].plot(hourly.index, hourly.values, marker='o', linewidth=2, markersize=4, color='steelblue')
    axes[idx].fill_between(hourly.index, hourly.values, alpha=0.3, color='steelblue')
    axes[idx].set_title(f'{species} (n={len(species_df)})', fontsize=11, fontweight='bold')
    axes[idx].set_xlabel('Hour of Day', fontsize=9)
    axes[idx].set_ylabel('Detections', fontsize=9)
    axes[idx].set_xticks(range(0, 24, 4))
    axes[idx].set_xlim(-0.5, 23.5)
    axes[idx].grid(True, alpha=0.3)

plt.suptitle('Temporal Activity Patterns by Species', fontsize=14, fontweight='bold', y=1.00)
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/04_species_temporal_patterns.png', dpi=DPI, bbox_inches='tight')
plt.close()
print(f'   ✅ Saved: {OUTPUT_DIR}/04_species_temporal_patterns.png')

# ============================================================================
# 5. DAILY SUMMARY
# ============================================================================

print('📈 5. Creating daily summary...')
df['date'] = df['absolute_timestamp'].dt.date
daily_species = df.groupby('date')['common_name'].nunique()
daily_detections = df.groupby('date').size()

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

daily_detections.plot(kind='bar', ax=ax1, color='steelblue')
ax1.set_ylabel('Total Detections', fontsize=11)
ax1.set_title('Daily Detection Summary', fontsize=13, fontweight='bold')
ax1.tick_params(axis='x', rotation=45)
ax1.grid(True, alpha=0.3)

daily_species.plot(kind='bar', ax=ax2, color='darkgreen')
ax2.set_ylabel('Unique Species', fontsize=11)
ax2.set_xlabel('Date', fontsize=11)
ax2.tick_params(axis='x', rotation=45)
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/05_daily_summary.png', dpi=DPI, bbox_inches='tight')
plt.close()
print(f'   ✅ Saved: {OUTPUT_DIR}/05_daily_summary.png')

# ============================================================================
# 6. CONFIDENCE BY SPECIES (TOP 15)
# ============================================================================

print('📈 6. Creating confidence by species boxplot (top 15)...')
top15_species = df['common_name'].value_counts().head(15).index
df_top15 = df[df['common_name'].isin(top15_species)]

fig, ax = plt.subplots(figsize=(14, 8))
df_top15.boxplot(column='confidence', by='common_name', ax=ax, patch_artist=True)
ax.set_xlabel('Species', fontsize=11)
ax.set_ylabel('Confidence Score', fontsize=11)
ax.set_title('')
plt.suptitle('Detection Confidence by Species (Top 15)', fontsize=13, fontweight='bold')
plt.xticks(rotation=45, ha='right')
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/06_confidence_by_species.png', dpi=DPI, bbox_inches='tight')
plt.close()
print(f'   ✅ Saved: {OUTPUT_DIR}/06_confidence_by_species.png')

# ============================================================================
# SUMMARY
# ============================================================================

print()
print('✅ All visualizations complete!')
print(f'📁 Saved to: {OUTPUT_DIR}/')
print()
print('📊 Summary Statistics:')
print(f'   Total detections: {len(df):,}')
print(f'   Unique species: {df["common_name"].nunique()}')
print(f'   Date range: {df["absolute_timestamp"].min().date()} to {df["absolute_timestamp"].max().date()}')
print(f'   Confidence range: {df["confidence"].min():.3f} - {df["confidence"].max():.3f}')
print(f'   Mean confidence: {df["confidence"].mean():.3f}')
print()
