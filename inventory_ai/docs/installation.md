# Installation Guide

## Prerequisites

- **Python 3.11+**. On Windows, install from python.org (not the Microsoft
  Store stub) so `python`/`pip` resolve correctly, and check "Add Python to
  PATH" during install.
- **Node.js 18+** and npm, for the React dashboard.
- A webcam (built-in laptop camera works for initial development).
- Optional: an NVIDIA GPU + CUDA for faster RT-DETR inference (set
  `INV_RTDETR_DEVICE=cuda`). CPU inference works but is slower.

## Backend Setup

```bash
cd inventory_ai
python -m venv .venv
.venv\Scripts\activate        # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Generate the SQLite database with 100 dummy products and 1000 dummy
verification transactions:

```bash
python -m database.seed
```

This creates `inventory_ai/database/inventory.db`. Re-running is a no-op if
the database already has products (delete the file to reseed).

Start the API server:

```bash
uvicorn backend.main:app --reload --port 8000
```

Verify it's up: open http://localhost:8000/health — should return
`{"status": "ok", ...}`. Interactive API docs are at
http://localhost:8000/docs.

## Frontend Setup

```bash
cd inventory_ai/dashboard
npm install
npm run dev
```

Open http://localhost:5174. The dev server proxies `/api/*` requests to
`http://localhost:8000` (configured in `vite.config.js`), so both servers
must be running.

## Running Tests

```bash
cd inventory_ai
pip install -r requirements.txt   # includes pytest
pytest
```

## Configuration

All runtime settings live in `backend/config/settings.py` and can be
overridden via environment variables prefixed `INV_`, e.g.:

```bash
set INV_CAMERA_SOURCE=1
set INV_RTDETR_DEVICE=cuda
set INV_RTDETR_CONFIDENCE_THRESHOLD=0.6
```

Or place them in an `inventory_ai/.env` file (loaded automatically).
