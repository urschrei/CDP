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
FROM ghcr.io/astral-sh/uv:0.12.13-python3.14-trixie-slim
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_NO_DEV=1 \
    UV_PYTHON_DOWNLOADS=0
WORKDIR /app

# The photographs change less often than the code, so their layer comes first.
COPY media/instance media/instance

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=.python-version,target=.python-version \
    uv sync --locked --no-install-project

COPY pyproject.toml uv.lock .python-version README.md ./
COPY src src
COPY migrations migrations
COPY --from=assets /app/src/cdpp/static/dist src/cdpp/static/dist
RUN --mount=type=cache,target=/root/.cache/uv uv sync --locked

COPY db_dumps/cdpp.sql db_dumps/cdpp.sql
COPY --chmod=755 deploy/start.sh deploy/start.sh
RUN useradd --system --user-group --home-dir /app cdpp \
    && mkdir -p /data /app/instance \
    && chown cdpp:cdpp /data /app/instance

# Mount the database volume on /data. deploy/start.sh starts as root, and
# starts the application as the user cdpp.
ENV PATH="/app/.venv/bin:$PATH" \
    CDPP_SQLALCHEMY_DATABASE_URI=sqlite:////data/cdpp.sqlite3 \
    CDPP_MEDIA_ROOT=/app/media
EXPOSE 8000

# The Git commit and the jj change ID of the code, for the metadata of
# downloaded photographs. They are the last layer, so a new commit does not
# build the other layers again.
ARG CDPP_COMMIT CDPP_CHANGE
ENV CDPP_COMMIT=$CDPP_COMMIT \
    CDPP_CHANGE=$CDPP_CHANGE
CMD ["deploy/start.sh"]
