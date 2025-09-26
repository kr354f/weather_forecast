# Cloud Deployment Guide

This guide provides detailed instructions for deploying the Weather Forecast Microservice on major cloud platforms.

## Table of Contents

- [AWS Deployment](#aws-deployment)
- [Azure Deployment](#azure-deployment)
- [Google Cloud Platform](#google-cloud-platform)
- [DigitalOcean](#digitalocean)
- [Heroku](#heroku)
- [Kubernetes Deployment](#kubernetes-deployment)
- [Docker Swarm](#docker-swarm)
- [Cost Optimization](#cost-optimization)
- [Monitoring & Scaling](#monitoring--scaling)

## AWS Deployment

### Method 1: AWS App Runner (Recommended for Simplicity)

AWS App Runner is the easiest way to deploy containerized applications.

#### Prerequisites
- AWS CLI installed and configured
- Docker installed locally
- OpenWeatherMap API key

#### Step 1: Push to Container Registry

```bash
# Build and tag the image
docker build -t weather-forecast .

# Create ECR repository
aws ecr create-repository --repository-name weather-forecast

# Get login token
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com

# Tag for ECR
docker tag weather-forecast:latest 123456789012.dkr.ecr.us-east-1.amazonaws.com/weather-forecast:latest

# Push to ECR
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/weather-forecast:latest
```

#### Step 2: Create App Runner Service

```bash
# Create apprunner.yaml
cat > apprunner.yaml << EOF
version: 1.0
runtime: docker
build:
  commands:
    build:
      - echo "No build commands - using pre-built image"
run:
  runtime-version: latest
  command: uvicorn app.main:app --host 0.0.0.0 --port 8080
  network:
    port: 8080
    env:
      OPENWEATHERMAP_API_KEY: \${OPENWEATHERMAP_API_KEY}
  env:
    - name: OPENWEATHERMAP_API_KEY
      value: "your_api_key_here"
EOF

# Create service using AWS CLI
aws apprunner create-service \
  --service-name weather-forecast \
  --source-configuration '{
    "ImageRepository": {
      "ImageIdentifier": "123456789012.dkr.ecr.us-east-1.amazonaws.com/weather-forecast:latest",
      "ImageConfiguration": {
        "Port": "8080",
        "RuntimeEnvironmentVariables": {
          "OPENWEATHERMAP_API_KEY": "your_api_key_here"
        }
      },
      "ImageRepositoryType": "ECR"
    },
    "AutoDeploymentsEnabled": true
  }' \
  --instance-configuration '{
    "Cpu": "0.25 vCPU",
    "Memory": "0.5 GB"
  }'
```

### Method 2: AWS ECS with Fargate

For more control and scalability, use ECS with Fargate.

#### Step 1: Create Task Definition

```json
{
  "family": "weather-forecast-task",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "executionRoleArn": "arn:aws:iam::123456789012:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "weather-forecast",
      "image": "123456789012.dkr.ecr.us-east-1.amazonaws.com/weather-forecast:latest",
      "portMappings": [
        {
          "containerPort": 8080,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "OPENWEATHERMAP_API_KEY",
          "value": "your_api_key_here"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/weather-forecast",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

#### Step 2: Create ECS Service

```bash
# Create cluster
aws ecs create-cluster --cluster-name weather-forecast-cluster

# Register task definition
aws ecs register-task-definition --cli-input-json file://task-definition.json

# Create service
aws ecs create-service \
  --cluster weather-forecast-cluster \
  --service-name weather-forecast-service \
  --task-definition weather-forecast-task:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-12345678,subnet-87654321],securityGroups=[sg-12345678],assignPublicIp=ENABLED}"
```

### Method 3: AWS Lambda with Mangum

For serverless deployment, use AWS Lambda with the Mangum adapter.

#### Step 1: Modify for Lambda

```python
# lambda_handler.py
from mangum import Mangum
from app.main import app

handler = Mangum(app)
```

#### Step 2: Deploy with SAM

```yaml
# template.yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Globals:
  Function:
    Timeout: 30
    MemorySize: 512
    Runtime: python3.11

Resources:
  WeatherForecastFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: .
      Handler: lambda_handler.handler
      Environment:
        Variables:
          OPENWEATHERMAP_API_KEY: !Ref OpenWeatherMapApiKey
      Events:
        WeatherApi:
          Type: Api
          Properties:
            Path: /{proxy+}
            Method: ANY

Parameters:
  OpenWeatherMapApiKey:
    Type: String
    Description: OpenWeatherMap API Key
    NoEcho: true

Outputs:
  WeatherForecastApi:
    Description: "API Gateway endpoint URL"
    Value: !Sub "https://${ServerlessRestApi}.execute-api.${AWS::Region}.amazonaws.com/Prod/"
```

```bash
# Deploy with SAM
sam build
sam deploy --guided
```

## Azure Deployment

### Method 1: Azure Container Instances (ACI)

Simple container deployment for development and testing.

```bash
# Login to Azure
az login

# Create resource group
az group create --name weather-forecast-rg --location eastus

# Create container registry
az acr create --resource-group weather-forecast-rg --name weatherforecastacr --sku Basic

# Login to ACR
az acr login --name weatherforecastacr

# Build and push image
docker build -t weather-forecast .
docker tag weather-forecast weatherforecastacr.azurecr.io/weather-forecast:latest
docker push weatherforecastacr.azurecr.io/weather-forecast:latest

# Create container instance
az container create \
  --resource-group weather-forecast-rg \
  --name weather-forecast-container \
  --image weatherforecastacr.azurecr.io/weather-forecast:latest \
  --registry-login-server weatherforecastacr.azurecr.io \
  --registry-username $(az acr credential show --name weatherforecastacr --query username -o tsv) \
  --registry-password $(az acr credential show --name weatherforecastacr --query passwords[0].value -o tsv) \
  --dns-name-label weather-forecast-api \
  --ports 8080 \
  --environment-variables OPENWEATHERMAP_API_KEY=your_api_key_here \
  --cpu 1 \
  --memory 1
```

### Method 2: Azure App Service

For production workloads with auto-scaling and management features.

```bash
# Create App Service plan
az appservice plan create \
  --name weather-forecast-plan \
  --resource-group weather-forecast-rg \
  --sku B1 \
  --is-linux

# Create web app
az webapp create \
  --resource-group weather-forecast-rg \
  --plan weather-forecast-plan \
  --name weather-forecast-webapp \
  --deployment-container-image-name weatherforecastacr.azurecr.io/weather-forecast:latest

# Configure container registry
az webapp config container set \
  --name weather-forecast-webapp \
  --resource-group weather-forecast-rg \
  --docker-custom-image-name weatherforecastacr.azurecr.io/weather-forecast:latest \
  --docker-registry-server-url https://weatherforecastacr.azurecr.io \
  --docker-registry-server-user $(az acr credential show --name weatherforecastacr --query username -o tsv) \
  --docker-registry-server-password $(az acr credential show --name weatherforecastacr --query passwords[0].value -o tsv)

# Set environment variables
az webapp config appsettings set \
  --resource-group weather-forecast-rg \
  --name weather-forecast-webapp \
  --settings OPENWEATHERMAP_API_KEY=your_api_key_here WEBSITES_PORT=8080
```

### Method 3: Azure Kubernetes Service (AKS)

For scalable production deployments.

```bash
# Create AKS cluster
az aks create \
  --resource-group weather-forecast-rg \
  --name weather-forecast-aks \
  --node-count 2 \
  --enable-addons monitoring \
  --generate-ssh-keys

# Get credentials
az aks get-credentials --resource-group weather-forecast-rg --name weather-forecast-aks

# Apply Kubernetes manifests (see Kubernetes section below)
kubectl apply -f k8s/
```

## Google Cloud Platform

### Method 1: Cloud Run (Recommended)

Google Cloud Run is perfect for containerized microservices.

```bash
# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Build and push to Container Registry
docker build -t gcr.io/PROJECT_ID/weather-forecast .
docker push gcr.io/PROJECT_ID/weather-forecast

# Deploy to Cloud Run
gcloud run deploy weather-forecast \
  --image gcr.io/PROJECT_ID/weather-forecast \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --set-env-vars OPENWEATHERMAP_API_KEY=your_api_key_here \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10
```

### Method 2: Google Kubernetes Engine (GKE)

```bash
# Create GKE cluster
gcloud container clusters create weather-forecast-cluster \
  --num-nodes 2 \
  --machine-type e2-medium \
  --zone us-central1-a

# Get credentials
gcloud container clusters get-credentials weather-forecast-cluster --zone us-central1-a

# Apply Kubernetes manifests
kubectl apply -f k8s/
```

### Method 3: App Engine

```yaml
# app.yaml
runtime: custom
env: flex

automatic_scaling:
  min_num_instances: 1
  max_num_instances: 10
  cool_down_period_sec: 120
  cpu_utilization:
    target_utilization: 0.6

env_variables:
  OPENWEATHERMAP_API_KEY: "your_api_key_here"

resources:
  cpu: 1
  memory_gb: 0.5
  disk_size_gb: 10
```

```bash
# Deploy to App Engine
gcloud app deploy
```

## DigitalOcean

### Method 1: DigitalOcean App Platform

```yaml
# .do/app.yaml
name: weather-forecast
services:
- name: api
  source_dir: /
  github:
    repo: your-username/weather-forecast
    branch: main
  run_command: uvicorn app.main:app --host 0.0.0.0 --port 8080
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: OPENWEATHERMAP_API_KEY
    value: your_api_key_here
  http_port: 8080
  health_check:
    http_path: /health
```

```bash
# Deploy using doctl
doctl apps create .do/app.yaml
```

### Method 2: DigitalOcean Kubernetes

```bash
# Create Kubernetes cluster
doctl kubernetes cluster create weather-forecast-k8s --count 2 --size s-1vcpu-2gb --region nyc1

# Get credentials
doctl kubernetes cluster kubeconfig save weather-forecast-k8s

# Apply manifests
kubectl apply -f k8s/
```

## Heroku

Simple deployment for prototyping and small applications.

```bash
# Install Heroku CLI and login
heroku login

# Create Heroku app
heroku create weather-forecast-api

# Set environment variables
heroku config:set OPENWEATHERMAP_API_KEY=your_api_key_here

# Deploy using Container Registry
heroku container:login
heroku container:push web
heroku container:release web
```

Create `heroku.yml`:
```yaml
build:
  docker:
    web: Dockerfile
run:
  web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

## Kubernetes Deployment

### Kubernetes Manifests

#### Deployment
```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: weather-forecast
  labels:
    app: weather-forecast
spec:
  replicas: 3
  selector:
    matchLabels:
      app: weather-forecast
  template:
    metadata:
      labels:
        app: weather-forecast
    spec:
      containers:
      - name: weather-forecast
        image: weather-forecast:latest
        ports:
        - containerPort: 8080
        env:
        - name: OPENWEATHERMAP_API_KEY
          valueFrom:
            secretKeyRef:
              name: weather-forecast-secret
              key: api-key
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

#### Service
```yaml
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: weather-forecast-service
spec:
  selector:
    app: weather-forecast
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080
  type: ClusterIP
```

#### Ingress
```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: weather-forecast-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: weather-api.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: weather-forecast-service
            port:
              number: 80
```

#### Secret
```yaml
# k8s/secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: weather-forecast-secret
type: Opaque
data:
  api-key: <base64-encoded-api-key>
```

#### ConfigMap
```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: weather-forecast-config
data:
  DEBUG: "false"
  REQUEST_TIMEOUT: "10"
  MAX_CONCURRENT_REQUESTS: "100"
```

#### Horizontal Pod Autoscaler
```yaml
# k8s/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: weather-forecast-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: weather-forecast
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### Deploy to Kubernetes

```bash
# Create namespace
kubectl create namespace weather-forecast

# Create secret with API key
kubectl create secret generic weather-forecast-secret \
  --from-literal=api-key=your_api_key_here \
  --namespace weather-forecast

# Apply all manifests
kubectl apply -f k8s/ --namespace weather-forecast

# Check deployment status
kubectl get pods --namespace weather-forecast
kubectl get services --namespace weather-forecast
```

## Docker Swarm

For Docker Swarm deployments:

```yaml
# docker-compose.swarm.yml
version: '3.8'

services:
  weather-forecast:
    image: weather-forecast:latest
    ports:
      - "8080:8080"
    environment:
      - OPENWEATHERMAP_API_KEY=${OPENWEATHERMAP_API_KEY}
    deploy:
      replicas: 3
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
      update_config:
        parallelism: 1
        delay: 10s
        failure_action: rollback
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

networks:
  default:
    driver: overlay
    attachable: true
```

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.swarm.yml weather-forecast

# Check services
docker service ls
docker service ps weather-forecast_weather-forecast
```

## Cost Optimization

### AWS Cost Optimization
- Use **Spot Instances** for non-critical workloads
- Implement **auto-scaling** based on demand
- Use **Reserved Instances** for predictable workloads
- Consider **AWS Lambda** for sporadic usage

### Azure Cost Optimization
- Use **Azure Reserved VM Instances**
- Implement **auto-shutdown** for development environments
- Use **Azure Container Instances** for small workloads
- Consider **consumption-based** pricing models

### GCP Cost Optimization
- Use **preemptible instances** for batch processing
- Implement **automatic scaling**
- Use **sustained use discounts**
- Consider **Cloud Functions** for event-driven workloads

### General Cost Tips
- **Right-size resources** based on actual usage
- **Monitor and alert** on spending
- **Use caching** to reduce API calls
- **Implement efficient logging** to reduce storage costs

## Monitoring & Scaling

### Monitoring Setup

#### Prometheus + Grafana
```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'weather-forecast'
    static_configs:
      - targets: ['weather-forecast-service:8080']
    metrics_path: /metrics
    scrape_interval: 5s
```

#### Application Metrics
Add to your FastAPI app:
```python
from prometheus_fastapi_instrumentator import Instrumentator

# Add to main.py
Instrumentator().instrument(app).expose(app)
```

### Alerting Rules
```yaml
# alerts/rules.yml
groups:
- name: weather-forecast-alerts
  rules:
  - alert: HighErrorRate
    expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: "High error rate detected"
      
  - alert: ServiceDown
    expr: up{job="weather-forecast"} == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "Weather forecast service is down"
```

### Auto-scaling Configuration

#### CPU-based scaling
```bash
# Kubernetes HPA
kubectl autoscale deployment weather-forecast --cpu-percent=70 --min=2 --max=10

# AWS Auto Scaling
aws autoscaling create-auto-scaling-group \
  --auto-scaling-group-name weather-forecast-asg \
  --min-size 2 \
  --max-size 10 \
  --desired-capacity 3 \
  --target-group-arns arn:aws:elasticloadbalancing:region:account:targetgroup/weather-forecast-tg/id
```

#### Custom metrics scaling
```yaml
# Custom HPA based on API requests per second
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: weather-forecast-custom-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: weather-forecast
  minReplicas: 2
  maxReplicas: 20
  metrics:
  - type: Pods
    pods:
      metric:
        name: requests_per_second
      target:
        type: AverageValue
        averageValue: "100"
```

## Security Best Practices

### Container Security
- Use **non-root user** in containers
- **Scan images** for vulnerabilities
- Use **minimal base images**
- **Update dependencies** regularly

### Network Security
- Use **HTTPS/TLS** for all communications
- Implement **network policies** in Kubernetes
- Use **private subnets** for backend services
- Configure **security groups/firewalls** properly

### Secrets Management
- Use **managed secret services** (AWS Secrets Manager, Azure Key Vault, etc.)
- **Rotate API keys** regularly
- **Encrypt secrets** at rest and in transit
- **Audit secret access**

### Example: AWS Secrets Manager Integration
```python
import boto3
import json

def get_secret(secret_name):
    session = boto3.session.Session()
    client = session.client('secretsmanager', region_name='us-east-1')
    
    try:
        response = client.get_secret_value(SecretId=secret_name)
        secret = json.loads(response['SecretString'])
        return secret['OPENWEATHERMAP_API_KEY']
    except Exception as e:
        raise Exception(f"Failed to retrieve secret: {e}")

# Use in config.py
api_key = get_secret('weather-forecast/api-key')
```

## Backup and Disaster Recovery

### Database Backups
If you add a database later:
```bash
# PostgreSQL backup
pg_dump -h host -U user -d weather_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Automated backup script
#!/bin/bash
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME > $BACKUP_DIR/backup_$DATE.sql
aws s3 cp $BACKUP_DIR/backup_$DATE.sql s3://backup-bucket/weather-forecast/
```

### Configuration Backups
```bash
# Kubernetes configuration backup
kubectl get all --all-namespaces -o yaml > k8s-backup-$(date +%Y%m%d).yaml

# Docker Swarm backup
docker config ls
docker secret ls
```

### Multi-region Deployment
```yaml
# Global load balancer configuration for multi-region
# AWS Route 53 health checks and failover
# Azure Traffic Manager
# GCP Global Load Balancer
```

This comprehensive deployment guide covers all major cloud platforms and deployment scenarios. Choose the method that best fits your requirements, budget, and technical constraints.