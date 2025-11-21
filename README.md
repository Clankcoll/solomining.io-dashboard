# Read-Only Mirror

> **Note:** This is a read-only public mirror. The source repository is hosted on a private GitLab instance.
>
> - **Issues & Pull Requests:** Not monitored here
> - **Updates:** Automatically synced from private repository
> - **Docker Images:** Available on [Docker Hub](https://hub.docker.com/r/clanktechstudio/solomining.io-dashboard)

---

# Solomining.io Dashboard

[![License: Dual](https://img.shields.io/badge/License-Dual%20(Personal%2FCommercial)-blue.svg)](LICENSE)
[![Docker Hub](https://img.shields.io/badge/Docker%20Hub-clanktechstudio%2Fsolomining.io--dashboard-blue)](https://hub.docker.com/r/clanktechstudio/solomining.io-dashboard)

![Grafana Dashboard Preview](pictures/dashboard-preview.png)

Monitor your [solomining.io](https://bchnode.solomining.io) mining with a beautiful Grafana dashboard. Works with any coin supported by solomining.io (BCH, BTC, LTC, and more). Track hashrates, block probabilities, worker performance, and more.

---

## ⚡ Fastest Setup - One Command Install

**Complete installation in one command:**

```bash
curl -sSL https://raw.githubusercontent.com/Clankcoll/solomining.io-dashboard/main/setup.sh | bash
```

This will:
- Download all necessary files
- Prompt for your mining address
- Start Prometheus + Grafana + Exporter
- Pre-load the dashboard

**Access:** http://localhost:3000 (admin/admin)

---

## 🚀 Quick Start - Full Stack (Manual)

**Get everything running in 3 commands:**

```bash
# 1. Clone and enter directory
git clone https://github.com/Clankcoll/solomining.io-dashboard.git
cd solomining.io-dashboard

# 2. Configure your BCH address
cp .env.example .env
nano .env  # Edit BCH_ADDRESS=bitcoincash:YOUR_ADDRESS_HERE

# 3. Start all services (Prometheus + Grafana + Exporter)
docker-compose -f docker-compose.full-stack.yml up -d
```

**Access:** http://localhost:3000 (admin/admin)
**Dashboard is pre-loaded and ready to use!**

---

## 🔧 Quick Start - Exporter Only

**Already have Prometheus and Grafana?**

**Option 1: Using docker-compose.yml**
```bash
# Download the docker-compose.yml file
wget https://raw.githubusercontent.com/Clankcoll/solomining.io-dashboard/main/docker-compose.yml

# Edit and set your mining address
nano docker-compose.yml

# Start the exporter
docker-compose up -d
```

**Option 2: Using docker run**
```bash
docker run -d \
  -p 9123:9123 \
  -e BCH_ADDRESS=bitcoincash:YOUR_ADDRESS_HERE \
  clanktechstudio/solomining.io-dashboard:latest
```

Then add to Prometheus and import the dashboard from [here](https://raw.githubusercontent.com/Clankcoll/solomining.io-dashboard/main/grafana/dashboards/solomining-dashboard.json).

---

## 📚 Documentation

**[→ Full Documentation](DOCUMENTATION.md)** - Detailed setup, configuration, troubleshooting, and advanced options.

---

## 📄 License

**Personal Use**: Free
**Commercial Use**: License required → Contact: info@clank.tech

See [LICENSE](LICENSE) for details.

---

**Made by ClankTech (Clankcoll)**
