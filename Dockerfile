# Multi-stage: wheels are built in the builder, only the runtime is shipped.
# The base image is pinned by tag AND digest — a tag can be moved, a digest cannot.
FROM python:3.12.12-slim-bookworm@sha256:593bd06efe90efa80dc4eee3948be7c0fde4134606dd40d8dd8dbcade98e669c AS builder

WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


FROM python:3.12.12-slim-bookworm@sha256:593bd06efe90efa80dc4eee3948be7c0fde4134606dd40d8dd8dbcade98e669c AS runtime

# Non-root. Created before COPY so the files land owned by nobody writable.
RUN useradd --create-home --uid 10001 --shell /usr/sbin/nologin appuser

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH=/install/bin:$PATH \
    PYTHONPATH=/install/lib/python3.12/site-packages \
    PORT=8080

WORKDIR /srv
COPY --from=builder /install /install
COPY --chown=root:root app ./app

USER appuser
EXPOSE 8080

# Shell form would make PID 1 a shell and swallow SIGTERM, so the exec form
# matters: it is what lets a `docker stop` or a pod eviction shut down cleanly.
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--access-logfile", "-", "app:create_app()"]
