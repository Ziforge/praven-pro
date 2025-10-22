#!/usr/bin/env python3
"""
Test automatic weather and habitat detection features.
"""

from praven.config import ValidationConfig

print("=" * 80)
print("Testing Automatic Detection Features")
print("=" * 80)

# Test 1: Auto-detect both weather and habitat
print("\n### Test 1: Auto-detect weather and habitat ###")
print("Creating config with only GPS coordinates and date...")

config = ValidationConfig(
    location=(63.341, 10.215),  # Gaulossen Nature Reserve
    date="2025-10-15",
    habitat_type=None,  # Auto-detect
    weather_conditions=None,  # Auto-fetch
    auto_detect_habitat=True,
    auto_detect_weather=True
)

print(f"\n✅ Config created successfully!")
print(f"   Habitat: {config.habitat_type}")
print(f"   Weather: {config.weather_conditions}")

# Test 2: Manual habitat, auto weather
print("\n### Test 2: Manual habitat, auto weather ###")
config2 = ValidationConfig(
    location=(63.341, 10.215),
    date="2025-10-15",
    habitat_type="wetland",
    weather_conditions=None,
    auto_detect_habitat=False,
    auto_detect_weather=True
)

print(f"\n✅ Config created successfully!")
print(f"   Habitat: {config2.habitat_type} (manual)")
print(f"   Weather: {config2.weather_conditions}")

# Test 3: All manual
print("\n### Test 3: All manual (no auto-detection) ###")
config3 = ValidationConfig(
    location=(63.341, 10.215),
    date="2025-10-15",
    habitat_type="wetland",
    weather_conditions={'rain': 0.3, 'fog': 0.2},
    auto_detect_habitat=False,
    auto_detect_weather=False
)

print(f"\n✅ Config created successfully!")
print(f"   Habitat: {config3.habitat_type} (manual)")
print(f"   Weather: {config3.weather_conditions} (manual)")

print("\n" + "=" * 80)
print("All tests passed! ✅")
print("=" * 80)
