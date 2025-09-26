# Weather Forecast Microservice API Documentation

## Overview

The Weather Forecast Microservice provides comprehensive weather information through a RESTful API built with FastAPI. This service offers current weather conditions and multi-day forecasts for locations worldwide using the OpenWeatherMap API.

**Base URL**: `http://localhost:8080` (or your deployed service URL)  
**API Version**: v1  
**Authentication**: API Key (OpenWeatherMap)  
**Response Format**: JSON  
**Request Methods**: GET only  

## Quick Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Service information |
| `/health` | GET | Simple health check |
| `/api/v1/health` | GET | Comprehensive health check |
| `/api/v1/weather/current` | GET | Current weather conditions |
| `/api/v1/weather/forecast` | GET | Multi-day weather forecast |
| `/docs` | GET | Interactive API documentation |
| `/redoc` | GET | Alternative API documentation |

## Authentication

The service requires an OpenWeatherMap API key to function. Set the API key as an environment variable:

```bash
export OPENWEATHERMAP_API_KEY="your_api_key_here"
```

**Getting an API Key:**
1. Visit [OpenWeatherMap](https://openweathermap.org/api)
2. Sign up for a free account
3. Generate an API key from your account dashboard
4. The free tier includes 1,000 API calls per day

## API Endpoints

### 1. Service Information

Get basic information about the service.

**Endpoint**: `GET /`

**Response**:
```json
{
  "service": "Weather Forecast Microservice",
  "version": "1.0.0",
  "status": "running",
  "timestamp": "2025-09-26T10:30:00.000Z",
  "docs": "/docs",
  "health": "/api/v1/health"
}
```

### 2. Health Check (Simple)

Quick service availability check.

**Endpoint**: `GET /health`

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-09-26T10:30:00.000Z"
}
```

### 3. Health Check (Comprehensive)

Detailed service health including external API status.

**Endpoint**: `GET /api/v1/health`

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-09-26T10:30:00.000Z",
  "version": "1.0.0",
  "weather_api_status": "healthy"
}
```

**Status Values**:
- `healthy`: All systems operational
- `degraded`: Service running but weather API issues
- `unhealthy`: Service experiencing problems

### 4. Current Weather

Get current weather conditions for a specific location.

**Endpoint**: `GET /api/v1/weather/current`

#### Parameters

**Option 1: By City Name**
- `city` (string): City name, optionally with country code

**Option 2: By Coordinates**
- `lat` (float): Latitude (-90 to 90)
- `lon` (float): Longitude (-180 to 180)

#### Examples

**By City Name**:
```bash
GET /api/v1/weather/current?city=London
GET /api/v1/weather/current?city=London,UK
GET /api/v1/weather/current?city=New York,US
```

**By Coordinates**:
```bash
GET /api/v1/weather/current?lat=51.5074&lon=-0.1278
GET /api/v1/weather/current?lat=35.6762&lon=139.6503
```

#### Response

```json
{
  "city": "London",
  "country": "GB",
  "coordinates": {
    "lon": -0.1257,
    "lat": 51.5085
  },
  "temperature": 15.3,
  "feels_like": 14.8,
  "humidity": 72,
  "pressure": 1013,
  "weather": {
    "condition": "clouds",
    "description": "overcast clouds",
    "icon": "04d"
  },
  "wind_speed": 3.6,
  "wind_direction": 230,
  "cloudiness": 90,
  "visibility": 10000,
  "timestamp": "2025-09-26T10:30:00.000Z"
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `city` | string | City name |
| `country` | string | Country code (ISO 3166) |
| `coordinates` | object | Geographic coordinates |
| `coordinates.lat` | float | Latitude |
| `coordinates.lon` | float | Longitude |
| `temperature` | float | Current temperature (°C) |
| `feels_like` | float | Perceived temperature (°C) |
| `humidity` | integer | Humidity percentage (0-100) |
| `pressure` | integer | Atmospheric pressure (hPa) |
| `weather` | object | Weather conditions |
| `weather.condition` | string | Main weather condition |
| `weather.description` | string | Detailed description |
| `weather.icon` | string | Weather icon ID |
| `wind_speed` | float | Wind speed (m/s) |
| `wind_direction` | integer | Wind direction (degrees) |
| `cloudiness` | integer | Cloud coverage percentage |
| `visibility` | integer | Visibility (meters) |
| `timestamp` | string | Data timestamp (ISO 8601) |

### 5. Weather Forecast

Get multi-day weather forecast for a specific location.

**Endpoint**: `GET /api/v1/weather/forecast`

#### Parameters

**Location (choose one)**:
- `city` (string): City name, optionally with country code
- `lat` + `lon` (float): Geographic coordinates

**Forecast Length**:
- `days` (integer, optional): Number of forecast days (1-5, default: 3)

#### Examples

```bash
GET /api/v1/weather/forecast?city=Paris
GET /api/v1/weather/forecast?city=Tokyo&days=5
GET /api/v1/weather/forecast?lat=48.8566&lon=2.3522&days=3
```

#### Response

```json
{
  "city": "Paris",
  "country": "FR",
  "coordinates": {
    "lon": 2.3488,
    "lat": 48.8534
  },
  "forecast_days": [
    {
      "date": "2025-09-26",
      "temperature_min": 12.1,
      "temperature_max": 18.7,
      "humidity": 65,
      "weather": {
        "condition": "clear",
        "description": "clear sky",
        "icon": "01d"
      },
      "wind_speed": 2.8,
      "precipitation_probability": 0.0
    },
    {
      "date": "2025-09-27",
      "temperature_min": 14.2,
      "temperature_max": 20.1,
      "humidity": 58,
      "weather": {
        "condition": "clouds",
        "description": "few clouds",
        "icon": "02d"
      },
      "wind_speed": 3.2,
      "precipitation_probability": 0.15
    },
    {
      "date": "2025-09-28",
      "temperature_min": 11.8,
      "temperature_max": 17.9,
      "humidity": 78,
      "weather": {
        "condition": "rain",
        "description": "light rain",
        "icon": "10d"
      },
      "wind_speed": 4.1,
      "precipitation_probability": 0.82
    }
  ],
  "generated_at": "2025-09-26T10:30:00.000Z"
}
```

#### Forecast Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `city` | string | City name |
| `country` | string | Country code |
| `coordinates` | object | Geographic coordinates |
| `forecast_days` | array | Daily forecast entries |
| `forecast_days[].date` | string | Date (YYYY-MM-DD) |
| `forecast_days[].temperature_min` | float | Minimum temperature (°C) |
| `forecast_days[].temperature_max` | float | Maximum temperature (°C) |
| `forecast_days[].humidity` | integer | Average humidity (%) |
| `forecast_days[].weather` | object | Weather conditions |
| `forecast_days[].wind_speed` | float | Average wind speed (m/s) |
| `forecast_days[].precipitation_probability` | float | Precipitation chance (0-1) |
| `generated_at` | string | Response generation time |

## Error Handling

### HTTP Status Codes

| Code | Description | Cause |
|------|-------------|-------|
| 200 | OK | Request successful |
| 400 | Bad Request | Invalid parameters or missing required fields |
| 404 | Not Found | Location not found |
| 422 | Unprocessable Entity | Parameter validation error |
| 500 | Internal Server Error | Server configuration error |
| 503 | Service Unavailable | External weather API unavailable |

### Error Response Format

All errors return a consistent JSON structure:

```json
{
  "error": "ERROR_TYPE",
  "message": "Human-readable error description",
  "timestamp": "2025-09-26T10:30:00.000Z",
  "status_code": 400
}
```

### Common Error Types

#### 1. Invalid Parameters (400)

```json
{
  "error": "BAD_REQUEST",
  "message": "Cannot specify both city and coordinates",
  "timestamp": "2025-09-26T10:30:00.000Z",
  "status_code": 400
}
```

**Common causes**:
- Both city and coordinates provided
- Missing location parameters
- Incomplete coordinates (only lat or lon)

#### 2. Location Not Found (404)

```json
{
  "error": "NOT_FOUND",
  "message": "Location not found",
  "timestamp": "2025-09-26T10:30:00.000Z",
  "status_code": 404
}
```

**Solutions**:
- Check city name spelling
- Add country code (e.g., "London,UK")
- Verify coordinates are valid

#### 3. Validation Error (422)

```json
{
  "detail": [
    {
      "loc": ["query", "lat"],
      "msg": "ensure this value is greater than or equal to -90",
      "type": "value_error.number.not_ge",
      "ctx": {"limit_value": -90}
    }
  ]
}
```

#### 4. Service Configuration Error (500)

```json
{
  "error": "INTERNAL_SERVER_ERROR",
  "message": "Weather service configuration error",
  "timestamp": "2025-09-26T10:30:00.000Z",
  "status_code": 500
}
```

**Cause**: Missing or invalid OpenWeatherMap API key

#### 5. Service Unavailable (503)

```json
{
  "error": "SERVICE_UNAVAILABLE",
  "message": "Weather service temporarily unavailable",
  "timestamp": "2025-09-26T10:30:00.000Z",
  "status_code": 503
}
```

**Causes**:
- Network connectivity issues
- OpenWeatherMap API downtime
- Rate limit exceeded

## Rate Limiting

The service inherits rate limits from OpenWeatherMap:

- **Free Plan**: 1,000 calls/day, 60 calls/minute
- **Paid Plans**: Higher limits available

The service handles rate limits gracefully and returns appropriate error messages.

## Data Accuracy and Units

### Temperature
- **Unit**: Celsius (°C)
- **Precision**: 1 decimal place
- **Source**: OpenWeatherMap real-time data

### Wind
- **Speed Unit**: Meters per second (m/s)
- **Direction Unit**: Degrees (0-360, where 0° is North)

### Pressure
- **Unit**: Hectopascals (hPa)
- **Standard**: Sea level pressure

### Precipitation
- **Probability**: 0-1 scale (multiply by 100 for percentage)
- **Forecast**: Based on meteorological models

## Usage Examples

### cURL Examples

**Get current weather for London**:
```bash
curl "http://localhost:8080/api/v1/weather/current?city=London"
```

**Get 5-day forecast for Tokyo**:
```bash
curl "http://localhost:8080/api/v1/weather/forecast?city=Tokyo&days=5"
```

**Get weather by coordinates**:
```bash
curl "http://localhost:8080/api/v1/weather/current?lat=40.7128&lon=-74.0060"
```

**Check service health**:
```bash
curl "http://localhost:8080/api/v1/health"
```

### Python Examples

```python
import httpx
import asyncio

async def get_weather():
    async with httpx.AsyncClient() as client:
        # Current weather
        response = await client.get(
            "http://localhost:8080/api/v1/weather/current",
            params={"city": "London"}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"Temperature in {data['city']}: {data['temperature']}°C")
        
        # Forecast
        response = await client.get(
            "http://localhost:8080/api/v1/weather/forecast",
            params={"city": "Paris", "days": 3}
        )
        if response.status_code == 200:
            data = response.json()
            for day in data['forecast_days']:
                print(f"{day['date']}: {day['temperature_min']}°C - {day['temperature_max']}°C")

asyncio.run(get_weather())
```

### JavaScript Examples

```javascript
// Using fetch API
async function getCurrentWeather(city) {
    try {
        const response = await fetch(
            `http://localhost:8080/api/v1/weather/current?city=${encodeURIComponent(city)}`
        );
        
        if (response.ok) {
            const data = await response.json();
            console.log(`Temperature in ${data.city}: ${data.temperature}°C`);
            console.log(`Condition: ${data.weather.description}`);
        } else {
            const error = await response.json();
            console.error(`Error: ${error.message}`);
        }
    } catch (error) {
        console.error('Network error:', error);
    }
}

// Using axios
const axios = require('axios');

async function getForecast(city, days = 3) {
    try {
        const response = await axios.get('http://localhost:8080/api/v1/weather/forecast', {
            params: { city, days }
        });
        
        const forecast = response.data;
        console.log(`${days}-day forecast for ${forecast.city}:`);
        
        forecast.forecast_days.forEach(day => {
            console.log(`${day.date}: ${day.temperature_min}°C - ${day.temperature_max}°C`);
            console.log(`  ${day.weather.description}`);
        });
    } catch (error) {
        if (error.response) {
            console.error(`API Error: ${error.response.data.message}`);
        } else {
            console.error('Network error:', error.message);
        }
    }
}

// Usage
getCurrentWeather('London');
getForecast('Tokyo', 5);
```

## Interactive Documentation

The service provides interactive API documentation accessible at:

- **Swagger UI**: `http://localhost:8080/docs`
- **ReDoc**: `http://localhost:8080/redoc`
- **OpenAPI Schema**: `http://localhost:8080/openapi.json`

These interfaces allow you to:
- Explore all available endpoints
- Try API calls directly from the browser
- View request/response schemas
- Download the OpenAPI specification

## Best Practices

### 1. Error Handling
Always check HTTP status codes and handle errors appropriately:

```python
async def safe_weather_request(city):
    try:
        response = await client.get(f"/api/v1/weather/current?city={city}")
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            print(f"City '{city}' not found")
        elif response.status_code == 503:
            print("Weather service temporarily unavailable")
        else:
            print(f"Unexpected error: {response.status_code}")
            
    except Exception as e:
        print(f"Network error: {e}")
```

### 2. Rate Limiting
Implement client-side rate limiting to respect API limits:

```python
import asyncio

async def batch_weather_requests(cities):
    results = []
    for city in cities:
        result = await get_weather(city)
        results.append(result)
        await asyncio.sleep(1)  # Respect rate limits
    return results
```

### 3. Caching
Consider caching responses for better performance:

```python
import time
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_weather(city, timestamp_minutes):
    # Cache for 5-minute intervals
    return get_weather_sync(city)

def get_cached_weather(city):
    # Round timestamp to 5-minute intervals for caching
    cache_key = int(time.time() // 300)
    return cached_weather(city, cache_key)
```

### 4. Input Validation
Validate inputs before making API calls:

```python
import re

def validate_coordinates(lat, lon):
    return (-90 <= lat <= 90) and (-180 <= lon <= 180)

def validate_city_name(city):
    # Basic validation - adjust as needed
    return bool(re.match(r'^[a-zA-Z\s,.-]+$', city)) and len(city.strip()) > 0
```

## Troubleshooting

### Common Issues

1. **"Weather service configuration error"**
   - Ensure `OPENWEATHERMAP_API_KEY` environment variable is set
   - Verify API key is valid and active

2. **"Location not found"**
   - Check city name spelling
   - Try adding country code (e.g., "Springfield,US")
   - Use coordinates for precise locations

3. **"Service temporarily unavailable"**
   - Check internet connectivity
   - Verify OpenWeatherMap service status
   - Check if API key quota is exceeded

4. **Timeout errors**
   - Increase client timeout settings
   - Check network latency to the service
   - Verify service is running and responsive

### Health Monitoring

Monitor service health using the health endpoints:

```bash
# Quick health check
curl -f http://localhost:8080/health

# Detailed health check
curl http://localhost:8080/api/v1/health | jq .
```

Set up automated monitoring:

```bash
#!/bin/bash
# Simple health check script
while true; do
    if curl -f -s http://localhost:8080/health > /dev/null; then
        echo "$(date): Service healthy"
    else
        echo "$(date): Service unhealthy"
        # Send alert
    fi
    sleep 60
done
```

## API Versioning

The current API is version 1 (`/api/v1/`). Future versions will be introduced with new prefixes to maintain backward compatibility.

## Support

For issues and questions:
- Check the interactive documentation at `/docs`
- Review error messages for specific guidance
- Ensure API key is properly configured
- Verify input parameters match the expected format

## Changelog

### Version 1.0.0
- Initial API release
- Current weather and forecast endpoints
- Health monitoring
- Comprehensive error handling
- OpenAPI documentation