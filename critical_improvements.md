# Critical Improvements — Pre Dockerization

This document contains mandatory architectural and infrastructure improvements that should be implemented before Dockerization.

The purpose is to:

* avoid infrastructure instability
* prevent scaling bottlenecks
* reduce Docker debugging complexity
* improve deployment reliability
* stabilize request lifecycle behavior
* prepare the application for future worker/Redis integration

This is NOT a rewrite plan.

All improvements are intentionally incremental and non-destructive.

---

# Priority Order

## Critical Priority

Must be implemented before Dockerization.

* Gunicorn migration
* Environment variable management
* Retry + timeout handling
* Structured error handling
* JSON repair fallback
* Rate limiting
* CORS restriction
* .dockerignore
* File path normalization

---

## High Priority

Should ideally be completed before Dockerization.

* Logging system
* Health checks
* File cleanup lifecycle
* Upload validation
* Generated artifact cleanup
* Backend/frontend structure stabilization

---

## Medium Priority

Can be completed after Dockerization.

* React optimization
* Service decomposition
* Redis migration
* Worker extraction
* Background task orchestration

---

# 1. Replace Flask Development Server With Gunicorn

## Problem

Current backend execution uses:

```python
python app.py
```

The Flask development server:

* is not production-safe
* has poor concurrency handling
* blocks under slow requests
* performs poorly under load
* is unstable for containerized environments

---

## Required Change

Install:

```text
gunicorn
```

Replace runtime command with:

```dockerfile
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "app:app"]
```

---

## Benefits

* improved concurrency
* production-grade request handling
* stable worker management
* better Docker runtime behavior
* cleaner process lifecycle

---

# 2. Add Environment Variable Management

## Problem

Secrets and configuration are not fully centralized.

This creates:

* deployment instability
* onboarding friction
* secret leakage risk
* Docker configuration problems

---

## Required Files

Create:

```text
.env
.env.example
```

---

## Required Variables

```env
OPENAI_API_KEY=
GROQ_API_KEY=
SECRET_KEY=
FLASK_ENV=development
```

---

## Required Implementation

Create:

```text
backend/config/settings.py
```

Use:

```python
from dotenv import load_dotenv
import os

load_dotenv()
```

Centralize all environment reads.

---

## Benefits

* secure secret handling
* simplified Docker env injection
* cleaner deployments
* easier CI/CD later

---

# 3. Add Retry + Timeout Layer

## Problem

External APIs currently have:

* no retries
* no request timeout enforcement
* unstable failure behavior

This can:

* freeze workers
* block request lifecycle
* create cascading failures

---

## Required Implementation

Create:

```text
services/utils/retry.py
```

Implement:

* exponential backoff
* retryable exception filtering
* timeout wrapping
* centralized retry handling

---

## Retry Conditions

Retry only:

* 429
* 502
* 503
* timeout
* temporary connection failures

Do NOT retry:

* invalid input
* malformed schemas
* authentication failures

---

## Required Timeouts

All external calls must define explicit:

```python
timeout=60
```

Applies to:

* OpenAI
* Groq
* requests
* job APIs
* scraping logic

---

## Benefits

* stabilizes request lifecycle
* prevents hangs
* improves resilience
* improves scalability under load

---

# 4. Add JSON Repair Fallback

## Problem

LLM JSON parsing is fragile.

Malformed outputs currently crash request flows.

Common failures:

* trailing commas
* malformed quotes
* broken markdown fences
* partial JSON

---

## Required Dependency

Install:

```text
json-repair
```

---

## Required Parsing Flow

```text
json.loads
↓
json_repair.loads
↓
partial object extraction
```

---

## Benefits

* dramatically improves LLM stability
* reduces random extraction failures
* prevents malformed output crashes

---

# 5. Add Structured Error Handling

## Problem

Current errors are inconsistent.

Potential issues:

* internal stack leakage
* unstable frontend behavior
* unpredictable API responses

---

## Required Implementation

Create:

```text
services/utils/errors.py
```

Standard response format:

```json
{
  "success": false,
  "error": "User-safe message",
  "code": "INTERNAL_ERROR"
}
```

---

## Benefits

* predictable frontend contracts
* safer deployments
* easier debugging
* consistent API behavior

---

# 6. Add Rate Limiting

## Problem

Current API has no request throttling.

This creates:

* API budget drain risk
* denial-of-service risk
* accidental spam risk

---

## Required Dependency

Install:

```text
flask-limiter
```

---

## Required Limits

| Endpoint   | Limit  |
| ---------- | ------ |
| /upload    | 10/min |
| /find-jobs | 5/min  |
| /enhance   | 10/min |

---

## Benefits

* protects infrastructure
* protects API costs
* stabilizes concurrent usage

---

# 7. Restrict CORS

## Problem

Current CORS configuration is too permissive.

This allows:

* arbitrary frontend access
* unauthorized API consumption
* unnecessary security exposure

---

## Required Change

Restrict allowed origins.

Development:

```python
http://localhost:5173
```

Production:

```python
https://yourdomain.com
```

---

## Benefits

* safer API exposure
* cleaner deployment boundaries
* reduced attack surface

---

# 8. Add .dockerignore Files

## Problem

Without .dockerignore:

Docker build context becomes unnecessarily large.

This causes:

* slow builds
* massive image contexts
* cache invalidation
* poor developer experience

---

## Required Backend .dockerignore

```dockerignore
__pycache__/
*.pyc
.env
cache/
generated/
uploads/
.git
node_modules
```

---

## Required Frontend .dockerignore

```dockerignore
node_modules
dist
.git
.env
```

---

## Benefits

* faster Docker builds
* smaller images
* improved caching
* cleaner containerization

---

# 9. Normalize File Paths

## Problem

Current architecture risks OS-specific path assumptions.

This creates:

* Linux incompatibility
* Docker instability
* path resolution bugs

---

## Required Change

Use:

```python
from pathlib import Path
```

Avoid:

```python
"C:\\path\\file"
```

Avoid implicit relative paths.

---

## Benefits

* cross-platform compatibility
* Docker-safe filesystem handling
* cleaner path management

---

# 10. Add Upload Validation

## Problem

Uploads are insufficiently constrained.

Potential issues:

* oversized files
* malformed PDFs
* OCR crashes
* memory spikes

---

## Required Validation

Validate:

* MIME type
* extension
* file size
* corruption state

---

## Recommended Limits

```text
10MB upload limit
```

---

## Benefits

* safer processing pipeline
* prevents abuse
* improves reliability

---

# 11. Add Generated Artifact Cleanup

## Problem

Generated directories currently grow indefinitely.

This causes:

* disk growth
* Docker volume bloat
* deployment instability

---

## Required Cleanup Targets

* generated PDFs
* temporary OCR images
* stale uploads
* temp rendering artifacts

---

## Recommended Retention

```text
24 hours
```

---

## Benefits

* stable storage usage
* cleaner deployments
* simpler Docker persistence later

---

# 12. Add Logging System

## Problem

Current architecture uses print statements.

This limits:

* observability
* debugging
* production diagnostics

---

## Required Implementation

Create:

```text
services/utils/logger.py
```

Use:

```python
import logging
```

---

## Required Logging Levels

* INFO
* WARNING
* ERROR
* DEBUG

---

## Benefits

* production visibility
* easier debugging
* Docker log compatibility
* infrastructure monitoring readiness

---

# 13. Add Health Checks

## Problem

Containers currently have no runtime validation.

This limits:

* restart reliability
* orchestration readiness
* uptime monitoring

---

## Required Docker Healthcheck

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:5000"]
  interval: 30s
  timeout: 10s
  retries: 3
```

---

## Benefits

* container recovery readiness
* orchestration compatibility
* runtime visibility

---

# 14. Stabilize Backend/Frontend Separation

## Problem

Project structure is still partially transitional.

This increases:

* Docker complexity
* build confusion
* import instability

---

## Recommended Structure

```text
project/
│
├── backend/
├── frontend/
├── docker/
└── docs/
```

---

## Benefits

* cleaner Docker contexts
* easier dependency isolation
* simpler CI/CD later

---

# 15. Keep Architecture As Modular Monolith

## Important

Do NOT introduce yet:

* Kubernetes
* Redis workers
* Celery
* nginx reverse proxy
* distributed queues
* microservices

The current architecture is not mature enough to justify them.

---

# Correct Architectural Direction

```text
Current Monolith
        ↓
Stable Modular Monolith
        ↓
Dockerized Modular Monolith
        ↓
Redis-backed Task Queue
        ↓
Worker Separation
```

NOT:

```text
Monolith
↓
Immediate Distributed Systems
```

---

# Recommended Docker Scope

Initial Docker implementation should contain ONLY:

```text
frontend container
backend container
```

No Redis yet.

No worker containers yet.

No nginx yet.

---

# Final Objective

The goal is to:

* stabilize request lifecycle behavior
* reduce infrastructure fragility
* improve scalability incrementally
* prepare for future queue-based processing
* simplify Dockerization
* improve deployment readiness

without introducing architectural breakpoints or destructive rewrites.
