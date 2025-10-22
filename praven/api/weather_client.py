"""
Weather API client for automatic weather data retrieval.

Uses Open-Meteo API (free, no API key required) to fetch historical weather
data based on GPS coordinates and datetime.
"""

import requests
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import json
from pathlib import Path


class WeatherClient:
    """Client for fetching historical weather data from Open-Meteo API."""

    def __init__(self, cache_dir: str = "cache/weather"):
        """
        Initialize weather client.

        Args:
            cache_dir: Directory for caching weather data
        """
        self.base_url = "https://api.open-meteo.com/v1/forecast"
        self.archive_url = "https://archive-api.open-meteo.com/v1/archive"
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get_weather(
        self,
        lat: float,
        lon: float,
        date: str,
        time: Optional[str] = None
    ) -> Dict[str, float]:
        """
        Get weather conditions for specific location and time.

        Args:
            lat: Latitude
            lon: Longitude
            date: Date in YYYY-MM-DD format
            time: Time in HH:MM format (optional, defaults to 12:00)

        Returns:
            Dictionary with weather conditions:
            {
                'temperature': float (°C),
                'rain': float (0.0-1.0 normalized),
                'fog': float (0.0-1.0 visibility-based),
                'wind_speed': float (km/h),
                'cloud_cover': float (0-100%)
            }
        """
        # Check cache first
        cache_key = f"{lat:.3f}_{lon:.3f}_{date}"
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached

        # Parse date and time
        dt = datetime.strptime(date, "%Y-%m-%d")
        if time:
            hour = int(time.split(':')[0])
        else:
            hour = 12  # Default to noon

        # Determine if we need archive or forecast API
        days_ago = (datetime.now() - dt).days

        if days_ago > 5:
            # Use archive API for historical data (>5 days old)
            weather_data = self._fetch_archive_weather(lat, lon, date, hour)
        else:
            # Use forecast API for recent data
            weather_data = self._fetch_forecast_weather(lat, lon, date, hour)

        # Cache the result
        self._save_to_cache(cache_key, weather_data)

        return weather_data

    def _fetch_archive_weather(
        self,
        lat: float,
        lon: float,
        date: str,
        hour: int
    ) -> Dict[str, float]:
        """Fetch historical weather data from archive API."""
        params = {
            'latitude': lat,
            'longitude': lon,
            'start_date': date,
            'end_date': date,
            'hourly': [
                'temperature_2m',
                'precipitation',
                'visibility',
                'windspeed_10m',
                'cloudcover'
            ],
            'timezone': 'auto'
        }

        try:
            response = requests.get(self.archive_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            return self._parse_weather_response(data, hour)

        except Exception as e:
            print(f"Warning: Could not fetch archive weather data: {e}")
            return self._get_default_weather()

    def _fetch_forecast_weather(
        self,
        lat: float,
        lon: float,
        date: str,
        hour: int
    ) -> Dict[str, float]:
        """Fetch recent weather data from forecast API."""
        params = {
            'latitude': lat,
            'longitude': lon,
            'hourly': [
                'temperature_2m',
                'precipitation',
                'visibility',
                'windspeed_10m',
                'cloudcover'
            ],
            'past_days': 7,
            'forecast_days': 1,
            'timezone': 'auto'
        }

        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            return self._parse_weather_response(data, hour, date)

        except Exception as e:
            print(f"Warning: Could not fetch weather data: {e}")
            return self._get_default_weather()

    def _parse_weather_response(
        self,
        data: Dict,
        hour: int,
        target_date: Optional[str] = None
    ) -> Dict[str, float]:
        """Parse Open-Meteo API response."""
        hourly = data.get('hourly', {})
        times = hourly.get('time', [])

        # Find the closest matching hour
        if target_date:
            # Find index for specific date and hour
            target_time = f"{target_date}T{hour:02d}:00"
            try:
                idx = times.index(target_time)
            except ValueError:
                # Fallback to closest hour
                idx = hour if hour < len(times) else 0
        else:
            # Use provided hour index
            idx = hour if hour < len(times) else 0

        # Extract weather variables with None handling
        temp_list = hourly.get('temperature_2m', [15.0] * (idx + 1))
        precip_list = hourly.get('precipitation', [0.0] * (idx + 1))
        visibility_list = hourly.get('visibility', [10000.0] * (idx + 1))
        wind_list = hourly.get('windspeed_10m', [0.0] * (idx + 1))
        clouds_list = hourly.get('cloudcover', [0.0] * (idx + 1))

        temp = temp_list[idx] if idx < len(temp_list) and temp_list[idx] is not None else 15.0
        precip = precip_list[idx] if idx < len(precip_list) and precip_list[idx] is not None else 0.0
        visibility = visibility_list[idx] if idx < len(visibility_list) and visibility_list[idx] is not None else 10000.0
        wind = wind_list[idx] if idx < len(wind_list) and wind_list[idx] is not None else 0.0
        clouds = clouds_list[idx] if idx < len(clouds_list) and clouds_list[idx] is not None else 0.0

        # Normalize values for Praven
        rain_normalized = self._normalize_precipitation(precip)
        fog_normalized = self._normalize_visibility(visibility)

        return {
            'temperature': float(temp),
            'rain': rain_normalized,
            'fog': fog_normalized,
            'wind_speed': float(wind),
            'cloud_cover': float(clouds) / 100.0,  # Normalize from 0-100 to 0-1
            'raw_precipitation_mm': float(precip),
            'raw_visibility_m': float(visibility)
        }

    def _normalize_precipitation(self, precip_mm: float) -> float:
        """
        Normalize precipitation to 0.0-1.0 scale.

        Scale:
        0.0 mm = 0.0 (no rain)
        0.5 mm = 0.2 (light drizzle)
        2.5 mm = 0.5 (moderate rain)
        10 mm  = 0.8 (heavy rain)
        25+ mm = 1.0 (very heavy rain)
        """
        if precip_mm <= 0:
            return 0.0
        elif precip_mm < 0.5:
            return 0.1
        elif precip_mm < 2.5:
            return 0.2 + (precip_mm - 0.5) / 2.0 * 0.3  # 0.2-0.5
        elif precip_mm < 10:
            return 0.5 + (precip_mm - 2.5) / 7.5 * 0.3  # 0.5-0.8
        else:
            return min(1.0, 0.8 + (precip_mm - 10) / 15 * 0.2)  # 0.8-1.0

    def _normalize_visibility(self, visibility_m: float) -> float:
        """
        Normalize visibility to fog density (0.0-1.0 scale).

        Scale:
        >10 km = 0.0 (no fog)
        5 km   = 0.2 (light haze)
        1 km   = 0.5 (moderate fog)
        200 m  = 0.8 (heavy fog)
        <50 m  = 1.0 (dense fog)
        """
        if visibility_m >= 10000:
            return 0.0
        elif visibility_m >= 5000:
            return 0.2 * (1 - (visibility_m - 5000) / 5000)  # 0.0-0.2
        elif visibility_m >= 1000:
            return 0.2 + 0.3 * (1 - (visibility_m - 1000) / 4000)  # 0.2-0.5
        elif visibility_m >= 200:
            return 0.5 + 0.3 * (1 - (visibility_m - 200) / 800)  # 0.5-0.8
        else:
            return min(1.0, 0.8 + 0.2 * (1 - visibility_m / 200))  # 0.8-1.0

    def _get_default_weather(self) -> Dict[str, float]:
        """Return default weather conditions when API fails."""
        return {
            'temperature': 15.0,
            'rain': 0.0,
            'fog': 0.0,
            'wind_speed': 5.0,
            'cloud_cover': 50.0,
            'raw_precipitation_mm': 0.0,
            'raw_visibility_m': 10000.0
        }

    def _get_from_cache(self, cache_key: str) -> Optional[Dict[str, float]]:
        """Get weather data from cache."""
        cache_file = self.cache_dir / f"{cache_key}.json"

        if cache_file.exists():
            # Check if cache is less than 30 days old
            age_days = (datetime.now().timestamp() - cache_file.stat().st_mtime) / 86400
            if age_days < 30:
                try:
                    with open(cache_file, 'r') as f:
                        return json.load(f)
                except Exception:
                    pass

        return None

    def _save_to_cache(self, cache_key: str, data: Dict[str, float]) -> None:
        """Save weather data to cache."""
        cache_file = self.cache_dir / f"{cache_key}.json"
        try:
            with open(cache_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not cache weather data: {e}")


def get_weather_for_detection(
    lat: float,
    lon: float,
    timestamp: str
) -> Dict[str, float]:
    """
    Convenience function to get weather for a detection.

    Args:
        lat: Latitude
        lon: Longitude
        timestamp: ISO timestamp (e.g., "2025-10-15 14:30:00")

    Returns:
        Weather conditions dictionary
    """
    client = WeatherClient()

    # Parse timestamp
    dt = datetime.fromisoformat(timestamp.replace(' ', 'T'))
    date = dt.strftime('%Y-%m-%d')
    time = dt.strftime('%H:%M')

    return client.get_weather(lat, lon, date, time)


if __name__ == "__main__":
    # Demo
    client = WeatherClient()

    # Test with Gaulossen coordinates
    weather = client.get_weather(
        lat=63.341,
        lon=10.215,
        date="2025-10-15",
        time="14:30"
    )

    print("Weather Conditions:")
    print(f"  Temperature: {weather['temperature']:.1f}°C")
    print(f"  Rain: {weather['rain']:.2f} (normalized)")
    print(f"  Fog: {weather['fog']:.2f} (normalized)")
    print(f"  Wind: {weather['wind_speed']:.1f} km/h")
    print(f"  Clouds: {weather['cloud_cover']:.0f}%")
    print(f"  Raw precipitation: {weather['raw_precipitation_mm']:.2f} mm")
    print(f"  Raw visibility: {weather['raw_visibility_m']:.0f} m")
