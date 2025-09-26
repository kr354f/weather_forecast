"""Weather API endpoints."""

from datetime import datetime, timezone
from typing import Union
from fastapi import APIRouter, Depends, Query, HTTPException, status
import logging

from app.models import (
    SimpleCurrentWeather,
    SimpleForecastResponse,
    HealthResponse,
    ErrorResponse,
    WeatherQueryParams,
    ForecastQueryParams
)
from app.services.weather_service import (
    WeatherService,
    get_weather_service,
    WeatherServiceError,
    WeatherAPIError,
    InvalidLocationError,
    APIKeyError
)
from app.config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["weather"])


@router.get(
    "/weather/current",
    response_model=SimpleCurrentWeather,
    summary="Get current weather",
    description="Get current weather conditions by city name or coordinates"
)
async def get_current_weather(
    city: str = Query(None, description="City name (e.g., 'London' or 'London,UK')"),
    lat: float = Query(None, description="Latitude (-90 to 90)", ge=-90, le=90),
    lon: float = Query(None, description="Longitude (-180 to 180)", ge=-180, le=180),
    weather_service: WeatherService = Depends(get_weather_service)
):
    """
    Get current weather conditions for a specified location.
    
    You can specify the location using either:
    - City name: `?city=London` or `?city=London,UK`
    - Coordinates: `?lat=51.5074&lon=-0.1278`
    
    The API returns current temperature, humidity, weather conditions, and more.
    """
    try:
        # Validate input parameters
        if city and (lat is not None or lon is not None):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot specify both city and coordinates"
            )
        
        # Check for incomplete coordinates first
        if (lat is None) != (lon is None):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Both latitude and longitude must be provided"
            )
        
        # Check if neither city nor coordinates are provided
        if not city and lat is None and lon is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either city name or both latitude and longitude must be provided"
            )
        
        # Fetch weather data
        if city:
            logger.info(f"Fetching current weather for city: {city}")
            weather_data = await weather_service.get_current_weather_by_city(city)
        else:
            logger.info(f"Fetching current weather for coordinates: {lat}, {lon}")
            weather_data = await weather_service.get_current_weather_by_coordinates(lat, lon)
        
        return weather_data
    
    except APIKeyError as e:
        logger.error(f"API key error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Weather service configuration error"
        )
    
    except InvalidLocationError as e:
        logger.warning(f"Invalid location requested: {city or f'{lat},{lon}'}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found"
        )
    
    except WeatherAPIError as e:
        logger.error(f"Weather API error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Weather service temporarily unavailable"
        )
    
    except HTTPException:
        # Re-raise HTTPExceptions (like validation errors) without modification
        raise
    
    except Exception as e:
        logger.error(f"Unexpected error in get_current_weather: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get(
    "/weather/forecast",
    response_model=SimpleForecastResponse,
    summary="Get weather forecast",
    description="Get multi-day weather forecast by city name or coordinates"
)
async def get_weather_forecast(
    city: str = Query(None, description="City name (e.g., 'London' or 'London,UK')"),
    lat: float = Query(None, description="Latitude (-90 to 90)", ge=-90, le=90),
    lon: float = Query(None, description="Longitude (-180 to 180)", ge=-180, le=180),
    days: int = Query(3, description="Number of forecast days (1-5)", ge=1, le=5),
    weather_service: WeatherService = Depends(get_weather_service)
):
    """
    Get weather forecast for the next few days for a specified location.
    
    You can specify the location using either:
    - City name: `?city=London` or `?city=London,UK`
    - Coordinates: `?lat=51.5074&lon=-0.1278`
    
    You can also specify the number of forecast days (1-5, default is 3).
    
    The API returns daily forecasts with temperature ranges, weather conditions, and precipitation probability.
    """
    try:
        # Validate input parameters
        if city and (lat is not None or lon is not None):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot specify both city and coordinates"
            )
        
        if not city and (lat is None or lon is None):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either city name or both latitude and longitude must be provided"
            )
        
        if (lat is None) != (lon is None):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Both latitude and longitude must be provided for coordinate-based queries"
            )
        
        # Fetch forecast data
        if city:
            logger.info(f"Fetching {days}-day forecast for city: {city}")
            forecast_data = await weather_service.get_forecast_by_city(city, days)
        else:
            logger.info(f"Fetching {days}-day forecast for coordinates: {lat}, {lon}")
            forecast_data = await weather_service.get_forecast_by_coordinates(lat, lon, days)
        
        return forecast_data
    
    except APIKeyError as e:
        logger.error(f"API key error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Weather service configuration error"
        )
    
    except InvalidLocationError as e:
        logger.warning(f"Invalid location requested: {city or f'{lat},{lon}'}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found"
        )
    
    except WeatherAPIError as e:
        logger.error(f"Weather API error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Weather service temporarily unavailable"
        )
    
    except HTTPException:
        # Re-raise HTTPExceptions (like validation errors) without modification
        raise
    
    except Exception as e:
        logger.error(f"Unexpected error in get_weather_forecast: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Check the health status of the weather service"
)
async def health_check(
    weather_service: WeatherService = Depends(get_weather_service)
):
    """
    Perform a health check of the weather service.
    
    This endpoint checks:
    - Service availability
    - External weather API connectivity
    - Overall system status
    
    Returns the service status and version information.
    """
    try:
        settings = get_settings()
        
        # Check external API health
        api_healthy = await weather_service.check_api_health()
        weather_api_status = "healthy" if api_healthy else "unhealthy"
        
        # Determine overall status
        overall_status = "healthy" if api_healthy else "degraded"
        
        logger.info(f"Health check completed: {overall_status}")
        
        return HealthResponse(
            status=overall_status,
            timestamp=datetime.now(timezone.utc),
            version=settings.app_version,
            weather_api_status=weather_api_status
        )
    
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        
        return HealthResponse(
            status="unhealthy",
            timestamp=datetime.now(timezone.utc),
            version=get_settings().app_version,
            weather_api_status="unknown"
        )