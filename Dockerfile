# syntax=docker/dockerfile:1

# Build the front-end assets.
FROM node:22-slim AS assets
WORKDIR /app
COPY package.json package-lock.json ./
RUN --mount=type=cache,target=/root/.npm npm ci
COPY frontend frontend
COPY src/cdpp/templates src/cdpp/templates
RUN npm run build

# Install the application.
FROM astral/uv:0.12-python3.14-trixie-slim
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_NO_DEV=1 \
    UV_PYTHON_DOWNLOADS=0
WORKDIR /app

COPY pyproject.toml uv.lock .python-version README.md ./
RUN --mount=type=cache,target=/root/.cache/uv uv sync --locked --no-install-project
COPY src src
COPY migrations migrations
COPY --from=assets /app/src/cdpp/static/dist src/cdpp/static/dist
RUN --mount=type=cache,target=/root/.cache/uv uv sync --locked

RUN useradd --system --home-dir /app cdpp \
    && mkdir -p /data /app/instance \
    && chown cdpp /data /app/instance
USER cdpp

# Mount the database volume on /data and the images on /app/media.
ENV PATH="/app/.venv/bin:$PATH" \
    CDPP_SQLALCHEMY_DATABASE_URI=sqlite:////data/cdpp.sqlite3 \
    CDPP_MEDIA_ROOT=/app/media
EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "cdpp:create_app()"]
