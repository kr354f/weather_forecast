"""Integration tests for the weather API endpoints."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

from app.main import app
from app.services.weather_service import WeatherAPIError, InvalidLocationError, APIKeyError
from app.models import SimpleCurrentWeather, SimpleForecastResponse, Coord, SimpleWeatherCondition


client = TestClient(app)


class TestWeatherAPI:
    """Test cases for weather API endpoints."""
    
    def test_root_endpoint(self):
        """Test root endpoint returns service information."""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert "service" in data
        assert "version" in data
        assert "status" in data
        assert data["status"] == "running"
    
    def test_simple_health_check(self):
        """Test simple health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    @patch('app.services.weather_service.weather_service.get_current_weather_by_city')
    def test_get_current_weather_by_city_success(self, mock_get_weather):
        """Test successful current weather retrieval by city."""
        # Mock the weather service response
        mock_weather_data = SimpleCurrentWeather(
            city="London",
            country="GB",
            coordinates=Coord(lon=-0.1257, lat=51.5085),
            temperature=15.3,
            feels_like=14.8,
            humidity=72,
            pressure=1013,
            weather=SimpleWeatherCondition(
                condition="clouds",
                description="overcast clouds",
                icon="04d"
            ),
            wind_speed=3.6,
            wind_direction=230,
            cloudiness=90,
            visibility=10000,
            timestamp="2025-09-26T10:30:00Z"
        )
        
        mock_get_weather.return_value = mock_weather_data
        
        response = client.get("/api/v1/weather/current?city=London")
        assert response.status_code == 200
        
        data = response.json()
        assert data["city"] == "London"
        assert data["country"] == "GB"
        assert data["temperature"] == 15.3
        assert data["weather"]["condition"] == "clouds"
    
    @patch('app.services.weather_service.weather_service.get_current_weather_by_coordinates')
    def test_get_current_weather_by_coordinates_success(self, mock_get_weather):
        """Test successful current weather retrieval by coordinates."""
        mock_weather_data = SimpleCurrentWeather(
            city="London",
            country="GB",
            coordinates=Coord(lon=-0.1278, lat=51.5074),
            temperature=16.1,
            feels_like=15.7,
            humidity=68,
            pressure=1015,
            weather=SimpleWeatherCondition(
                condition="clear",
                description="clear sky",
                icon="01d"
            ),
            wind_speed=2.8,
            wind_direction=190,
            cloudiness=20,
            visibility=10000,
            timestamp="2025-09-26T11:00:00Z"
        )
        
        mock_get_weather.return_value = mock_weather_data
        
        response = client.get("/api/v1/weather/current?lat=51.5074&lon=-0.1278")
        assert response.status_code == 200
        
        data = response.json()
        assert data["city"] == "London"
        assert data["temperature"] == 16.1
        assert data["weather"]["condition"] == "clear"
    
    def test_get_current_weather_missing_parameters(self):
        """Test current weather endpoint with missing parameters."""
        response = client.get("/api/v1/weather/current")
        assert response.status_code == 400
        
        data = response.json()
        assert "Either city name or both latitude and longitude must be provided" in data["message"]
    
    def test_get_current_weather_conflicting_parameters(self):
        """Test current weather endpoint with conflicting parameters."""
        response = client.get("/api/v1/weather/current?city=London&lat=51.5&lon=-0.12")
        assert response.status_code == 400
        
        data = response.json()
        assert "Cannot specify both city and coordinates" in data["message"]
    
    def test_get_current_weather_incomplete_coordinates(self):
        """Test current weather endpoint with incomplete coordinates."""
        response = client.get("/api/v1/weather/current?lat=51.5")
        assert response.status_code == 400
        
        data = response.json()
        assert "Both latitude and longitude must be provided" in data["message"]
    
    @patch('app.services.weather_service.weather_service.get_current_weather_by_city')
    def test_get_current_weather_invalid_location(self, mock_get_weather):
        """Test current weather endpoint with invalid location."""
        mock_get_weather.side_effect = InvalidLocationError("Location not found")
        
        response = client.get("/api/v1/weather/current?city=InvalidCity")
        assert response.status_code == 404
        
        data = response.json()
        assert data["message"] == "Location not found"
    
    @patch('app.services.weather_service.weather_service.get_current_weather_by_city')
    def test_get_current_weather_api_error(self, mock_get_weather):
        """Test current weather endpoint with API error."""
        mock_get_weather.side_effect = WeatherAPIError("API unavailable")
        
        response = client.get("/api/v1/weather/current?city=London")
        assert response.status_code == 503
        
        data = response.json()
        assert data["message"] == "Weather service temporarily unavailable"
    
    @patch('app.services.weather_service.weather_service.get_current_weather_by_city')
    def test_get_current_weather_api_key_error(self, mock_get_weather):
        """Test current weather endpoint with API key error."""
        mock_get_weather.side_effect = APIKeyError("Invalid API key")
        
        response = client.get("/api/v1/weather/current?city=London")
        assert response.status_code == 500
        
        data = response.json()
        assert data["message"] == "Weather service configuration error"
    
    @patch('app.services.weather_service.weather_service.get_forecast_by_city')
    def test_get_forecast_by_city_success(self, mock_get_forecast):
        """Test successful forecast retrieval by city."""
        from app.models import SimpleForecastDay
        
        mock_forecast_data = SimpleForecastResponse(
            city="London",
            country="GB",
            coordinates=Coord(lon=-0.1257, lat=51.5085),
            forecast_days=[
                SimpleForecastDay(
                    date="2025-09-26",
                    temperature_min=12.1,
                    temperature_max=18.7,
                    humidity=65,
                    weather=SimpleWeatherCondition(
                        condition="clear",
                        description="clear sky",
                        icon="01d"
                    ),
                    wind_speed=2.8,
                    precipitation_probability=0.0
                )
            ],
            generated_at="2025-09-26T10:30:00Z"
        )
        
        mock_get_forecast.return_value = mock_forecast_data
        
        response = client.get("/api/v1/weather/forecast?city=London&days=3")
        assert response.status_code == 200
        
        data = response.json()
        assert data["city"] == "London"
        assert len(data["forecast_days"]) == 1
        assert data["forecast_days"][0]["date"] == "2025-09-26"
    
    def test_get_forecast_invalid_days_parameter(self):
        """Test forecast endpoint with invalid days parameter."""
        response = client.get("/api/v1/weather/forecast?city=London&days=10")
        assert response.status_code == 422  # Validation error
    
    def test_get_forecast_negative_days_parameter(self):
        """Test forecast endpoint with negative days parameter."""
        response = client.get("/api/v1/weather/forecast?city=London&days=-1")
        assert response.status_code == 422  # Validation error
    
    @patch('app.services.weather_service.weather_service.check_api_health')
    def test_health_check_success(self, mock_health_check):
        """Test successful health check."""
        mock_health_check.return_value = True
        
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["weather_api_status"] == "healthy"
        assert "version" in data
        assert "timestamp" in data
    
    @patch('app.services.weather_service.weather_service.check_api_health')
    def test_health_check_degraded(self, mock_health_check):
        """Test health check with degraded status."""
        mock_health_check.return_value = False
        
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "degraded"
        assert data["weather_api_status"] == "unhealthy"
    
    @patch('app.services.weather_service.weather_service.check_api_health')
    def test_health_check_exception(self, mock_health_check):
        """Test health check with exception."""
        mock_health_check.side_effect = Exception("Health check failed")
        
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "unhealthy"
        assert data["weather_api_status"] == "unknown"
    
    def test_invalid_latitude(self):
        """Test endpoint with invalid latitude."""
        response = client.get("/api/v1/weather/current?lat=91&lon=0")
        assert response.status_code == 422  # Validation error
    
    def test_invalid_longitude(self):
        """Test endpoint with invalid longitude."""
        response = client.get("/api/v1/weather/current?lat=0&lon=181")
        assert response.status_code == 422  # Validation error
    
    def test_api_documentation_accessible(self):
        """Test that API documentation is accessible."""
        response = client.get("/docs")
        assert response.status_code == 200
        
        response = client.get("/redoc")
        assert response.status_code == 200
        
        response = client.get("/openapi.json")
        assert response.status_code == 200