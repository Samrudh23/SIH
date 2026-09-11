# SIH26034 — Production Deployment & Release Engineering Guide

> **Official Release & Hosting Specification for SIH26034 Packaged Commodities Compliance Scanner**
> Prepared by: **P6 Deployment & Release Engineering**
> Current Version: `1.0.0` (Production Ready)
> Supported Environments: Docker, Docker Compose, Render, Railway, Vercel/Netlify, Linux/Windows Bare-Metal

---

## Table of Contents
1. [System Architecture & Topology](#1-system-architecture--topology)
2. [Hosting & Infrastructure Decisions](#2-hosting--infrastructure-decisions)
3. [Environment Variables Reference](#3-environment-variables-reference)
4. [Deployment Modes](#4-deployment-modes)
   - [Mode A: Unified Full-Stack Production Container (Recommended for SIH)](#mode-a-unified-full-stack-production-container-recommended-for-sih)
   - [Mode B: Decoupled Architecture (Static Frontend + Hosted FastAPI)](#mode-b-decoupled-architecture-static-frontend--hosted-fastapi)
5. [Local Development & Production Commands](#5-local-development--production-commands)
6. [Containerization & Orchestration](#6-containerization--orchestration)
7. [Cloud Deployment Procedures (Render, Railway, Fly.io)](#7-cloud-deployment-procedures)
8. [Health Check & Automated Smoke Testing](#8-health-check--automated-smoke-testing)
9. [Backup, Restore & Persistence](#9-backup-restore--persistence)
10. [Troubleshooting & FAQs](#10-troubleshooting--faqs)
11. [Known Operational Limitations](#11-known-operational-limitations)

---

## 1. System Architecture & Topology

```
+-----------------------------------------------------------------------------+
|                                END USERS                                    |
|             (Enforcement Officers / Legal Metrology Inspectors)             |
+-----------------------------------------------------------------------------+
                                       |
                                       | HTTPS (Port 8000 / 443)
                                       v
+-----------------------------------------------------------------------------+
|                 SIH26034 UNIFIED PRODUCTION SERVICE (Uvicorn / FastAPI)      |
|                                                                             |
|  +-------------------------------------+  +------------------------------+  |
|  |       INSPECTOR PORTAL (SPA)        |  |        REST API ROUTER       |  |
|  |  Vanilla ES6+ Modules + Tailwind    |  |  FastAPI Lifespan & Engines  |  |
|  |  - Dashboard View                   |  |  - /api/health (Healthcheck) |  |
|  |  - New Inspection & Camera Capture  |  |  - /api/inspections          |  |
|  |  - Multi-Surface Evidence Viewer    |  |  - /api/extractions (P1)     |  |
|  |  - Real Compliance Findings (P2)    |  |  - /api/analysis (P2 Engine) |  |
|  |  - Medical Device Confirmation Gate |  |  - /api/dashboard            |  |
|  |  - Manual Review & Conflict Center  |  |  - /api/reports (JSON & HTML)|  |
|  |  - Printable Statutory Reports      |  |  - /api/images (Safe Stream) |  |
|  +-------------------------------------+  +------------------------------+  |
|                      |                                   |                  |
+----------------------|-----------------------------------|------------------+
                       |                                   |
                       v                                   v
+------------------------------------+    +-----------------------------------+
|         PERSISTENT DATABASE        |    |      PERSISTENT EVIDENCE DISK     |
|   SQLite (WAL Mode enabled) or     |    |   Sanitized UUID Image Store      |
|   PostgreSQL via DATABASE_URL      |    |   Path Traversal Guarded          |
|   Mount: /data/db/sih26034.db      |    |   Mount: /data/uploads            |
+------------------------------------+    +-----------------------------------+
```

---

## 2. Hosting & Infrastructure Decisions

### Database Decision: SQLite with WAL (with Managed PostgreSQL Drop-In)
- **Primary Selection for SIH Hackathon**: SQLite (`sih26034.db`) mounted on a persistent volume.
- **Rationale**:
  1. **Zero External Dependencies**: Does not depend on external database clusters, preventing connectivity failures during live jury evaluation.
  2. **High Read/Write Performance**: SQLite in WAL (Write-Ahead Logging) mode comfortably handles hundreds of concurrent inspections with microsecond query latency.
  3. **Portability**: Database can be bundled or snapshotted instantaneously for offline jury verification.
- **Enterprise / Multi-Instance Scalability**: SQLAlchemy 2.0 connection abstraction allows zero-code migration to Managed PostgreSQL simply by supplying `DATABASE_URL=postgresql://user:pass@host:5432/dbname`.

### Evidence Storage Decision: Persistent Local Volume with Safe Streamer
- **Primary Selection for SIH Hackathon**: Dedicated disk storage mounted at `/data/uploads` or `./uploads`.
- **Rationale**:
  1. **Direct Path Validation**: Strict UUID-based file naming and path traversal checks prevent directory escaping vulnerabilities.
  2. **Zero Cloud Egress Overhead**: Images stream directly via FastAPI's `FileResponse` at `/api/images/{file_name}` without cloud bucket latency or credential expiration.
  3. **Integrity**: Evidence remains permanently bound to the inspection record across application restarts.

---

## 3. Environment Variables Reference

| Variable | Default Value | Production Recommendation | Purpose |
| :--- | :--- | :--- | :--- |
| `APP_ENV` | `development` | `production` | Enables production security constraints and disables test mocks. |
| `DEBUG` | `true` | `false` | Disables stack trace leakage and verbose debug logs. |
| `HOST` | `0.0.0.0` | `0.0.0.0` | Network interface to bind HTTP listener. |
| `PORT` | `8000` | `${PORT:-8000}` | Application HTTP listening port. |
| `DATABASE_URL` | `sqlite:///./sih26034.db` | `sqlite:////data/db/sih26034.db` | SQLAlchemy database connection URI. |
| `UPLOAD_DIR` | `./uploads` | `/data/uploads` | Path to package image evidence store. |
| `MAX_FILE_SIZE_BYTES` | `10485760` (10MB) | `10485760` | Maximum allowed package image upload size. |
| `ALLOWED_ORIGINS` | `localhost ports` | `https://your-domain.com` | Comma-separated list of CORS origins for decoupled mode. |
| `SERVE_FRONTEND` | `true` | `true` | Mounts the Inspector Portal static frontend directly on `/`. |
| `FRONTEND_DIR` | `./frontend` | `/app/frontend` | Directory containing `index.html` and `src/`. |
| `COMPLIANCE_ENGINE_TYPE`| `real` | `real` | Active compliance engine (`real` for P2 engine, `mock` for demo). |
| `WEB_CONCURRENCY` | `1` | `2` | Number of Uvicorn worker processes in container environments. |

---

## 4. Deployment Modes

### Mode A: Unified Full-Stack Production Container (Recommended for SIH)
FastAPI serves the REST API (`/api/*`), interactive API docs (`/docs`), and the Inspector Portal frontend (`/`, `/src/*`).
- **Advantages**:
  - Single hosted URL (e.g. `https://sih26034.onrender.com` or `http://localhost:8000`).
  - No CORS configuration issues.
  - Zero latency between frontend and backend.
  - Atomic releases (frontend and backend update in sync).

### Mode B: Decoupled Architecture (Static Frontend + Hosted FastAPI)
The frontend is hosted on Vercel, Netlify, or Cloudflare Pages, while the backend runs on Render, Railway, or Bare-Metal.
- **Configuration**:
  - Backend: set `ALLOWED_ORIGINS=https://sih26034.vercel.app`.
  - Frontend: configure `API_BASE_URL=https://sih26034-api.onrender.com/api` (or configure reverse proxy rewrites in `vercel.json` / `netlify.toml`).

---

## 5. Local Development & Production Commands

### Running Locally with Python Virtualenv
```bash
# 1. Activate virtual environment
# Windows:
backend\.venv\Scripts\activate
# Linux/macOS:
source backend/.venv/bin/activate

# 2. Run test suites
pytest backend/tests
node frontend/tests/runner.js

# 3. Launch unified production server
python scripts/start_production.py
```

### Running Backend & Frontend in Decoupled Development Mode
```bash
# Terminal 1: Backend API
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

# Terminal 2: Frontend Static Host
cd frontend
node server.js
# Access frontend on http://localhost:3000
```

---

## 6. Containerization & Orchestration

### Building and Running with Docker
```bash
# 1. Build the production multi-stage image
docker build -t sih26034-compliance-scanner:latest .

# 2. Run container with persistent data volumes
docker run -d \
  --name sih26034 \
  -p 8000:8000 \
  -v sih_db:/data/db \
  -v sih_uploads:/data/uploads \
  -e APP_ENV=production \
  -e DEBUG=false \
  sih26034-compliance-scanner:latest

# 3. Verify health
curl -f http://localhost:8000/api/health
```

### Orchestrating with Docker Compose
```bash
# Start service in detached mode
docker-compose up -d

# View container logs
docker-compose logs -f sih26034-app

# Run smoke tests against container
python scripts/smoke_test.py --target-url http://localhost:8000

# Stop service without losing persistent data
docker-compose down
```

---

## 7. Cloud Deployment Procedures

### Deploying to Render (1-Click Blueprint)
1. Fork or push the repository to GitHub.
2. In the Render Dashboard, select **New -> Blueprint**.
3. Point to the repository. Render automatically reads `render.yaml`:
   - Builds Python runtime with `requirements.txt`.
   - Attaches a 1GB persistent disk at `/var/data` for database and image storage.
   - Starts Uvicorn with 2 worker processes.
4. Deployment completes automatically.

### Deploying to Railway / Fly.io / GCP Cloud Run
- Attach a persistent volume for `/data`.
- Configure environment variables from `.env.example`.
- Expose port `8000` (or map `$PORT`).

---

## 8. Health Check & Automated Smoke Testing

### Liveness Healthcheck Endpoint
- **URL**: `GET /api/health`
- **Expected Status**: `200 OK`
- **Sample Response**:
  ```json
  {
    "status": "ok",
    "service": "sih26034-backend",
    "compliance_engine": "real",
    "environment": "production"
  }
  ```

### Executing Automated End-to-End Smoke Test Suite
The repository includes a dedicated 16-step smoke test suite validating the complete inspection lifecycle:
```bash
python scripts/smoke_test.py --target-url http://127.0.0.1:8000
```
**Test Lifecycle Stages Verified**:
1. API Health endpoint availability
2. Inspector Portal root asset delivery (`/`)
3. Static module and typography delivery (`/src/app.js`, `/src/styles/app.css`)
4. Operational KPI summary retrieval (`/api/dashboard/summary`)
5. Inspection creation with surface checklist (`POST /api/inspections`)
6. Package evidence image upload (`POST /api/inspections/{id}/image`)
7. Stored evidence image retrieval and streaming (`GET /api/images/{filename}`)
8. P1 Extraction payload ingestion with schema validation
9. P2 Compliance evaluation execution (`POST /api/inspections/{id}/analyze`)
10. Rule result status semantics verification across 15 legal rules
11. Multi-surface conflict detection (MRP & Net Quantity conflicts)
12. Medical Device Confirmation Gate toggling (Fix 2)
13. Inspector physical measurement notes persistence
14. Structured statutory JSON report generation
15. High-fidelity printable HTML report delivery
16. Database write persistence across subsequent queries

---

## 9. Backup, Restore & Persistence

### Backup
To create an offline backup of all inspection data:
```bash
# Copy SQLite database
cp sih26034.db sih26034_backup_$(date +%Y%m%d).db

# Archive uploads directory
tar -czvf uploads_backup_$(date +%Y%m%d).tar.gz uploads/
```

### Restore
```bash
# Restore SQLite database
cp sih26034_backup_YYYYMMDD.db sih26034.db

# Restore uploads
tar -xzvf uploads_backup_YYYYMMDD.tar.gz
```

---

## 10. Troubleshooting & FAQs

### Problem: `422 Unprocessable Entity` on Extraction Submission
- **Root Cause**: `ExtractionPayload` requires `raw_text` and `confidence` fields for each declared field.
- **Solution**: Ensure your payload contains `raw_text` for extracted components as specified in `docs/legal/Confidence_Status_Schema.md`.

### Problem: Port 8000 already in use
- **Solution**: Run on another port using environment variable:
  ```bash
  PORT=8080 python scripts/start_production.py
  ```
  The Inspector Portal automatically adapts to same-origin `/api` on any port.

### Problem: Upload fails with `File exceeds maximum allowed size`
- **Solution**: Adjust `MAX_FILE_SIZE_BYTES` in `.env` (default is 10MB: `10485760`).

---

## 11. Known Operational Limitations
1. **SQLite Write Concurrency**: SQLite safely handles multiple concurrent readers and sequential writes. For hyper-scale deployments exceeding >50 simultaneous write transactions per second, transition to PostgreSQL by setting `DATABASE_URL`.
2. **Ephemeral Containers**: On hosting platforms without persistent disks (e.g. standard Heroku free dynos), uploads and the SQLite database will reset upon container restart. Always use a persistent volume mount (`/data`) or cloud storage backends for production persistence.
