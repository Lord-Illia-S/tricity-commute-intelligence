FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project
COPY ingestion/ ./ingestion/
CMD [ "uv", "run", "--no-sync", "python", "ingestion/poll_live_feeds.py"]
