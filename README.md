# Tricity Commute Intelligence

Live tracking and prediction of bus and tram delays in Gdańsk and Gdynia.

## MVP scope (due 13 Dec 2026)
- **In:** live delays for Gdańsk + Gdynia buses and trams, joined with weather data, shown on a Streamlit dashboard.
- **Stretch:** SKM (train) real-time data.
- **Out (for now):** delay prediction model; it comes after the MVP.


## Architecture

_Coming soon._

## Tech stack

- Python 3.12, managed with [uv](https://docs.astral.sh/uv/)
- Linting and formatting: [ruff](https://docs.astral.sh/ruff/)
- Git hooks: [pre-commit](https://pre-commit.com/)

## Getting started

1. Install uv: see the [installation guide](https://docs.astral.sh/uv/getting-started/installation/).
For Windows: powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
For Linux/Mac: curl -LsSf https://astral.sh/uv/install.sh | sh
2. Clone the repo and install dependencies:

   ```bash
   git clone https://github.com/Lord-Illia-S/tricity-commute-intelligence.git
   cd tricity-commute-intelligence
   uv sync
   ```

3. Install the git hooks and copy .env.example to .env:

   ```bash
   uv run python -m pre_commit install
   cp .env.example .env
   ```

4. Run all checks manually:

   ```bash
   uv run python -m pre_commit run --all-files
   uv run pytest
   ```

   Both should pass. If they do, you're ready to open your first PR.

To download static GTFS run the command:
   ```bash
   uv run ingestion/download_static_gtfs.py
   ```
To test the downloading without acces to the internet(using MagicMock and patch) run the command:
   ```bash
   uv run pytest
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

1. Gdansk static GTFS: https://ckan.multimediagdansk.pl/dataset/c24aa637-3619-4dc2-a171-a23eec8f2172/resource/30e783e4-2bec-4a7d-bb22-ee3e3b26ca96/download/gtfsgoogle.zip
2. Gdynia static GTFS: https://api.zdiz.gdynia.pl/pt/gtfs.zip
3. SKM static GTFS:  https://www.skm.pkp.pl/gtfs-mi-kpd.zip

## Roadmap

_Coming soon._

## Team

- Illia Święcicki
- Vlad Zemliakov
