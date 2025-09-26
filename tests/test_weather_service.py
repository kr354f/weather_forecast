"""Unit tests for the weather service."""

import pytest
import httpx
from unittest.mock import AsyncMock, patch
from datetime import datetime, timezone

from app.services.weather_service import (
    WeatherService, 
    WeatherAPIError, 
    InvalidLocationError, 
    APIKeyError
)
from app.models import CurrentWeatherResponse, ForecastResponse


class TestWeatherService:
    """Test cases for WeatherService."""
    
    @pytest.fixture
    def weather_service(self):
        """Create a WeatherService instance for testing."""
        return WeatherService()
    
    @pytest.fixture
    def sample_current_weather_response(self):
        """Sample OpenWeatherMap current weather response."""
        return {
            "coord": {"lon": -0.1257, "lat": 51.5085},
            "weather": [
                {
                    "id": 804,
                    "main": "Clouds",
                    "description": "overcast clouds",
                    "icon": "04d"
                }
            ],
            "base": "stations",
            "main": {
                "temp": 15.3,
                "feels_like": 14.8,
                "temp_min": 13.2,
                "temp_max": 17.1,
                "pressure": 1013,
                "humidity": 72,
                "sea_level": 1013,
                "grnd_level": 1009
            },
            "visibility": 10000,
            "wind": {
                "speed": 3.6,
                "deg": 230,
                "gust": 7.2
            },
            "clouds": {
                "all": 90
            },
            "dt": 1727347200,
            "sys": {
                "type": 2,
                "id": 2019646,
                "country": "GB",
                "sunrise": 1727322180,
                "sunset": 1727365740
            },
            "timezone": 3600,
            "id": 2643743,
            "name": "London",
            "cod": 200
        }
    
    @pytest.fixture
    def sample_forecast_response(self):
        """Sample OpenWeatherMap forecast response."""
        return {
            "cod": "200",
            "message": 0,
            "cnt": 8,
            "list": [
                {
                    "dt": 1727370000,
                    "main": {
                        "temp": 16.2,
                        "feels_like": 15.8,
                        "temp_min": 14.1,
                        "temp_max": 16.2,
                        "pressure": 1014,
                        "sea_level": 1014,
                        "grnd_level": 1010,
                        "humidity": 75,
                        "temp_kf": 2.1
                    },
                    "weather": [
                        {
                            "id": 803,
                            "main": "Clouds",
                            "description": "broken clouds",
                            "icon": "04n"
                        }
                    ],
                    "clouds": {
                        "all": 75
                    },
                    "wind": {
                        "speed": 2.8,
                        "deg": 210,
                        "gust": 5.1
                    },
                    "visibility": 10000,
                    "pop": 0.12,
                    "dt_txt": "2025-09-26 15:00:00"
                }
            ],
            "city": {
                "id": 2643743,
                "name": "London",
                "coord": {
                    "lat": 51.5085,
                    "lon": -0.1257
                },
                "country": "GB",
                "population": 1000000,
                "timezone": 3600,
                "sunrise": 1727322180,
                "sunset": 1727365740
            }
        }
    
    @pytest.mark.asyncio
    async def test_get_current_weather_by_city_success(
        self, 
        weather_service, 
        sample_current_weather_response
    ):
        """Test successful current weather retrieval by city."""
        with patch.object(weather_service, '_make_request') as mock_request, \
             patch.object(weather_service, '_get_api_key', return_value="test_key"):
            
            mock_request.return_value = sample_current_weather_response
            
            result = await weather_service.get_current_weather_by_city("London")
            
            assert result.city == "London"
            assert result.country == "GB"
            assert result.temperature == 15.3
            assert result.weather.condition == "clouds"
            mock_request.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_current_weather_by_coordinates_success(
        self, 
        weather_service, 
        sample_current_weather_response
    ):
        """Test successful current weather retrieval by coordinates."""
        with patch.object(weather_service, '_make_request') as mock_request, \
             patch.object(weather_service, '_get_api_key', return_value="test_key"):
            
            mock_request.return_value = sample_current_weather_response
            
            result = await weather_service.get_current_weather_by_coordinates(51.5, -0.12)
            
            assert result.city == "London"
            assert result.coordinates.lat == 51.5085
            assert result.coordinates.lon == -0.1257
            mock_request.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_forecast_by_city_success(
        self, 
        weather_service, 
        sample_forecast_response
    ):
        """Test successful forecast retrieval by city."""
        with patch.object(weather_service, '_make_request') as mock_request, \
             patch.object(weather_service, '_get_api_key', return_value="test_key"):
            
            mock_request.return_value = sample_forecast_response
            
            result = await weather_service.get_forecast_by_city("London", 3)
            
            assert result.city == "London"
            assert result.country == "GB"
            assert len(result.forecast_days) <= 3
            mock_request.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_api_key_error(self, weather_service):
        """Test APIKeyError when API key is missing."""
        with patch.object(weather_service, '_get_api_key', return_value=None):
            with pytest.raises(APIKeyError):
                await weather_service.get_current_weather_by_city("London")
    
    @pytest.mark.asyncio
    async def test_invalid_location_error(self, weather_service):
        """Test InvalidLocationError for invalid location."""
        with patch.object(weather_service, '_get_api_key', return_value="test_key"):
            
            # Mock HTTP client to return 404
            mock_response = AsyncMock()
            mock_response.status_code = 404
            
            with patch.object(weather_service, '_get_client') as mock_get_client:
                mock_client = AsyncMock()
                mock_client.get.return_value = mock_response
                mock_get_client.return_value = mock_client
                
                with pytest.raises(InvalidLocationError):
                    await weather_service.get_current_weather_by_city("InvalidCity")
    
    @pytest.mark.asyncio
    async def test_weather_api_error(self, weather_service):
        """Test WeatherAPIError for API failures."""
        with patch.object(weather_service, '_get_api_key', return_value="test_key"):
            
            # Mock HTTP client to return 500
            mock_response = AsyncMock()
            mock_response.status_code = 500
            mock_response.text = "Internal Server Error"
            
            with patch.object(weather_service, '_get_client') as mock_get_client:
                mock_client = AsyncMock()
                mock_client.get.return_value = mock_response
                mock_get_client.return_value = mock_client
                
                with pytest.raises(WeatherAPIError):
                    await weather_service.get_current_weather_by_city("London")
    
    @pytest.mark.asyncio
    async def test_network_timeout(self, weather_service):
        """Test handling of network timeouts."""
        with patch.object(weather_service, '_get_api_key', return_value="test_key"):
            
            with patch.object(weather_service, '_get_client') as mock_get_client:
                mock_client = AsyncMock()
                mock_client.get.side_effect = httpx.TimeoutException("Timeout")
                mock_get_client.return_value = mock_client
                
                with pytest.raises(WeatherAPIError, match="Request timeout"):
                    await weather_service.get_current_weather_by_city("London")
    
    @pytest.mark.asyncio
    async def test_check_api_health_success(self, weather_service):
        """Test successful API health check."""
        with patch.object(weather_service, 'get_current_weather_by_city') as mock_get_weather:
            mock_get_weather.return_value = AsyncMock()
            
            result = await weather_service.check_api_health()
            
            assert result is True
            mock_get_weather.assert_called_once_with("London")
    
    @pytest.mark.asyncio
    async def test_check_api_health_failure(self, weather_service):
        """Test API health check failure."""
        with patch.object(weather_service, 'get_current_weather_by_city') as mock_get_weather:
            mock_get_weather.side_effect = WeatherAPIError("API unavailable")
            
            result = await weather_service.check_api_health()
            
            assert result is False