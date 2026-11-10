# BuildEstimate — Construction Estimating Demo

A small, functional estimating application for general contractors. Built to demonstrate **Python backend development, configurable data, business-rule calculations, input validation, a browser UI, and automated testing**.

> **Portfolio demonstration, not a production estimating system.** All catalog costs are fabricated example values, **not verified supplier quotes**. Verify local labor, tax rules, permit requirements, takeoffs, vendor prices and contract terms before using any output commercially.

## What it does

- Loads construction items, unit material costs and labor-hour assumptions from an editable CSV price book.
- Estimates material expense with waste, labor by labor hours and hourly rate, material-only tax, overhead, profit markup, and suggested customer price.
- Displays line-item calculations and a cost breakdown. Exports structured JSON, and supports browser print / save as PDF.
- Rejects unknown catalog codes, invalid quantities, nonfinite numbers and invalid percentages.
- Separates deterministic computation (`app/estimator.py`) from the HTTP interface (`app/server.py`). Uses decimal money arithmetic and unit tests.

## Quick start

Requires **Python 3.10+**. No external Python packages required.

```bash
python -m app.server
```

Visit **http://127.0.0.1:8000**. Open the terminal from the repository root directory.

Run tests:

```bash
python -m unittest discover -s tests -v
```

## Project layout

```text
app/estimator.py     Calculation and validation engine
app/server.py        Simple local HTTP endpoints
web/index.html       Responsive HTML/CSS/JavaScript frontend
data/catalog.csv     Editable sample construction price book
tests/               Unit tests
```

## Calculation assumptions

For each line item:

- `materials = quantity × unit_material_cost × (1 + waste%)` (rounded to cents per item)
- `labor = quantity × labor_hours_per_unit × hourly_labor_rate` (rounded per item)

Across the project:

- `direct_cost = materials + labor + tax_on_materials`
- `overhead = direct_cost × overhead%`
- `profit_markup = (direct_cost + overhead) × profit_markup%`
- `estimated_price = direct_cost + overhead + profit_markup`

**Markup is different from gross margin.** To target a specific gross margin, the formula would need to change. The demo deliberately makes these assumptions explicit.

## API examples

`GET /api/catalog` — returns the price book.

`GET /api/health` — health check.

`POST /api/estimate`:

```json
{
  "project_name": "Kitchen Remodel",
  "labor_rate": 55,
  "waste_percent": 10,
  "overhead_percent": 12,
  "profit_markup_percent": 15,
  "material_tax_percent": 0,
  "items": [
    { "code": "CABINET", "quantity": 12 },
    { "code": "FLOOR", "quantity": 250 }
  ]
}
```

## Engineering choices and limitations

- The calculation engine is independent of any AI model: **AI can assist in extracting scope, but should never silently invent prices or quantities**.
- No customer information is saved to disk. The local web server listens on `127.0.0.1` by default.
- No login, database, vendor integrations, jurisdiction-specific tax rules, permit costs, contingency management, or change-order management is included.
- The local HTTP server is intended for evaluation only. It lacks production authentication, HTTPS, audit logs and rate limiting.

## Possible next iterations

1. Import a supplier's CSV price book with change history and validation.
2. Build an AI-assisted scope parser that proposes catalog-matched items **for human confirmation**.
3. Add estimates with versions, approvals, scope changes and comparison to actual costs.
4. Add an authenticated production API and CI workflow.

## Interview walkthrough (two minutes)

1. Show the CSV price book, then change a unit cost.
2. Add a line item and generate an estimate; show how costs flow through to the total.
3. Explain why Decimal, input validation, and explicit markup assumptions matter.
4. Run the unit tests and discuss the AI-assisted scope import as a controlled next step.

**Suggested resume bullet (only after you personally understand and can demonstrate it):**

> Built a Python-based construction estimating demo with configurable CSV price data, labor/material pricing, overhead and markup calculations, REST-style JSON endpoints, and automated tests.
