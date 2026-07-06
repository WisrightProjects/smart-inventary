# Deployment Guide

## Overview

Two independent services to deploy:

- **Backend**: FastAPI app (`backend.main:app`) + SQLite DB + RT-DETR model.
- **Frontend**: Static React build served by any static host or reverse
  proxy.

## Backend

### Option A: Single machine (recommended for a shop-floor/warehouse box)

Run behind a process manager so it survives crashes/reboots:

```bash
pip install -r requirements.txt
python -m database.seed        # first run only
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 1
```

Use exactly 1 worker if a physical camera is attached — multiple workers
would each try to open the same camera device and conflict. On Windows,
wrap this in a Scheduled Task or NSSM service; on Linux, a systemd unit.

Example systemd unit (`/etc/systemd/system/inventory-ai.service`):

```ini
[Unit]
Description=AI Inventory Verification Backend
After=network.target

[Service]
WorkingDirectory=/opt/inventory_ai
ExecStart=/opt/inventory_ai/.venv/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8000
Restart=on-failure
Environment=INV_CAMERA_SOURCE=0

[Install]
WantedBy=multi-user.target
```

### Option B: GPU inference server + separate camera-edge box

If the camera is physically distant from the inference server, capture
frames on an edge device and POST them to a variant of `/api/verify` that
accepts an uploaded frame instead of pulling from a local `VideoCapture`
(extend `backend/api/verify.py` accordingly — the verification/counting
logic is already decoupled from camera capture, so this only touches the
API layer).

## Frontend

Build a static bundle and serve it from any static host or the same
machine via nginx:

```bash
cd dashboard
npm run build      # outputs dashboard/dist
```

Serve `dashboard/dist` and reverse-proxy `/api/*` to the backend. Example
nginx config:

```nginx
server {
    listen 80;
    root /opt/inventory_ai/dashboard/dist;
    location / { try_files $uri /index.html; }
    location /api/ { proxy_pass http://127.0.0.1:8000/api/; }
}
```

## Database

SQLite is fine for a single-site deployment. For multi-site or
high-concurrency needs, swap `INV_DATABASE_URL` to a Postgres URL — the
SQLAlchemy models require no changes, only the connection string.

## Environment Variables Checklist

| Variable | Purpose |
|---|---|
| `INV_CAMERA_SOURCE` | Camera index or stream URI |
| `INV_RTDETR_CHECKPOINT` | Path to fine-tuned model (or HF hub id) |
| `INV_RTDETR_DEVICE` | `cpu` or `cuda` |
| `INV_DATABASE_URL` | Override the default SQLite path/engine |
| `INV_DEBUG` | Set `false` in production to reduce log verbosity |
