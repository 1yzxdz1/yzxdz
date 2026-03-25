# Deployment Guide

## Goal

Deploy this project to a cloud server so other people can access it from their own computers through a browser.

## Recommended Production Topology

- `frontend`: Vue build served by Nginx
- `backend`: FastAPI served by Uvicorn
- `database`: SQLite MVP version stored on the server
- `entry`: public HTTP port `80`

This repository already includes:

- `backend/Dockerfile`
- `frontend/Dockerfile`
- `frontend/nginx/default.conf`
- `docker-compose.prod.yml`

## Step 1: Prepare a Linux server

Recommended:

- Ubuntu 22.04 or 24.04
- 2 vCPU
- 2 GB RAM

Open these ports in the cloud firewall/security group:

- `80` for HTTP
- `443` for HTTPS if you add SSL later
- `22` for SSH

## Step 2: Install Docker and Docker Compose

Example on Ubuntu:

```bash
sudo apt update
sudo apt install -y docker.io docker-compose-plugin
sudo systemctl enable docker
sudo systemctl start docker
```

## Step 3: Upload the project

You can upload with Git:

```bash
git clone <your-repo-url>
cd NCRE-Review-System
```

Or copy the project folder to the server manually.

## Step 4: Initialize the database once

Before starting containers, initialize the SQLite file:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/seed_data.py
cd ..
```

This will create:

- `backend/ncre_review.db`

## Step 5: Start production containers

From the project root:

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

After startup, open:

- `http://<your-server-ip>`

## Step 6: Register the first real user

Because demo accounts were removed, the system starts with zero users.

Open:

- `http://<your-server-ip>/login`

Then register your own account.

## Optional Step 7: Bind a domain

Point your domain DNS `A` record to your server IP:

- `review.example.com -> <your-server-ip>`

Then later you can add HTTPS with:

- Nginx + Certbot
- or Caddy
- or a cloud load balancer

## Notes

- This MVP uses SQLite, which is fine for demo and low traffic.
- For public production with more users, switch to PostgreSQL.
- If you change the server port mapping, also update your firewall rules.
