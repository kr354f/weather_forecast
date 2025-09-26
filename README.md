# Weather Forecast Microservice

A comprehensive, production-ready weather forecast microservice built with **Python 3.11** and **FastAPI**. This service provides current weather conditions and multi-day forecasts for locations worldwide, designed to run efficiently in Docker containers and optimized for **Killercoda** environments.

## 🌟 Features

- **Current Weather**: Real-time weather conditions by city name or coordinates
- **Weather Forecasts**: Up to 5-day weather forecasts with daily aggregations
- **Multiple Location Formats**: Support for city names (`London`, `London,UK`) and geographic coordinates
- **Health Monitoring**: Comprehensive health checks and service monitoring
- **Async Performance**: Fast, concurrent request handling with FastAPI
- **Robust Error Handling**: Graceful error handling with detailed error responses
- **Docker Ready**: Optimized multi-stage Docker build
- **Killercoda Compatible**: Runs on port 8080 with fast startup
- **OpenAPI Documentation**: Interactive API documentation at `/docs`

## 📋 API Endpoints

### Current Weather
```
GET /api/v1/weather/current?city=London
GET /api/v1/weather/current?lat=51.5&lon=-0.12
```

### Weather Forecast
```
GET /api/v1/weather/forecast?city=London&days=3
GET /api/v1/weather/forecast?lat=51.5&lon=-0.12&days=5
```

### Health Check
```
GET /api/v1/health
GET /health
```

### Service Info
```
GET /
```

## 🚀 Quick Start

### Prerequisites

1. **Python 3.11+** installed
2. **OpenWeatherMap API Key** (free at [openweathermap.org](https://openweathermap.org/api))
3. **Docker** (optional, for containerized deployment)

### Method 1: Direct Python Execution

1. **Clone and Navigate**
   ```bash
   cd weather_forecast
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set API Key**
   ```bash
   # Linux/MacOS
   export OPENWEATHERMAP_API_KEY="your_api_key_here"
   
   # Windows PowerShell
   $env:OPENWEATHERMAP_API_KEY="your_api_key_here"
   
   # Windows CMD
   set OPENWEATHERMAP_API_KEY=your_api_key_here
   ```

4. **Run the Service**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8080
   ```

### Method 2: Docker Deployment

#### Option A: Docker Compose (Recommended)

1. **Production Deployment**
   ```bash
   # Set API key
   export OPENWEATHERMAP_API_KEY="your_api_key_here"
   
   # Start with Docker Compose
   docker-compose up -d
   ```

2. **Development with Hot Reload**
   ```bash
   # Start development environment
   docker-compose -f docker-compose.dev.yml up -d
   ```

3. **Production with Load Balancer**
   ```bash
   # Start with nginx load balancer
   docker-compose -f docker-compose.prod.yml --profile production up -d
   ```

#### Option B: Manual Docker Build

1. **Build Docker Image**
   ```bash
   docker build -t weather-forecast .
   ```

2. **Run Container**
   ```bash
   docker run -d \
     -p 8080:8080 \
     -e OPENWEATHERMAP_API_KEY="your_api_key_here" \
     --name weather-service \
     weather-forecast
   ```

### Method 3: Killercoda Deployment

For Killercoda environments, choose the method that works best:

#### Option A: Direct Python (Fastest Startup)
```bash
# Set API key and start service
export OPENWEATHERMAP_API_KEY="your_api_key_here" && \
pip install -r requirements.txt && \
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

#### Option B: Docker Compose (Recommended for Production Demo)
```bash
# Set API key and start with Docker Compose
export OPENWEATHERMAP_API_KEY="your_api_key_here" && \
docker-compose up -d
```

#### Option C: Manual Docker (Container Demo)
```bash
# Build and run manually
docker build -t weather-forecast . && \
docker run -p 8080:8080 -e OPENWEATHERMAP_API_KEY="your_api_key_here" weather-forecast
```

**Killercoda Compatibility Features:**
- ✅ Runs on port 8080 as required
- ✅ Fast startup (< 30 seconds with Python, < 60 seconds with Docker)
- ✅ No external dependencies beyond API key
- ✅ Works with both pip and Docker deployment
- ✅ Immediate health check availability
- ✅ Interactive documentation at `/docs`

## 📚 API Usage Examples

### Get Current Weather by City
```bash
curl "http://localhost:8080/api/v1/weather/current?city=London"
```

**Response:**
```json
{
  "city": "London",
  "country": "GB",
  "coordinates": {"lon": -0.1257, "lat": 51.5085},
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
  "timestamp": "2025-09-26T10:30:00Z"
}
```

### Get Weather by Coordinates
```bash
curl "http://localhost:8080/api/v1/weather/current?lat=51.5074&lon=-0.1278"
```

### Get 3-Day Forecast
```bash
curl "http://localhost:8080/api/v1/weather/forecast?city=Paris&days=3"
```

**Response:**
```json
{
  "city": "Paris",
  "country": "FR",
  "coordinates": {"lon": 2.3488, "lat": 48.8534},
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
    }
  ],
  "generated_at": "2025-09-26T10:30:00Z"
}
```

### Health Check
```bash
curl "http://localhost:8080/api/v1/health"
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-09-26T10:30:00Z",
  "version": "1.0.0",
  "weather_api_status": "healthy"
}
```

## 🏗️ Architecture

```
weather_forecast/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application & middleware
│   ├── config.py                  # Configuration management
│   ├── models.py                  # Pydantic models & schemas
│   ├── routers/
│   │   ├── __init__.py
│   │   └── weather.py             # Weather API endpoints
│   └── services/
│       ├── __init__.py
│       └── weather_service.py     # OpenWeatherMap integration
├── docs/
│   ├── api.md                     # Comprehensive API documentation
│   └── deployment.md              # Cloud deployment guides
├── tests/
│   ├── __init__.py
│   ├── test_weather_service.py    # Unit tests - service layer
│   ├── test_api.py                # Unit tests - API endpoints
│   ├── test_accuracy_reliability.py # Accuracy & reliability tests
│   └── load_test.py               # Performance & load tests
├── docker-compose.yml             # Production Docker Compose
├── docker-compose.dev.yml         # Development Docker Compose
├── docker-compose.prod.yml        # Production with load balancer
├── nginx.conf                     # Nginx configuration for production
├── Dockerfile                     # Multi-stage Docker build
├── .dockerignore                  # Docker ignore rules
├── .env.example                   # Environment variables template
├── requirements.txt               # Python dependencies
├── pytest.ini                    # Test configuration
├── demo.py                        # Interactive demonstration
├── run_tests.py                   # Comprehensive test runner
├── DELIVERABLES.md                # Complete project overview
└── README.md                      # This file
```

## ⚙️ Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENWEATHERMAP_API_KEY` | **Yes** | - | Your OpenWeatherMap API key |
| `DEBUG` | No | `false` | Enable debug mode |
| `HOST` | No | `0.0.0.0` | Server host |
| `PORT` | No | `8080` | Server port |
| `REQUEST_TIMEOUT` | No | `10` | API request timeout (seconds) |

### Configuration File

Create a `.env` file in the root directory:

```env
OPENWEATHERMAP_API_KEY=your_api_key_here
DEBUG=false
HOST=0.0.0.0
PORT=8080
REQUEST_TIMEOUT=10
```

## 🔍 Monitoring & Logging

### Health Endpoints

- `/health` - Simple health check
- `/api/v1/health` - Comprehensive health check with external API status

### Logging

The service provides structured logging with:
- Request/response logging
- Performance metrics
- Error tracking
- External API status

### Metrics

Access built-in metrics at:
- Service uptime and version info at `/`
- Detailed health status at `/api/v1/health`

## 🐳 Docker Details

### Multi-Stage Build

The Dockerfile uses a multi-stage build for optimization:

1. **Builder Stage**: Installs build dependencies and Python packages
2. **Production Stage**: Contains only runtime dependencies and application code

### Security Features

- Non-root user execution
- Minimal base image (Python 3.11 slim)
- Health checks included
- Optimized layer caching

### Docker Compose Files

The project includes three Docker Compose configurations:

- **`docker-compose.yml`** - Production deployment (Killercoda compatible)
- **`docker-compose.dev.yml`** - Development with hot reload
- **`docker-compose.prod.yml`** - Production with load balancer and scaling

See the [Docker Compose Configurations](#-docker-compose-configurations) section for detailed usage instructions.

Quick start:
```bash
export OPENWEATHERMAP_API_KEY="your_key"
docker-compose up -d
```

## 🐳 Docker Compose Configurations

The project includes multiple Docker Compose configurations for different use cases:

### 📦 Production (`docker-compose.yml`)
**Best for**: Production deployments, Killercoda demos

```bash
# Start production service
export OPENWEATHERMAP_API_KEY="your_key"
docker-compose up -d

# View logs
docker-compose logs -f

# Stop service
docker-compose down
```

**Features:**
- Single container deployment
- Port 8080 (Killercoda compatible)
- Health checks enabled
- Automatic restart on failure
- Environment variable configuration

### 🛠️ Development (`docker-compose.dev.yml`)
**Best for**: Local development with hot reload

```bash
# Start development environment
export OPENWEATHERMAP_API_KEY="your_key"
docker-compose -f docker-compose.dev.yml up -d

# Run tests in separate container
docker-compose -f docker-compose.dev.yml --profile testing run test-runner python run_tests.py
```

**Features:**
- Hot reload for code changes
- Volume mounts for source code
- Debug mode enabled
- Separate test runner container

### 🚀 Production with Load Balancer (`docker-compose.prod.yml`)
**Best for**: Scalable production deployments

```bash
# Start with nginx load balancer
export OPENWEATHERMAP_API_KEY="your_key"
docker-compose -f docker-compose.prod.yml --profile production up -d
```

**Features:**
- Multiple API replicas (3 instances)
- Nginx load balancer
- Resource limits and reservations
- Rolling updates
- Production-grade configuration

### 🔧 Docker Compose Commands

```bash
# Build and start
docker-compose up --build -d

# Scale service (production only)
docker-compose -f docker-compose.prod.yml up -d --scale weather-api=5

# View service status
docker-compose ps

# View logs
docker-compose logs weather-api

# Restart service
docker-compose restart weather-api

# Clean up everything
docker-compose down -v --remove-orphans
```

## 🧪 Testing

### Manual Testing

1. **Start the service** (see Quick Start)

2. **Test endpoints**:
   ```bash
   # Health check
   curl http://localhost:8080/health
   
   # Current weather
   curl "http://localhost:8080/api/v1/weather/current?city=London"
   
   # Forecast
   curl "http://localhost:8080/api/v1/weather/forecast?city=Tokyo&days=5"
   ```

3. **Interactive documentation**: Visit `http://localhost:8080/docs`

### Unit Tests

Run the included unit tests:

```bash
# Install test dependencies
pip install pytest httpx pytest-asyncio

# Run tests
python -m pytest tests/ -v
```

## 🚨 Error Handling

The service provides comprehensive error handling:

### HTTP Status Codes

- `200` - Success
- `400` - Bad Request (invalid parameters)
- `404` - Not Found (invalid location)
- `500` - Internal Server Error
- `503` - Service Unavailable (weather API down)

### Error Response Format

```json
{
  "error": "INVALID_LOCATION",
  "message": "Location not found",
  "timestamp": "2025-09-26T10:30:00Z",
  "status_code": 404
}
```

### Common Error Scenarios

1. **Missing API Key**: Service returns configuration error
2. **Invalid Location**: Returns 404 with location not found message
3. **API Rate Limit**: Returns 503 with service unavailable message
4. **Network Issues**: Handled gracefully with timeout and retry logic

## 🔧 Troubleshooting

### Common Issues

1. **"Weather service configuration error"**
   - Check that `OPENWEATHERMAP_API_KEY` is set
   - Verify the API key is valid

2. **"Location not found"**
   - Check spelling of city name
   - Try adding country code: `London,UK`
   - Verify coordinates are valid (-90 to 90 for lat, -180 to 180 for lon)

3. **"Service temporarily unavailable"**
   - Check internet connection
   - Verify OpenWeatherMap API status
   - Check if API key has remaining quota

4. **Slow responses**
   - Check network latency to OpenWeatherMap API
   - Consider implementing caching (future enhancement)

### Debug Mode

Enable debug mode for detailed logging:

```bash
export DEBUG=true
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

## 📋 Killercoda Compatibility

This service is specifically designed for Killercoda environments with multiple deployment options:

### Requirements Met

✅ **Port 8080**: Service runs on the required port  
✅ **Fast Startup**: Optimized for quick initialization (< 60 seconds)  
✅ **Pip Installation**: Works with standard pip install command  
✅ **Docker Support**: Full Docker and Docker Compose support  
✅ **No External Dependencies**: Only requires pip/Docker and API key  
✅ **Environment Variables**: API key injection via env vars  
✅ **Interactive Documentation**: Available immediately at `/docs`  

### Killercoda Deployment Options

#### 🚀 Fastest Startup (< 30 seconds)
```bash
export OPENWEATHERMAP_API_KEY="your_key" && \
pip install -r requirements.txt && \
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

#### 🐳 Docker Compose (Recommended)
```bash
export OPENWEATHERMAP_API_KEY="your_key" && \
docker-compose up -d
```

#### 📦 Manual Docker Build
```bash
docker build -t weather-api . && \
docker run -p 8080:8080 -e OPENWEATHERMAP_API_KEY="your_key" weather-api
```

### Testing in Killercoda

Once deployed, test the service immediately:
```bash
# Health check
curl http://localhost:8080/health

# Get weather
curl "http://localhost:8080/api/v1/weather/current?city=London"

# Interactive docs
echo "Visit: http://localhost:8080/docs"
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **OpenWeatherMap** for providing the weather data API
- **FastAPI** for the excellent web framework
- **Pydantic** for data validation and serialization
- **Uvicorn** for ASGI server implementation

---

**Made with ❤️ for weather enthusiasts and developers**

For questions or support, please open an issue in the repository.