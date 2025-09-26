"""Pydantic models for weather data and API responses."""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator


class WeatherCondition(BaseModel):
    """Weather condition details."""
    main: str = Field(..., description="Main weather condition (Rain, Snow, Clear, etc.)")
    description: str = Field(..., description="Weather condition description")
    icon: str = Field(..., description="Weather icon ID")


class MainWeatherData(BaseModel):
    """Main weather measurements."""
    temp: float = Field(..., description="Temperature in Celsius")
    feels_like: float = Field(..., description="Human perception of temperature in Celsius")
    temp_min: float = Field(..., description="Minimum temperature in Celsius")
    temp_max: float = Field(..., description="Maximum temperature in Celsius")
    pressure: int = Field(..., description="Atmospheric pressure in hPa")
    humidity: int = Field(..., description="Humidity percentage")
    sea_level: Optional[int] = Field(None, description="Sea level pressure in hPa")
    grnd_level: Optional[int] = Field(None, description="Ground level pressure in hPa")


class Wind(BaseModel):
    """Wind information."""
    speed: float = Field(..., description="Wind speed in m/s")
    deg: int = Field(..., description="Wind direction in degrees")
    gust: Optional[float] = Field(None, description="Wind gust in m/s")


class Clouds(BaseModel):
    """Cloud information."""
    all: int = Field(..., description="Cloudiness percentage")


class Sys(BaseModel):
    """System information."""
    country: str = Field(..., description="Country code")
    sunrise: int = Field(..., description="Sunrise time (Unix timestamp)")
    sunset: int = Field(..., description="Sunset time (Unix timestamp)")


class Coord(BaseModel):
    """Geographic coordinates."""
    lon: float = Field(..., description="Longitude")
    lat: float = Field(..., description="Latitude")


class CurrentWeatherResponse(BaseModel):
    """Current weather API response."""
    coord: Coord
    weather: List[WeatherCondition]
    base: str
    main: MainWeatherData
    visibility: int = Field(..., description="Visibility in meters")
    wind: Wind
    clouds: Clouds
    dt: int = Field(..., description="Data calculation time (Unix timestamp)")
    sys: Sys
    timezone: int = Field(..., description="Timezone offset in seconds")
    id: int = Field(..., description="City ID")
    name: str = Field(..., description="City name")
    cod: int = Field(..., description="HTTP status code")


class ForecastItem(BaseModel):
    """Single forecast entry."""
    dt: int = Field(..., description="Forecast time (Unix timestamp)")
    main: MainWeatherData
    weather: List[WeatherCondition]
    clouds: Clouds
    wind: Wind
    visibility: int = Field(..., description="Visibility in meters")
    pop: float = Field(..., description="Probability of precipitation")
    dt_txt: str = Field(..., description="Forecast time in text format")


class City(BaseModel):
    """City information in forecast."""
    id: int = Field(..., description="City ID")
    name: str = Field(..., description="City name")
    coord: Coord
    country: str = Field(..., description="Country code")
    population: int = Field(..., description="City population")
    timezone: int = Field(..., description="Timezone offset in seconds")
    sunrise: int = Field(..., description="Sunrise time (Unix timestamp)")
    sunset: int = Field(..., description="Sunset time (Unix timestamp)")


class ForecastResponse(BaseModel):
    """Weather forecast API response."""
    cod: str = Field(..., description="HTTP status code")
    message: int = Field(..., description="Message code")
    cnt: int = Field(..., description="Number of forecast entries")
    list: List[ForecastItem] = Field(..., description="Forecast data list")
    city: City


# Simplified response models for our API
class SimpleWeatherCondition(BaseModel):
    """Simplified weather condition for API response."""
    condition: str = Field(..., description="Weather condition (clear, rain, snow, etc.)")
    description: str = Field(..., description="Weather description")
    icon: str = Field(..., description="Weather icon ID")


class SimpleCurrentWeather(BaseModel):
    """Simplified current weather response."""
    city: str = Field(..., description="City name")
    country: str = Field(..., description="Country code")
    coordinates: Coord = Field(..., description="Geographic coordinates")
    temperature: float = Field(..., description="Current temperature in Celsius")
    feels_like: float = Field(..., description="Feels like temperature in Celsius")
    humidity: int = Field(..., description="Humidity percentage")
    pressure: int = Field(..., description="Atmospheric pressure in hPa")
    weather: SimpleWeatherCondition = Field(..., description="Weather conditions")
    wind_speed: float = Field(..., description="Wind speed in m/s")
    wind_direction: int = Field(..., description="Wind direction in degrees")
    cloudiness: int = Field(..., description="Cloudiness percentage")
    visibility: int = Field(..., description="Visibility in meters")
    timestamp: datetime = Field(..., description="Data timestamp")


class SimpleForecastDay(BaseModel):
    """Simplified daily forecast entry."""
    date: str = Field(..., description="Forecast date (YYYY-MM-DD)")
    temperature_min: float = Field(..., description="Minimum temperature in Celsius")
    temperature_max: float = Field(..., description="Maximum temperature in Celsius")
    humidity: int = Field(..., description="Average humidity percentage")
    weather: SimpleWeatherCondition = Field(..., description="Weather conditions")
    wind_speed: float = Field(..., description="Wind speed in m/s")
    precipitation_probability: float = Field(..., description="Precipitation probability (0-1)")


class SimpleForecastResponse(BaseModel):
    """Simplified forecast response."""
    city: str = Field(..., description="City name")
    country: str = Field(..., description="Country code")
    coordinates: Coord = Field(..., description="Geographic coordinates")
    forecast_days: List[SimpleForecastDay] = Field(..., description="Daily forecast")
    generated_at: datetime = Field(..., description="Response generation timestamp")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(..., description="Health check timestamp")
    version: str = Field(..., description="API version")
    weather_api_status: str = Field(..., description="External weather API status")


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    timestamp: datetime = Field(..., description="Error timestamp")
    status_code: int = Field(..., description="HTTP status code")


# Query parameter models
class WeatherQueryParams(BaseModel):
    """Base weather query parameters."""
    city: Optional[str] = Field(None, description="City name")
    lat: Optional[float] = Field(None, description="Latitude", ge=-90, le=90)
    lon: Optional[float] = Field(None, description="Longitude", ge=-180, le=180)
    
    @validator('city')
    def validate_city(cls, v, values):
        if v and (values.get('lat') is not None or values.get('lon') is not None):
            raise ValueError("Cannot specify both city and coordinates")
        return v
    
    @validator('lon')
    def validate_coordinates(cls, v, values):
        lat = values.get('lat')
        if (lat is None) != (v is None):
            raise ValueError("Both latitude and longitude must be provided for coordinate-based queries")
        if v is None and values.get('city') is None:
            raise ValueError("Either city name or coordinates (lat, lon) must be provided")
        return v


class ForecastQueryParams(WeatherQueryParams):
    """Forecast query parameters."""
    days: Optional[int] = Field(3, description="Number of forecast days", ge=1, le=5)