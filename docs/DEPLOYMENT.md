# Deployment Guide

This guide covers deploying the Perpetual Scholar Agent in production environments.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start (Docker Compose)](#quick-start-docker-compose)
- [Production Deployment](#production-deployment)
- [Configuration](#configuration)
- [Monitoring](#monitoring)
- [Backup & Recovery](#backup--recovery)
- [Troubleshooting](#troubleshooting)
- [Security Considerations](#security-considerations)

## Prerequisites

- Docker 20.10+ and Docker Compose 2.0+
- Python 3.11+ (for bare metal deployment)
- 8GB RAM minimum (16GB recommended)
- 50GB disk space (for models, database, and experiments)
- For local SLM: Ollama installed with Qwen2.5-Coder-7B or DeepSeek-Coder-7B
- For cloud LLM: API keys for Anthropic Claude or OpenAI GPT-4o

## Quick Start (Docker Compose)

### 1. Clone and Configure

```bash
git clone https://github.com/your-org/perpetual-scholar-agent.git
cd perpetual-scholar-agent
cp .env.example .env
# Edit .env with your configuration
```

### 2. Start Services

```bash
docker-compose up -d
```

This starts:
- **Agent**: Main orchestration service
- **Ollama**: Local SLM backend (if configured)
- **PostgreSQL**: Lesson storage and experiment tracking
- **Redis**: Task queue and caching
- **Grafana + Prometheus**: Monitoring stack

### 3. Initialize Database

```bash
docker-compose exec agent python -m agent.database.schema init
```

### 4. Verify Health

```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy", "timestamp": "2025-..."}
```

## Production Deployment

### Option 1: Docker Swarm / Kubernetes

For scalable deployments with redundancy:

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  agent:
    image: ghcr.io/your-org/perpetual-scholar-agent:latest
    environment:
      - ENVIRONMENT=production
      - LOG_LEVEL=INFO
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2'
          memory: 4G
    volumes:
      - agent_data:/app/data
      - /var/run/docker.sock:/var/run/docker.sock:ro
```

Deploy:
```bash
docker stack deploy -c docker-compose.prod.yml psa
```

### Option 2: Bare Metal with systemd

#### 1. Install System Dependencies

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y python3.11 python3.11-venv docker.io redis-server postgresql

# Create service user
sudo useradd -r -s /bin/bash psa
sudo mkdir -p /opt/perpetual-scholar-agent
sudo chown psa:psa /opt/perpetual-scholar-agent
```

#### 2. Setup Application

```bash
# As psa user
cd /opt/perpetual-scholar-agent
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Copy and configure
cp .env.example .env
# Edit .env for production
```

#### 3. Configure systemd

```bash
# Copy service file
sudo cp psa-agent.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable psa-agent
sudo systemctl start psa-agent
```

#### 4. Verify

```bash
sudo systemctl status psa-agent
sudo journalctl -u psa-agent -f
```

### Option 3: Cloud Deployment (AWS/GCP/Azure)

#### AWS EC2 with ECS

1. **ECR Setup**
```bash
aws ecr create-repository --repository-name perpetual-scholar-agent
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/perpetual-scholar-agent:latest
```

2. **ECS Task Definition**
```json
{
  "family": "perpetual-scholar-agent",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "2048",
  "memory": "4096",
  "containerDefinitions": [
    {
      "name": "agent",
      "image": "<account-id>.dkr.ecr.<region>.amazonaws.com/perpetual-scholar-agent:latest",
      "environment": [
        {"name": "ENVIRONMENT", "value": "production"},
        {"name": "LOG_LEVEL", "value": "INFO"}
      ],
      "secrets": [
        {"name": "ANTHROPIC_API_KEY", "valueFrom": "arn:aws:secretsmanager:..."}
      ]
    }
  ]
}
```

3. **Deploy**
```bash
aws ecs create-service --cluster psa-prod --task-definition perpetual-scholar-agent --desired-count 2 --launch-type FARGATE
```

#### Google Cloud Run

```bash
# Build and push
gcloud builds submit --tag gcr.io/$PROJECT_ID/perpetual-scholar-agent

# Deploy
gcloud run deploy perpetual-scholar-agent \
  --image gcr.io/$PROJECT_ID/perpetual-scholar-agent \
  --platform managed \
  --region us-central1 \
  --memory 4Gi \
  --cpu 2 \
  --set-env-vars ENVIRONMENT=production \
  --set-secrets ANTHROPIC_API_KEY=anthropic-api-key:latest
```

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `ENVIRONMENT` | Environment (development/production) | `development` | Yes |
| `LOG_LEVEL` | Logging verbosity | `INFO` | No |
| `DOMAIN_FOCUS` | Research domain | `backend_performance` | No |
| `LLM_PROVIDER` | LLM backend (ollama/claude/openai) | `ollama` | Yes |
| `OLLAMA_BASE_URL` | Ollama API endpoint | `http://localhost:11434` | If LLM_PROVIDER=ollama |
| `OLLAMA_MODEL` | Ollama model name | `qwen2.5-coder:7b` | If LLM_PROVIDER=ollama |
| `ANTHROPIC_API_KEY` | Claude API key | - | If LLM_PROVIDER=claude |
| `DATABASE_URL` | Postgres connection string | `postgresql://...` | Yes |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379` | Yes |
| `SANDBOX_CPU_LIMIT` | Max CPU per experiment | `2` | No |
| `SANDBOX_MEMORY_LIMIT` | Max RAM per experiment | `2g` | No |
| `EXPERIMENT_TIMEOUT_SECONDS` | Experiment timeout | `300` | No |

### Production Recommendations

1. **Secrets Management**: Use AWS Secrets Manager, HashiCorp Vault, or Kubernetes secrets
2. **Database**: Use managed Postgres (RDS, CloudSQL, Azure Database)
3. **Queue**: Use managed Redis (ElastiCache, Memorystore, Azure Cache)
4. **Monitoring**: Enable Prometheus metrics and Grafana dashboards
5. **Logging**: Ship logs to CloudWatch, Elasticsearch, or Loki

## Monitoring

### Health Endpoints

```bash
# Overall health
curl http://localhost:8000/health

# Component status
curl http://localhost:8000/health/components

# Metrics (Prometheus format)
curl http://localhost:8000/metrics
```

### Key Metrics

- **Experiments Run**: Total experiments executed
- **Experiments Failed**: Failed experiment rate
- **Lessons Learned**: Verified lessons stored
- **Sandbox Utilization**: Docker container usage
- **LLM Latency**: Average LLM response time
- **Database Latency**: Query performance

### Grafana Dashboards

Import the pre-configured dashboard from `monitoring/grafana-dashboard.json`:

```bash
curl http://localhost:3000/api/dashboards/import \
  -X POST \
  -H "Content-Type: application/json" \
  -u admin:admin \
  -d @monitoring/grafana-dashboard.json
```

### Alerts

Configure Prometheus alerts in `monitoring/alerts.yml`:

```yaml
groups:
  - name: psa_alerts
    rules:
      - alert: HighFailureRate
        expr: rate(experiments_failed_total[5m]) > 0.1
        annotations:
          summary: "High experiment failure rate"
      
      - alert: SandboxExhausted
        expr: sandbox_available_containers < 1
        annotations:
          summary: "No sandbox containers available"
```

## Backup & Recovery

### Database Backups

#### Automated (Recommended)

```bash
# Daily backups via cron
0 2 * * * pg_dump -U psa -h localhost perpetual_scholar | gzip > /backups/psa-$(date +\%Y\%m\%d).sql.gz
```

#### Manual

```bash
# Backup
docker-compose exec postgres pg_dump -U psa perpetual_scholar > backup.sql

# Restore
docker-compose exec -T postgres psql -U psa perpetual_scholar < backup.sql
```

### Lesson Store Backups

```bash
# Backup SQLite database and vector index
tar -czf lessons-backup.tar.gz data/lessons.db data/faiss.index/

# Restore
tar -xzf lessons-backup.tar.gz -C data/
```

### Model Checkpoints

```bash
# Backup LoRA adapters
tar -czf lora-backup.tar.gz models/lora-adapters/

# Restore
tar -xzf lora-backup.tar.gz -C models/
```

### Disaster Recovery

1. **Database Restoration**
   - Stop agent: `docker-compose stop agent`
   - Restore Postgres: `docker-compose exec -T postgres psql ... < backup.sql`
   - Verify: `docker-compose exec postgres psql -U psa -c "SELECT COUNT(*) FROM lessons;"`
   - Restart: `docker-compose start agent`

2. **Complete System Restoration**
   - Deploy fresh infrastructure
   - Restore database, lessons, models from backups
   - Verify with: `python -m tests.integration.test_recovery`

## Troubleshooting

### Common Issues

#### 1. Agent Won't Start

**Symptom**: Container exits immediately

**Diagnosis**:
```bash
docker-compose logs agent
# Check for:
# - Missing environment variables
# - Database connection failures
# - Port conflicts
```

**Fix**:
- Verify `.env` file exists and is valid
- Check database is accessible: `docker-compose exec postgres ping`
- Ensure ports 8000, 11434 are available

#### 2. Ollama Connection Timeout

**Symptom**: `requests.exceptions.ConnectionError: ollama`

**Diagnosis**:
```bash
curl http://localhost:11434/api/tags
# Should return model list
```

**Fix**:
- Restart Ollama: `docker-compose restart ollama`
- Pull required model: `docker-compose exec ollama ollama pull qwen2.5-coder:7b`
- Check Ollama logs: `docker-compose logs ollama`

#### 3. Experiments Hanging

**Symptom**: Experiments never complete

**Diagnosis**:
```bash
# Check sandbox containers
docker ps | grep sandbox

# Check agent logs
docker-compose logs agent | grep experiment
```

**Fix**:
- Lower timeout: `EXPERIMENT_TIMEOUT_SECONDS=120`
- Increase sandbox limits: `SANDBOX_CPU_LIMIT=4`
- Kill stuck containers: `docker kill $(docker ps -q -f name=sandbox)`

#### 4. High Memory Usage

**Symptom**: OOM kills or swapping

**Diagnosis**:
```bash
docker stats
# Check per-container memory usage
```

**Fix**:
- Add memory limits to docker-compose.yml
- Reduce concurrent experiments: `MAX_CONCURRENT_EXPERIMENTS=2`
- Clear unused Docker images: `docker system prune -a`

#### 5. Database Locks

**Symptom**: `database is locked` or connection timeouts

**Diagnosis**:
```bash
docker-compose exec postgres psql -U psa -c "SELECT * FROM pg_stat_activity WHERE state = 'active';"
```

**Fix**:
- Close idle connections: `docker-compose restart postgres`
- Increase pool size: `DATABASE_POOL_SIZE=20`
- Enable connection pooling: Configure PgBouncer

### Debug Mode

Enable detailed logging:

```bash
# In .env
LOG_LEVEL=DEBUG
DEBUG_EXPERIMENTS=true

# Restart
docker-compose restart agent
```

### Health Check Failures

```bash
# Run comprehensive health check
curl http://localhost:8000/health/detailed

# Expected output:
{
  "status": "healthy",
  "checks": {
    "database": "ok",
    "redis": "ok",
    "ollama": "ok",
    "sandbox": "ok"
  }
}
```

## Security Considerations

### Production Hardening

1. **Network Isolation**
   - Run agent in isolated VPC/subnet
   - Restrict outbound internet access
   - Use private endpoints for cloud resources

2. **Container Security**
   - Run as non-root user
   - Read-only root filesystem where possible
   - Scan images for vulnerabilities: `docker scan perpetual-scholar-agent`

3. **Secrets Management**
   - Never commit `.env` files
   - Rotate API keys regularly
   - Use different keys for dev/staging/prod

4. **Sandbox Isolation**
   - Experiments run in ephemeral containers
   - Network access blocked or restricted
   - Resource limits enforced

5. **API Security**
   - Enable authentication for admin endpoints
   - Use HTTPS in production
   - Rate-limit external API calls

### Compliance Notes

- **GDPR**: No user data is stored by default
- **SOC2**: Enable audit logging: `AUDIT_LOGGING=true`
- **HIPAA**: Not designed for healthcare data
- **FedRAMP**: Use government cloud regions

### Updating

```bash
# Pull latest image
docker-compose pull

# Zero-downtime deployment
docker-compose up -d --no-deps agent

# Or rolling restart
docker-compose up -d --no-deps --force-recreate agent
```

### Rollback

```bash
# Tag previous version
docker tag perpetual-scholar-agent:latest perpetual-scholar-agent:previous

# Rollback
docker-compose.yml:
  image: perpetual-scholar-agent:previous
```

## Performance Tuning

### For High Experiment Throughput

1. Increase parallelism:
```bash
MAX_CONCURRENT_EXPERIMENTS=10
SANDBOX_CPU_LIMIT=1
SANDBOX_MEMORY_LIMIT=1g
```

2. Use Redis for queue:
```bash
REDIS_URL=redis://redis-cluster:6379
```

3. Batch embeddings:
```bash
EMBEDDING_BATCH_SIZE=32
```

### For Low Resource Usage

1. Reduce concurrency:
```bash
MAX_CONCURRENT_EXPERIMENTS=1
```

2. Use smaller model:
```bash
OLLAMA_MODEL=qwen2.5-coder:3b
```

3. Increase experiment filtering:
```bash
MIN_RELEVANCE_SCORE=0.8
```

## Support

- **Documentation**: https://docs.perpetual-scholar-agent.com
- **Issues**: https://github.com/your-org/perpetual-scholar-agent/issues
- **Discussions**: https://github.com/your-org/perpetual-scholar-agent/discussions
- **Email**: support@perpetual-scholar-agent.com
