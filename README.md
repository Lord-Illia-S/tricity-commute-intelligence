# Tricity Commute Intelligence

Live tracking and prediction of bus and tram delays in Gdańsk and Gdynia.

## Architecture

_Coming soon._

## Tech stack

- Python 3.12, managed with [uv](https://docs.astral.sh/uv/)
- Linting and formatting: [ruff](https://docs.astral.sh/ruff/)
- Git hooks: [pre-commit](https://pre-commit.com/)

## Getting started

1. Install uv: see the [installation guide](https://docs.astral.sh/uv/getting-started/installation/).
2. Clone the repo and install dependencies:

   ```bash
   git clone https://github.com/Lord-Illia-S/tricity-commute-intelligence.git
   cd tricity-commute-intelligence
   uv sync
   ```

3. Install the git hooks:

   ```bash
   uv run python -m pre_commit install
   ```

4. Run all checks manually:

   ```bash
   uv run python -m pre_commit run --all-files
   ```

## Project structure

```
ingestion/       # pollers that fetch the live feeds
transform/       # dbt models
orchestration/   # Dagster pipelines
dashboard/       # Streamlit app
notebooks/       # exploration
tests/           # tests
docs/adr/        # architecture decision records
```

## Data sources

_Coming soon._

## Roadmap

_Coming soon._

## Team

- Illia Święcicki
- Wlad
