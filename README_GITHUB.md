# Weather Forecast Microservice

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Killercoda](https://img.shields.io/badge/Killercoda-Compatible-orange.svg)](https://killercoda.com/)

A comprehensive, production-ready weather forecast microservice built with **Python 3.11** and **FastAPI**. This service provides current weather conditions and multi-day forecasts for locations worldwide, designed to run efficiently in Docker containers and optimized for **Killercoda** environments.

## 🌟 Features

- **🌤️ Current Weather**: Real-time weather conditions by city name or coordinates
- **📅 Weather Forecasts**: Up to 5-day weather forecasts with daily aggregations  
- **🌍 Multiple Location Formats**: Support for city names and geographic coordinates
- **💚 Health Monitoring**: Comprehensive health checks and service monitoring
- **⚡ Async Performance**: Fast, concurrent request handling with FastAPI
- **🛡️ Robust Error Handling**: Graceful error handling with detailed error responses
- **🐳 Docker Ready**: Optimized multi-stage Docker build with Docker Compose
- **🎯 Killercoda Compatible**: Runs on port 8080 with fast startup
- **📚 OpenAPI Documentation**: Interactive API documentation at `/docs`

## 🚀 Quick Start

### Prerequisites
1. **Python 3.11+** or **Docker**
2. **OpenWeatherMap API key** (free at [openweathermap.org](https://openweathermap.org/api))

### Option 1: Docker Compose (Recommended)
```bash
# Clone repository
git clone https://github.com/kr354f/weather_forecast.git
cd weather_forecast

# Set API key and start
export OPENWEATHERMAP_API_KEY="your_api_key_here"
docker-compose up -d
```

### Option 2: Python Direct
```bash
# Clone and setup
git clone https://github.com/kr354f/weather_forecast.git
cd weather_forecast

# Install and run
export OPENWEATHERMAP_API_KEY="your_api_key_here"
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

### Option 3: Killercoda One-liner
```bash
export OPENWEATHERMAP_API_KEY="your_key" && \
pip install -r requirements.txt && \
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

## 📋 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Service information |
| `/health` | GET | Simple health check |
| `/api/v1/health` | GET | Comprehensive health check |
| `/api/v1/weather/current` | GET | Current weather conditions |
| `/api/v1/weather/forecast` | GET | Multi-day weather forecast |
| `/docs` | GET | Interactive API documentation |

## 🧪 Testing the Service

```bash
# Health check
curl http://localhost:8080/health

# Current weather by city
curl "http://localhost:8080/api/v1/weather/current?city=London"

# Current weather by coordinates  
curl "http://localhost:8080/api/v1/weather/current?lat=51.5074&lon=-0.1278"

# 5-day forecast
curl "http://localhost:8080/api/v1/weather/forecast?city=Tokyo&days=5"

# Interactive documentation
open http://localhost:8080/docs
```

## 🐳 Docker Deployment Options

### Development Environment
```bash
# Start development with hot reload
docker-compose -f docker-compose.dev.yml up -d
```

### Production with Load Balancer
```bash
# Start production environment with nginx
docker-compose -f docker-compose.prod.yml --profile production up -d
```

### Manual Docker Build
```bash
docker build -t weather-forecast .
docker run -p 8080:8080 -e OPENWEATHERMAP_API_KEY="your_key" weather-forecast
```

## 📊 Running Tests

```bash
# Install test dependencies
pip install -r requirements.txt

# Run all tests
python run_tests.py --all

# Run specific test categories
python run_tests.py --unit      # Unit tests only
python run_tests.py --accuracy  # Accuracy tests only
python run_tests.py --load      # Include load tests

# Interactive demo
python demo.py
```

## 🏗️ Architecture

```
weather_forecast/
├── app/                       # Application source code
│   ├── main.py               # FastAPI application
│   ├── config.py             # Configuration management
│   ├── models.py             # Pydantic models
│   ├── routers/              # API endpoints
│   └── services/             # Business logic
├── tests/                    # Comprehensive test suite
├── docs/                     # API and deployment documentation
├── docker-compose*.yml       # Docker deployment configurations
└── Dockerfile               # Multi-stage Docker build
```

## 🌐 Cloud Deployment

The service supports deployment on all major cloud platforms:

- **AWS** (App Runner, ECS, Lambda)
- **Azure** (Container Instances, App Service, AKS)
- **Google Cloud** (Cloud Run, GKE, App Engine)
- **DigitalOcean, Heroku, Kubernetes**

See [`docs/deployment.md`](docs/deployment.md) for detailed cloud deployment instructions.

## 📚 Documentation

- **[API Documentation](docs/api.md)** - Comprehensive API reference with examples
- **[Deployment Guide](docs/deployment.md)** - Cloud deployment instructions
- **[Quick Start Guide](QUICK_START.md)** - Fast deployment reference
- **[Project Overview](DELIVERABLES.md)** - Complete project documentation

## 🔧 Configuration

Set environment variables:

```bash
export OPENWEATHERMAP_API_KEY="your_api_key_here"  # Required
export DEBUG="false"                                # Optional
export HOST="0.0.0.0"                              # Optional  
export PORT="8080"                                  # Optional
```

Or create a `.env` file:
```env
OPENWEATHERMAP_API_KEY=your_api_key_here
DEBUG=false
HOST=0.0.0.0
PORT=8080
```

## 🛡️ Security Features

- ✅ Input validation and sanitization
- ✅ Non-root user in containers  
- ✅ Minimal base images
- ✅ Secret management via environment variables
- ✅ CORS configuration for web integration

## 📈 Performance & Monitoring

- **Sub-second response times** for most requests
- **Concurrent request handling** (tested up to 50 concurrent users)
- **Built-in health checks** for monitoring
- **Structured logging** for debugging
- **Auto-scaling support** via containerization

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Run the test suite: `python run_tests.py --all`
5. Commit your changes: `git commit -am 'Add feature'`
6. Push to the branch: `git push origin feature-name`
7. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenWeatherMap** for providing the weather data API
- **FastAPI** for the excellent web framework
- **Pydantic** for data validation and serialization
- **Docker** for containerization capabilities

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/kr354f/weather_forecast/issues)
- **Documentation**: Available in the [`docs/`](docs/) directory
- **API Reference**: Interactive docs at `/docs` when service is running

---

**⭐ If you find this project useful, please give it a star on GitHub!**