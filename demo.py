#!/usr/bin/env python3
"""
Example script demonstrating how to use the Weather Forecast Microservice API.

This script shows how to make requests to the weather API endpoints and handle responses.
Make sure the weather service is running before executing this script.
"""

import asyncio
import httpx
import json
from datetime import datetime


# Configuration
BASE_URL = "http://localhost:8080"
TIMEOUT = 10.0


async def test_weather_api():
    """Test the weather API with various endpoints."""
    
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        
        print("🌤️  Weather Forecast Microservice - API Demo")
        print("=" * 50)
        
        # Test 1: Service Info
        print("\n1. Testing service info...")
        try:
            response = await client.get(f"{BASE_URL}/")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Service: {data['service']} v{data['version']}")
                print(f"   Status: {data['status']}")
            else:
                print(f"❌ Service info failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Service info error: {e}")
        
        # Test 2: Health Check
        print("\n2. Testing health check...")
        try:
            response = await client.get(f"{BASE_URL}/api/v1/health")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health: {data['status']}")
                print(f"   Weather API: {data['weather_api_status']}")
            else:
                print(f"❌ Health check failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Health check error: {e}")
        
        # Test 3: Current Weather by City
        print("\n3. Testing current weather by city...")
        cities = ["London", "Tokyo", "New York", "Sydney"]
        
        for city in cities:
            try:
                response = await client.get(
                    f"{BASE_URL}/api/v1/weather/current",
                    params={"city": city}
                )
                if response.status_code == 200:
                    data = response.json()
                    weather = data['weather']
                    print(f"✅ {data['city']}, {data['country']}: "
                          f"{data['temperature']}°C, {weather['description']}")
                else:
                    print(f"❌ {city} weather failed: {response.status_code}")
                    if response.status_code == 404:
                        print(f"   City not found")
                    elif response.status_code == 500:
                        print(f"   Server configuration error (check API key)")
            except Exception as e:
                print(f"❌ {city} weather error: {e}")
        
        # Test 4: Current Weather by Coordinates
        print("\n4. Testing current weather by coordinates...")
        locations = [
            (51.5074, -0.1278, "London"),
            (35.6762, 139.6503, "Tokyo"),
            (40.7128, -74.0060, "New York"),
        ]
        
        for lat, lon, name in locations:
            try:
                response = await client.get(
                    f"{BASE_URL}/api/v1/weather/current",
                    params={"lat": lat, "lon": lon}
                )
                if response.status_code == 200:
                    data = response.json()
                    weather = data['weather']
                    print(f"✅ {name} ({lat}, {lon}): "
                          f"{data['temperature']}°C, {weather['description']}")
                else:
                    print(f"❌ {name} coordinates weather failed: {response.status_code}")
            except Exception as e:
                print(f"❌ {name} coordinates weather error: {e}")
        
        # Test 5: Weather Forecast
        print("\n5. Testing weather forecast...")
        try:
            response = await client.get(
                f"{BASE_URL}/api/v1/weather/forecast",
                params={"city": "London", "days": 3}
            )
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 3-day forecast for {data['city']}, {data['country']}:")
                for day in data['forecast_days']:
                    weather = day['weather']
                    print(f"   {day['date']}: "
                          f"{day['temperature_min']}°C - {day['temperature_max']}°C, "
                          f"{weather['description']}")
            else:
                print(f"❌ Forecast failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Forecast error: {e}")
        
        # Test 6: Invalid Requests
        print("\n6. Testing error handling...")
        
        # Test invalid city
        try:
            response = await client.get(
                f"{BASE_URL}/api/v1/weather/current",
                params={"city": "NonExistentCity12345"}
            )
            if response.status_code == 404:
                print("✅ Invalid city properly handled (404)")
            else:
                print(f"❌ Invalid city handling unexpected: {response.status_code}")
        except Exception as e:
            print(f"❌ Invalid city test error: {e}")
        
        # Test missing parameters
        try:
            response = await client.get(f"{BASE_URL}/api/v1/weather/current")
            if response.status_code == 400:
                print("✅ Missing parameters properly handled (400)")
            else:
                print(f"❌ Missing parameters handling unexpected: {response.status_code}")
        except Exception as e:
            print(f"❌ Missing parameters test error: {e}")
        
        # Test conflicting parameters
        try:
            response = await client.get(
                f"{BASE_URL}/api/v1/weather/current",
                params={"city": "London", "lat": 51.5, "lon": -0.12}
            )
            if response.status_code == 400:
                print("✅ Conflicting parameters properly handled (400)")
            else:
                print(f"❌ Conflicting parameters handling unexpected: {response.status_code}")
        except Exception as e:
            print(f"❌ Conflicting parameters test error: {e}")
        
        print("\n" + "=" * 50)
        print("🎉 API Demo completed!")
        print("\n💡 Tips:")
        print("   - Visit http://localhost:8080/docs for interactive API documentation")
        print("   - Check http://localhost:8080/health for service status")
        print("   - Set OPENWEATHERMAP_API_KEY environment variable for full functionality")


async def test_specific_location():
    """Test a specific location with detailed output."""
    
    city = input("\n🌍 Enter a city name to test (or press Enter for London): ").strip()
    if not city:
        city = "London"
    
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        print(f"\n🔍 Testing weather for: {city}")
        print("-" * 30)
        
        # Current weather
        try:
            response = await client.get(
                f"{BASE_URL}/api/v1/weather/current",
                params={"city": city}
            )
            
            if response.status_code == 200:
                data = response.json()
                print("📍 Current Weather:")
                print(f"   Location: {data['city']}, {data['country']}")
                print(f"   Coordinates: {data['coordinates']['lat']}, {data['coordinates']['lon']}")
                print(f"   Temperature: {data['temperature']}°C (feels like {data['feels_like']}°C)")
                print(f"   Humidity: {data['humidity']}%")
                print(f"   Pressure: {data['pressure']} hPa")
                print(f"   Weather: {data['weather']['description']}")
                print(f"   Wind: {data['wind_speed']} m/s, {data['wind_direction']}°")
                print(f"   Cloudiness: {data['cloudiness']}%")
                print(f"   Visibility: {data['visibility']} m")
                print(f"   Updated: {data['timestamp']}")
            else:
                print(f"❌ Current weather failed: {response.status_code}")
                if response.status_code == 404:
                    print("   City not found. Try a different city name or add country code (e.g., 'London,UK')")
                return
        except Exception as e:
            print(f"❌ Current weather error: {e}")
            return
        
        # Forecast
        try:
            response = await client.get(
                f"{BASE_URL}/api/v1/weather/forecast",
                params={"city": city, "days": 5}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"\n📅 5-Day Forecast:")
                for day in data['forecast_days']:
                    print(f"   {day['date']}: {day['temperature_min']}°C - {day['temperature_max']}°C")
                    print(f"      {day['weather']['description']}, Wind: {day['wind_speed']} m/s")
                    print(f"      Humidity: {day['humidity']}%, Precipitation: {day['precipitation_probability']*100:.0f}%")
            else:
                print(f"❌ Forecast failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Forecast error: {e}")


if __name__ == "__main__":
    print("🚀 Starting Weather API Demo...")
    print(f"📡 Connecting to: {BASE_URL}")
    
    try:
        # Run the main demo
        asyncio.run(test_weather_api())
        
        # Interactive test
        while True:
            test_more = input("\n🤔 Would you like to test a specific location? (y/n): ").strip().lower()
            if test_more in ['y', 'yes']:
                asyncio.run(test_specific_location())
            else:
                break
                
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        print("\n🔧 Make sure the weather service is running:")
        print("   uvicorn app.main:app --host 0.0.0.0 --port 8080")
    
    print("\n🎯 Demo finished. Thank you!")