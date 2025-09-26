# Quick Deployment Guide

## 🚀 Killercoda Deployment (Choose One)

### Option 1: Python Direct (Fastest - ~30 seconds)
```bash
export OPENWEATHERMAP_API_KEY="your_api_key_here"
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

### Option 2: Docker Compose (Recommended - ~60 seconds)
```bash
export OPENWEATHERMAP_API_KEY="your_api_key_here"
docker-compose up -d
```

### Option 3: Docker Manual Build (~90 seconds)
```bash
docker build -t weather-forecast .
docker run -p 8080:8080 -e OPENWEATHERMAP_API_KEY="your_api_key_here" weather-forecast
```

## 🧪 Quick Test Commands

```bash
# Health check
curl http://localhost:8080/health

# Current weather
curl "http://localhost:8080/api/v1/weather/current?city=London"

# 5-day forecast
curl "http://localhost:8080/api/v1/weather/forecast?city=Tokyo&days=5"

# Interactive documentation
echo "Open: http://localhost:8080/docs"
```

## 🔑 Getting API Key

1. Visit: https://openweathermap.org/api
2. Sign up for free account
3. Generate API key from dashboard
4. Use the key in deployment commands above

## 📚 Available Endpoints

- `GET /` - Service info
- `GET /health` - Health check  
- `GET /api/v1/health` - Detailed health check
- `GET /api/v1/weather/current?city=London` - Current weather by city
- `GET /api/v1/weather/current?lat=51.5&lon=-0.12` - Current weather by coordinates
- `GET /api/v1/weather/forecast?city=Paris&days=3` - Weather forecast
- `GET /docs` - Interactive API documentation

## 🛠️ Development Commands

```bash
# Start development environment
docker-compose -f docker-compose.dev.yml up -d

# Run tests
python run_tests.py --all

# Run demo
python demo.py

# Load testing
python tests/load_test.py --test all
```

## 📦 Production Deployment

```bash
# Production with scaling
docker-compose -f docker-compose.prod.yml --profile production up -d

# Scale API instances
docker-compose -f docker-compose.prod.yml up -d --scale weather-api=5
```

## 🔧 Troubleshooting

**Service not starting?**
- Check API key is set: `echo $OPENWEATHERMAP_API_KEY`
- Verify port 8080 is available: `netstat -an | grep 8080`

**API errors?**
- Check API key is valid at OpenWeatherMap
- Verify internet connectivity
- Check service logs: `docker-compose logs weather-api`

**Need help?**
- Check `/docs` for interactive API documentation
- Review `README.md` for detailed instructions
- Run health check: `curl http://localhost:8080/health`