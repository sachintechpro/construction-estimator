# BuildEstimate — Construction Estimating Demo

**[Try the live application](https://buildestimate-82xs.onrender.com)** · [Browse source code](./construction-estimator-showcase/) · [Automated tests](https://github.com/sachintechpro/construction-estimator/actions)

A working, browser-based construction estimating portfolio project. Calculate material costs, labor, waste, material tax, overhead, and profit markup using an editable CSV price catalog.

## What this project demonstrates

- **Python backend and API:** HTTP endpoints for catalog data, health checks, and estimates
- **Business rules:** reproducible, decimal-based line-item and project-total calculations
- **Data-driven configuration:** edit construction costs and labor assumptions in CSV without changing code
- **Frontend:** responsive HTML, CSS, and JavaScript interface
- **Quality engineering:** automated unit tests and GitHub Actions continuous integration

## Live demo

**https://buildestimate-82xs.onrender.com**

Choose construction items, adjust quantities and rate assumptions, then click **Calculate estimate**. Export JSON or use **Print / Save PDF**. On Render's free tier, the site may take extra time to wake up after inactivity.

> **Portfolio demonstration only.** Cost data is illustrative, not live supplier quotes. Estimates should not be used as binding bids.

## Architecture

```text
Browser UI (web/index.html)
           |
           | HTTP / JSON
           v
Python server (app/server.py)
           |
           v
Estimate engine (app/estimator.py)
           |
           v
CSV price catalog (data/catalog.csv)
```

The calculation engine is deliberately independent of any AI model. Computed totals are deterministic and auditable. Future AI-assisted scope interpretation would require user confirmation, never invented prices.

## Run locally

Requires Python 3.10+ with no external dependencies.

```bash
git clone https://github.com/sachintechpro/construction-estimator.git
cd construction-estimator/construction-estimator-showcase
python -m app.server
```

Open `http://127.0.0.1:8000`.

### Run the automated tests

From the `construction-estimator-showcase` directory:

```bash
python -m unittest discover -s tests -v
```

The same tests run on GitHub Actions for every push or pull request to `main`.

## Source code

| Component | Location |
| --- | --- |
| Cost engine and validation | [`app/estimator.py`](./construction-estimator-showcase/app/estimator.py) |
| Backend HTTP server | [`app/server.py`](./construction-estimator-showcase/app/server.py) |
| Web interface | [`web/index.html`](./construction-estimator-showcase/web/index.html) |
| Editable cost catalog | [`data/catalog.csv`](./construction-estimator-showcase/data/catalog.csv) |
| Automated tests | [`tests/test_estimator.py`](./construction-estimator-showcase/tests/test_estimator.py) |
| Detailed technical guide | [`Project README`](./construction-estimator-showcase/README.md) |

## Current limitations

This is an engineering demo rather than a production bidding service: no authentication, customer database, live vendor pricing, jurisdiction-specific taxes, permit costs, change-order management, or production-grade rate limiting. The Python HTTP server is intentionally lightweight.
