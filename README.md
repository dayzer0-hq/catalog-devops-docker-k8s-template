# Docker + Kubernetes starter

A small, runnable Python + [Flask](https://flask.palletsprojects.com/) service and the
operational scaffolding around it — a multi-stage Dockerfile, a two-service Compose stack,
and split Kubernetes manifests. It is the starting point for DayZer0 catalog briefs on this
stack. **The service already runs and its tests already pass**: your tickets are about
building, shipping, probing and operating it, so the thing being operated ships working.

## What's here

```
app/
    __init__.py          the application factory — register a new blueprint here
    config.py            EVERY environment variable this service reads, in one place
    health.py            GET /health (liveness) and GET /readyz (readiness) — probes live here
    items.py             GET/POST /items — the one real endpoint, in-memory
    db.py                the only place a database connection is opened
requirements.txt         runtime dependencies, pinned exactly
requirements-dev.txt     the above plus pytest
Dockerfile               multi-stage build, non-root user, base image pinned by tag + digest
.dockerignore            keeps the build context (and .env) out of the image
compose.yaml             app + Postgres 16.9, both with healthchecks
.env.example             the variables Compose needs — copy to .env, which is gitignored
k8s/
    configmap.yaml       non-secret configuration
    deployment.yaml      replicas, probes, resource limits, container hardening
    service.yaml         ClusterIP service on port 80 -> container port 8080
Makefile                 build / run / test / up / k8s-apply
tests/
    test_health.py       /health answers ok; /readyz fails when the database is unconfigured
    test_items.py        the endpoint lists, creates, and rejects a missing name
```

## Requirements

- **Python 3.12 or newer** (`python3 --version`) to run or test the app directly.
- **Docker** with Compose v2 (`docker compose version`) for the container work.
- **kubectl** and any cluster (minikube, kind, Docker Desktop) for the `k8s/` tickets.

You need Python for the tests. Docker and kubectl are needed only by the tickets that
mention them.

## Run it

Without a container:

```bash
make install
make run
```

Then, in another terminal:

```bash
curl http://localhost:8080/health      # {"status":"ok"}
curl http://localhost:8080/items       # {"items":[{"id":1,"name":"first item"}]}
curl http://localhost:8080/readyz      # 503 until a database is configured
```

With the full stack:

```bash
cp .env.example .env     # then edit it
make up
```

`/readyz` answers 200 once Postgres is healthy — that is the point of having two probes.

## Test it

```bash
make test
```

All tests pass on a clean clone — you start green.

## What you add

Your tickets. One concern per file, so there is one obvious place for each change:

| If a ticket asks you to… | the file is |
|---|---|
| add or change a probe | `app/health.py` (and the probe block in `k8s/deployment.yaml`) |
| read a new setting | `app/config.py`, then `k8s/configmap.yaml` |
| add an endpoint | a new module beside `app/items.py`, registered in `app/__init__.py` |
| talk to the database | `app/db.py` |
| shrink or harden the image | `Dockerfile`, `.dockerignore` |
| add a local dependency (cache, queue) | `compose.yaml` |
| scale, limit, or expose the service | `k8s/deployment.yaml`, `k8s/service.yaml` |

## Secrets

**Nothing in this repository is a credential, and nothing you add should be.**

- Compose reads `POSTGRES_PASSWORD` from your `.env`, which is gitignored. The `:?`
  syntax in `compose.yaml` makes it refuse to start when that variable is unset, rather
  than falling back to something guessable.
- Kubernetes reads `DATABASE_URL` from a Secret named `catalog-db` that is deliberately
  **not** a file here. Create it out of band:

  ```bash
  kubectl create secret generic catalog-db \
    --from-literal=DATABASE_URL='postgresql://app:PASSWORD@HOST:5432/app'
  ```

- Every other setting is non-secret and lives in `k8s/configmap.yaml`.

## What is already hardened

Worth knowing before a ticket asks you to change it, because undoing one of these is easy
to do by accident:

- The container runs as **`appuser` (uid 10001)**, not root, and the Deployment asserts
  `runAsNonRoot` so a future image that forgets `USER` fails to schedule instead of
  quietly running as root.
- Both base images are pinned by **tag and digest**. A tag can be moved under you; a
  digest cannot. Pin whatever you add the same way, and never use `:latest`.
- The container drops **all capabilities**, forbids privilege escalation, and runs with a
  **read-only root filesystem** — which is why `/tmp` is mounted as an `emptyDir`.
- The Deployment sets both **requests and limits** for CPU and memory. A pod with no limit
  is a pod that can take a node down with it.
- `CMD` is in exec form, so the process is PID 1 and receives `SIGTERM` — without that a
  `docker stop` or a pod eviction waits out the grace period and then kills it.
