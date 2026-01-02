# Production Server Requirements - ClipForge AI Video Generation System

## Executive Summary

ClipForge is an AI-powered video generation system that requires significant computational resources for video rendering and API calls to external AI services (OpenAI, ElevenLabs, Google Gemini).

---

## 1. Hardware Requirements

### Minimum Production Server Specifications

#### **Single Server Setup (Small Scale: 1-10 videos/hour)**

| Component | Specification | Notes |
|-----------|--------------|-------|
| **CPU** | 8-core / 16-thread (Intel Xeon E5 or AMD EPYC) | Video encoding is CPU-intensive |
| **RAM** | 16 GB DDR4 | Minimum for concurrent processing |
| **Storage** | 500 GB SSD | Fast I/O for image/video operations |
| **GPU** | Optional (NVIDIA T4 or better) | Accelerates video rendering |
| **Network** | 100 Mbps+ | For API calls and file downloads |
| **OS** | Ubuntu 22.04 LTS or Windows Server 2022 | Linux preferred for stability |

#### **Recommended Production Server (Medium Scale: 10-50 videos/hour)**

| Component | Specification | Notes |
|-----------|--------------|-------|
| **CPU** | 16-core / 32-thread (Intel Xeon Gold or AMD EPYC) | Better parallel processing |
| **RAM** | 32 GB DDR4 | Handle multiple concurrent jobs |
| **Storage** | 1 TB NVMe SSD | High-speed storage for temp files |
| **GPU** | NVIDIA Tesla T4 / RTX 4060 (8GB VRAM) | Significantly faster rendering |
| **Network** | 1 Gbps | Fast API communication |
| **Backup Storage** | 2 TB HDD/SSD | For video archives |

#### **Enterprise Setup (High Scale: 50-200 videos/hour)**

| Component | Specification | Notes |
|-----------|--------------|-------|
| **CPU** | 32-core / 64-thread (Dual Xeon or AMD EPYC) | Multiple worker processes |
| **RAM** | 64-128 GB DDR4/DDR5 | Heavy multitasking |
| **Storage** | 2 TB NVMe SSD (RAID 10) | Redundancy + speed |
| **GPU** | NVIDIA A100 / RTX 4090 (24GB VRAM) | Professional-grade rendering |
| **Network** | 10 Gbps | Enterprise bandwidth |
| **Load Balancer** | Yes | Distribute requests |

---

## 2. Cloud Infrastructure Options

### **AWS (Amazon Web Services)**

#### Recommended Instance Types:

**Small Scale:**
- **Instance:** `t3.xlarge` (4 vCPUs, 16 GB RAM)
- **Storage:** 500 GB gp3 EBS
- **Estimated Cost:** ~$120-150/month

**Medium Scale:**
- **Instance:** `c6i.4xlarge` (16 vCPUs, 32 GB RAM)
- **Storage:** 1 TB gp3 EBS
- **Optional GPU:** `g4dn.xlarge` (NVIDIA T4)
- **Estimated Cost:** ~$400-600/month

**Enterprise Scale:**
- **Instance:** `c6i.8xlarge` + `g5.2xlarge` (GPU)
- **Load Balancer:** Application Load Balancer
- **Storage:** 2 TB EBS + S3 for archives
- **Estimated Cost:** ~$1,500-2,500/month

### **Google Cloud Platform (GCP)**

**Recommended:**
- **Instance:** `n2-standard-8` (8 vCPUs, 32 GB)
- **GPU:** NVIDIA T4 (optional)
- **Storage:** 1 TB Persistent SSD
- **Estimated Cost:** ~$350-550/month

### **Microsoft Azure**

**Recommended:**
- **Instance:** `Standard_D8s_v5` (8 vCPUs, 32 GB)
- **Storage:** Premium SSD 1 TB
- **GPU:** NC-series with NVIDIA T4
- **Estimated Cost:** ~$400-650/month

### **DigitalOcean (Budget Option)**

**Recommended:**
- **Droplet:** CPU-Optimized 8 vCPU, 16 GB RAM
- **Storage:** 1 TB Block Storage
- **Estimated Cost:** ~$250-350/month

### **Hostinger VPS (Budget-Friendly Option)**

**✅ YES - This project works perfectly on Hostinger VPS!**

Hostinger offers excellent VPS hosting at competitive prices, suitable for small to medium-scale deployments.

#### **Recommended Hostinger VPS Plans:**

**VPS Plan 4 (Starter/Small Scale):**
- **Specs:** 4 vCPU, 8 GB RAM, 200 GB NVMe
- **Bandwidth:** 4 TB
- **Cost:** ~$15-20/month
- **Suitable for:** 50-100 videos/month, testing, development
- **Limitation:** May struggle with concurrent requests

**VPS Plan 6 (Recommended for Production):**
- **Specs:** 6 vCPU, 12 GB RAM, 300 GB NVMe
- **Bandwidth:** 6 TB
- **Cost:** ~$30-40/month
- **Suitable for:** 200-500 videos/month
- **Performance:** Good for most use cases

**VPS Plan 8 (High Performance):**
- **Specs:** 8 vCPU, 16 GB RAM, 400 GB NVMe
- **Bandwidth:** 8 TB
- **Cost:** ~$60-80/month
- **Suitable for:** 500-1,000 videos/month
- **Performance:** Excellent for production

#### **Hostinger Setup Guide:**

1. **Order VPS with Ubuntu 22.04**
2. **Install Required Software:**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.10+
sudo apt install python3.10 python3-pip python3-venv -y

# Install FFmpeg and dependencies
sudo apt install ffmpeg imagemagick libmagickwand-dev -y
sudo apt install fonts-liberation libsm6 libxext6 libxrender-dev -y

# Install Nginx (reverse proxy)
sudo apt install nginx -y

# Install Certbot for SSL
sudo apt install certbot python3-certbot-nginx -y
```

3. **Deploy Application:**
```bash
# Clone your project
git clone your-repo-url
cd video_mike

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Add your API keys
```

4. **Set up Systemd Service:**
```bash
sudo nano /etc/systemd/system/clipforge.service
```

Add:
```ini
[Unit]
Description=ClipForge Video Generation API
After=network.target

[Service]
User=your-username
WorkingDirectory=/home/your-username/video_mike
Environment="PATH=/home/your-username/video_mike/venv/bin"
ExecStart=/home/your-username/video_mike/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

5. **Configure Nginx:**
```bash
sudo nano /etc/nginx/sites-available/clipforge
```

Add:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Increase timeout for video generation
        proxy_read_timeout 300s;
        proxy_connect_timeout 300s;
    }
}
```

6. **Enable SSL:**
```bash
sudo certbot --nginx -d your-domain.com
```

7. **Start Service:**
```bash
sudo systemctl enable clipforge
sudo systemctl start clipforge
sudo systemctl status clipforge
```

#### **Hostinger VPS Advantages:**
- ✅ Very affordable ($15-80/month)
- ✅ Good performance for the price
- ✅ Easy management panel
- ✅ Weekly backups included
- ✅ DDoS protection
- ✅ 24/7 support
- ✅ Multiple datacenter locations
- ✅ Full root access

#### **Hostinger VPS Limitations:**
- ⚠️ No GPU support (slower video rendering)
- ⚠️ Limited scalability vs cloud platforms
- ⚠️ Manual scaling (can't auto-scale)
- ⚠️ Single server setup
- ⚠️ Storage upgrades can be costly

#### **Performance on Hostinger VPS:**

**VPS Plan 6 (6 vCPU, 12 GB):**
- Video generation time: 90-180 seconds (vs 60-120s with GPU)
- Concurrent videos: 2-3 simultaneous
- Monthly capacity: 300-500 videos
- API costs: Still ~$0.30-0.40 per video

**Total Monthly Cost (VPS Plan 6):**
- VPS: $35/month
- API costs (500 videos): $150-200/month
- Domain + SSL: $15/month (if not using free SSL)
- **Total: $200-250/month** for 500 videos

#### **When to Use Hostinger VPS:**
✅ Small to medium projects (100-1,000 videos/month)
✅ Budget constraints
✅ Learning/testing environment
✅ Predictable traffic
✅ Single region deployment

#### **When to Upgrade to Cloud Platforms:**
⛔ Need auto-scaling
⛔ High traffic/concurrent requests (>10 simultaneous)
⛔ Global distribution required
⛔ Need managed services (database, load balancer)
⛔ Generating >2,000 videos/month

### **Other VPS Providers Comparison**

| Provider | 8 vCPU, 16GB RAM | Storage | Monthly Cost |
|----------|------------------|---------|--------------|
| **Hostinger** | ✅ Best Value | 400 GB NVMe | $60-80 |
| **Vultr** | Good | 320 GB SSD | $96 |
| **Linode** | Good | 320 GB SSD | $96 |
| **Hetzner** | Excellent | 240 GB SSD | €37 (~$40) |
| **Contabo** | Budget | 400 GB SSD | €25 (~$27) |
| **DigitalOcean** | Good | 160 GB SSD | $96 |

**Winner for Budget:** Hostinger or Hetzner
**Winner for Performance:** Hetzner or Hostinger VPS Plan 8

---

## 3. Software Requirements

### **Operating System**
- **Linux:** Ubuntu 22.04 LTS (Recommended)
- **Alternative:** Debian 11+, CentOS 8+, Windows Server 2022

### **Runtime Environment**
```
Python: 3.10 or higher
Node.js: 18+ (if adding frontend build)
FFmpeg: 4.4+ (Critical for video processing)
ImageMagick: 7.1+ (For subtitle rendering)
```

### **Python Dependencies**
```
FastAPI
Uvicorn[standard]
OpenAI SDK
ElevenLabs SDK
Google Generative AI SDK
MoviePy (2.x)
Pillow
NumPy
Pydantic
Python-dotenv
Python-slugify
```

### **System Libraries (Linux)**
```bash
sudo apt-get install -y \
    ffmpeg \
    imagemagick \
    libmagickwand-dev \
    fonts-liberation \
    libsm6 \
    libxext6 \
    libxrender-dev
```

---

## 4. Network & Security Requirements

### **Firewall Rules**
```
Inbound:
- Port 8000 (HTTP API) - From Load Balancer/Internet
- Port 443 (HTTPS) - Production with SSL
- Port 22 (SSH) - Admin access only (restrict IPs)

Outbound:
- Port 443 (HTTPS) - API calls to OpenAI, ElevenLabs, Google
- Port 80 (HTTP) - Package updates
```

### **SSL/TLS Certificate**
- **Required:** Yes (Let's Encrypt or commercial)
- **Provider:** Certbot, AWS Certificate Manager, Cloudflare

### **API Rate Limits**
```
OpenAI: Monitor token usage (GPT-4, DALL-E)
ElevenLabs: Character limits per month
Google Gemini: Request quotas
```

---

## 5. Storage Requirements

### **Disk Space Calculation**

Per Video:
- Images (7x): ~5-10 MB
- Audio: ~1-3 MB
- Video Output: ~10-50 MB (depending on length/quality)
- Temp Files: ~20-30 MB (deleted after)

**Total per video:** ~15-60 MB

**Monthly Storage Needs:**
- 100 videos/month: ~5 GB
- 1,000 videos/month: ~50 GB
- 10,000 videos/month: ~500 GB

### **Recommended Storage Strategy**
```
Local SSD: Active/temp files (500 GB - 2 TB)
Object Storage (S3/GCS): Archive completed videos
CDN: Serve videos to users (CloudFront, Cloudflare)
Backup: Weekly snapshots to separate region
```

---

## 6. Database Requirements

### **Current Setup**
- JSON-based database (videos_list.json)
- Suitable for <1,000 videos

### **Production Recommendation**
**Migrate to PostgreSQL or MySQL**

**Specifications:**
- **Version:** PostgreSQL 15+ / MySQL 8.0+
- **RAM:** 4-8 GB dedicated
- **Storage:** 50-100 GB SSD
- **Backup:** Daily automated backups

**Cloud Options:**
- AWS RDS PostgreSQL
- Google Cloud SQL
- Azure Database for PostgreSQL
- DigitalOcean Managed Database

---

## 7. Scalability Architecture

### **Horizontal Scaling (Recommended)**

```
                    [Load Balancer]
                          |
        +-----------------+------------------+
        |                 |                  |
   [App Server 1]   [App Server 2]   [App Server 3]
        |                 |                  |
        +-----------------+------------------+
                          |
                  [Shared Storage/S3]
                          |
                    [PostgreSQL DB]
```

### **Queue-Based Processing**
```
API Server → Redis/RabbitMQ Queue → Worker Processes → S3 Storage
```

**Benefits:**
- Handle burst traffic
- Prevent server overload
- Better resource utilization
- Easy to add workers

### **Recommended Queue System**
- **Redis** with Celery (Python)
- **RabbitMQ** for enterprise
- **AWS SQS** for AWS deployments

---

## 8. Monitoring & Logging

### **Required Monitoring**
```
Server Metrics:
- CPU utilization
- RAM usage
- Disk I/O
- Network traffic

Application Metrics:
- API response times
- Video generation success rate
- Queue length
- Error rates

External API Costs:
- OpenAI token usage
- ElevenLabs character count
- Google Gemini requests
```

### **Recommended Tools**
- **Monitoring:** Prometheus + Grafana, DataDog, New Relic
- **Logging:** ELK Stack (Elasticsearch, Logstash, Kibana)
- **Error Tracking:** Sentry
- **Uptime:** UptimeRobot, Pingdom

---

## 9. API Cost Estimates

### **Per Video Generation**

| Service | Usage | Cost |
|---------|-------|------|
| **OpenAI GPT-4** | Image prompts (~500 tokens) | ~$0.01 |
| **OpenAI DALL-E 3** | 7 images (1024x1024) | ~$0.28 |
| **ElevenLabs** | ~500 characters | ~$0.02 |
| **Google Gemini** | Alternative to DALL-E | ~$0.05-0.10 |
| **Total per video** | | **~$0.30-0.40** |

### **Monthly Cost Projections**

| Videos/Month | API Costs | Server | Total |
|--------------|-----------|--------|-------|
| 100 | $30-40 | $150 | ~$200 |
| 1,000 | $300-400 | $400 | ~$750 |
| 10,000 | $3,000-4,000 | $1,500 | ~$5,500 |

---

## 10. Performance Benchmarks

### **Expected Processing Times**

| Step | Time | Notes |
|------|------|-------|
| Narration (OpenAI TTS) | 5-10s | API call |
| Image Generation (DALL-E) | 30-60s | 7 images |
| Video Composition | 20-40s | CPU/GPU dependent |
| Subtitle Generation | 2-5s | AI segmentation |
| **Total** | **60-120s** | 1-2 minutes per video |

### **Optimization Tips**
- Use GPU for 50% faster video rendering
- Cache common prompts/styles
- Parallel image generation
- Optimize FFmpeg settings
- Use CDN for video delivery

---

## 11. Backup & Disaster Recovery

### **Backup Strategy**
```
Database: Daily automated backups (7-day retention)
Videos: Weekly backup to S3 Glacier
Configuration: Version control (Git)
Logs: 30-day retention in logging service
```

### **High Availability**
- Multi-region deployment
- Database replication
- Automatic failover
- CDN for global delivery

---

## 12. Security Best Practices

### **Required Security Measures**
- ✅ HTTPS/SSL for all traffic
- ✅ API key rotation (monthly)
- ✅ Environment variables for secrets
- ✅ Rate limiting on endpoints
- ✅ Input validation and sanitization
- ✅ Regular security updates
- ✅ Firewall rules (restrict to necessary ports)
- ✅ DDoS protection (Cloudflare, AWS Shield)
- ✅ Backup encryption
- ✅ Access logs and audit trails

---

## 13. Deployment Checklist

### **Pre-Production**
- [ ] Set up production server/cloud instance
- [ ] Install all required software dependencies
- [ ] Configure environment variables (.env)
- [ ] Set up PostgreSQL/MySQL database
- [ ] Configure SSL certificate
- [ ] Set up monitoring and logging
- [ ] Configure backup automation
- [ ] Load test the system
- [ ] Security audit

### **Production Launch**
- [ ] Deploy application code
- [ ] Configure reverse proxy (Nginx/Apache)
- [ ] Set up process manager (systemd/PM2)
- [ ] Configure auto-restart on failure
- [ ] Set up CDN for video delivery
- [ ] Configure rate limiting
- [ ] Monitor API costs
- [ ] Document runbooks

---

## 14. Cost Summary

### **Minimum Viable Production (100 videos/month)**
- **Server:** $150/month
- **API Costs:** $40/month
- **Storage:** $20/month
- **Monitoring:** $30/month
- **SSL/Domain:** $15/month
- **TOTAL:** ~$255/month

### **Medium Scale (1,000 videos/month)**
- **Server:** $500/month
- **API Costs:** $400/month
- **Storage/CDN:** $100/month
- **Database:** $50/month
- **Monitoring:** $100/month
- **TOTAL:** ~$1,150/month

### **Enterprise Scale (10,000 videos/month)**
- **Servers (3x):** $1,500/month
- **API Costs:** $4,000/month
- **Storage/CDN:** $500/month
- **Database:** $200/month
- **Monitoring:** $300/month
- **TOTAL:** ~$6,500/month

---

## 15. Recommended Starting Configuration

### **For Most Production Deployments**

**Cloud Provider:** AWS / Google Cloud
**Instance:** 8 vCPU, 32 GB RAM
**Storage:** 1 TB SSD
**Database:** PostgreSQL (managed)
**Monitoring:** Basic metrics + error tracking
**Budget:** $500-700/month

This configuration can handle:
- 500-1,000 videos/month
- 5-10 concurrent generations
- Room for growth
- Good performance

---

**Last Updated:** December 31, 2025  
**Version:** 1.0  
**Contact:** Production DevOps Team
