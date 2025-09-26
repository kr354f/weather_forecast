"""Weather service for integrating with OpenWeatherMap API."""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional
import httpx
from collections import defaultdict

from app.config import get_settings, get_api_key
from app.models import (
    CurrentWeatherResponse,
    ForecastResponse,
    SimpleCurrentWeather,
    SimpleForecastResponse,
    SimpleForecastDay,
    SimpleWeatherCondition,
    Coord
)


logger = logging.getLogger(__name__)


class WeatherServiceError(Exception):
    """Base exception for weather service errors."""
    pass


class WeatherAPIError(WeatherServiceError):
    """Exception raised when the weather API returns an error."""
    pass


class InvalidLocationError(WeatherServiceError):
    """Exception raised when the location is invalid."""
    pass


class APIKeyError(WeatherServiceError):
    """Exception raised when API key is missing or invalid."""
    pass


class WeatherService:
    """Service for fetching weather data from OpenWeatherMap API."""
    
    def __init__(self):
        self.settings = get_settings()
        self.base_url = self.settings.openweathermap_base_url
        self.timeout = self.settings.request_timeout
        self._client: Optional[httpx.AsyncClient] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self._client = httpx.AsyncClient(timeout=self.timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()
    
    def _get_client(self) -> httpx.AsyncClient:
        """Get HTTP client instance."""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self._client
    
    def _get_api_key(self) -> str:
        """Get API key and validate it exists."""
        api_key = get_api_key()
        if not api_key:
            raise APIKeyError(
                "OpenWeatherMap API key not found. Please set OPENWEATHERMAP_API_KEY environment variable."
            )
        return api_key
    
    async def _make_request(self, url: str, params: Dict) -> Dict:
        """Make HTTP request to OpenWeatherMap API."""
        try:
            client = self._get_client()
            response = await client.get(url, params=params)
            
            if response.status_code == 401:
                raise APIKeyError("Invalid API key")
            elif response.status_code == 404:
                raise InvalidLocationError("Location not found")
            elif response.status_code != 200:
                raise WeatherAPIError(f"API request failed with status {response.status_code}: {response.text}")
            
            return response.json()
            
        except httpx.TimeoutException:
            raise WeatherAPIError("Request timeout - weather service unavailable")
        except httpx.RequestError as e:
            raise WeatherAPIError(f"Network error: {str(e)}")
    
    async def get_current_weather_by_city(self, city: str) -> SimpleCurrentWeather:
        """Get current weather by city name."""
        api_key = self._get_api_key()
        url = f"{self.base_url}/weather"
        params = {
            "q": city,
            "appid": api_key,
            "units": "metric"
        }
        
        logger.info(f"Fetching current weather for city: {city}")
        data = await self._make_request(url, params)
        
        # Parse response using Pydantic model
        weather_data = CurrentWeatherResponse(**data)
        
        return self._convert_to_simple_current(weather_data)
    
    async def get_current_weather_by_coordinates(self, lat: float, lon: float) -> SimpleCurrentWeather:
        """Get current weather by coordinates."""
        api_key = self._get_api_key()
        url = f"{self.base_url}/weather"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": api_key,
            "units": "metric"
        }
        
        logger.info(f"Fetching current weather for coordinates: {lat}, {lon}")
        data = await self._make_request(url, params)
        
        # Parse response using Pydantic model
        weather_data = CurrentWeatherResponse(**data)
        
        return self._convert_to_simple_current(weather_data)
    
    async def get_forecast_by_city(self, city: str, days: int = 3) -> SimpleForecastResponse:
        """Get weather forecast by city name."""
        api_key = self._get_api_key()
        url = f"{self.base_url}/forecast"
        params = {
            "q": city,
            "appid": api_key,
            "units": "metric"
        }
        
        logger.info(f"Fetching {days}-day forecast for city: {city}")
        data = await self._make_request(url, params)
        
        # Parse response using Pydantic model
        forecast_data = ForecastResponse(**data)
        
        return self._convert_to_simple_forecast(forecast_data, days)
    
    async def get_forecast_by_coordinates(self, lat: float, lon: float, days: int = 3) -> SimpleForecastResponse:
        """Get weather forecast by coordinates."""
        api_key = self._get_api_key()
        url = f"{self.base_url}/forecast"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": api_key,
            "units": "metric"
        }
        
        logger.info(f"Fetching {days}-day forecast for coordinates: {lat}, {lon}")
        data = await self._make_request(url, params)
        
        # Parse response using Pydantic model
        forecast_data = ForecastResponse(**data)
        
        return self._convert_to_simple_forecast(forecast_data, days)
    
    async def check_api_health(self) -> bool:
        """Check if the weather API is accessible."""
        try:
            # Make a simple request to check API health
            # Using a known city to test connectivity
            await self.get_current_weather_by_city("London")
            return True
        except Exception as e:
            logger.error(f"Weather API health check failed: {str(e)}")
            return False
    
    def _convert_to_simple_current(self, weather_data: CurrentWeatherResponse) -> SimpleCurrentWeather:
        """Convert OpenWeatherMap response to simplified current weather."""
        primary_weather = weather_data.weather[0] if weather_data.weather else None
        
        return SimpleCurrentWeather(
            city=weather_data.name,
            country=weather_data.sys.country,
            coordinates=weather_data.coord,
            temperature=round(weather_data.main.temp, 1),
            feels_like=round(weather_data.main.feels_like, 1),
            humidity=weather_data.main.humidity,
            pressure=weather_data.main.pressure,
            weather=SimpleWeatherCondition(
                condition=primary_weather.main.lower() if primary_weather else "unknown",
                description=primary_weather.description if primary_weather else "No description available",
                icon=primary_weather.icon if primary_weather else ""
            ),
            wind_speed=round(weather_data.wind.speed, 1),
            wind_direction=weather_data.wind.deg,
            cloudiness=weather_data.clouds.all,
            visibility=weather_data.visibility,
            timestamp=datetime.fromtimestamp(weather_data.dt, tz=timezone.utc)
        )
    
    def _convert_to_simple_forecast(self, forecast_data: ForecastResponse, days: int) -> SimpleForecastResponse:
        """Convert OpenWeatherMap forecast response to simplified forecast."""
        # Group forecast items by date
        daily_forecasts = defaultdict(list)
        
        for item in forecast_data.list[:days * 8]:  # OpenWeatherMap provides 3-hour intervals (8 per day)
            date_str = item.dt_txt[:10]  # Extract date part (YYYY-MM-DD)
            daily_forecasts[date_str].append(item)
        
        # Create simplified daily forecasts
        forecast_days = []
        for date, items in list(daily_forecasts.items())[:days]:
            if not items:
                continue
                
            # Calculate daily aggregates
            temperatures = [item.main.temp for item in items]
            humidities = [item.main.humidity for item in items]
            wind_speeds = [item.wind.speed for item in items]
            pops = [item.pop for item in items]
            
            # Get most common weather condition for the day
            weather_conditions = [item.weather[0] for item in items if item.weather]
            primary_weather = weather_conditions[0] if weather_conditions else None
            
            forecast_day = SimpleForecastDay(
                date=date,
                temperature_min=round(min(temperatures), 1),
                temperature_max=round(max(temperatures), 1),
                humidity=round(sum(humidities) / len(humidities)),
                weather=SimpleWeatherCondition(
                    condition=primary_weather.main.lower() if primary_weather else "unknown",
                    description=primary_weather.description if primary_weather else "No description available",
                    icon=primary_weather.icon if primary_weather else ""
                ),
                wind_speed=round(sum(wind_speeds) / len(wind_speeds), 1),
                precipitation_probability=round(max(pops), 2)
            )
            forecast_days.append(forecast_day)
        
        return SimpleForecastResponse(
            city=forecast_data.city.name,
            country=forecast_data.city.country,
            coordinates=forecast_data.city.coord,
            forecast_days=forecast_days,
            generated_at=datetime.now(timezone.utc)
        )
    
    async def close(self):
        """Close HTTP client."""
        if self._client:
            await self._client.aclose()


# Global service instance
weather_service = WeatherService()


async def get_weather_service() -> WeatherService:
    """Dependency to get weather service instance."""
    return weather_service