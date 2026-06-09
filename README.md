# Private Markets Intelligence Platform

This project demonstrates how AI-assisted document intelligence can be combined with private-market cash-flow modelling, portfolio analytics, and liquidity stress testing to support institutional alternative-investment due diligence and monitoring.

## Scope

The current repository implements a working vertical slice for a synthetic Nordic infrastructure fund commitment use case. The pipeline:

1. Loads a synthetic infrastructure fund memo.
2. Extracts structured fund facts and risk findings.
3. Produces a deterministic due-diligence report.
4. Forecasts commitment cash flows under base and downside cases.
5. Adds the proposed commitment to a synthetic portfolio.
6. Runs a liquidity stress scenario.

The current implementation is deterministic by design. The LLM layer is abstracted behind a model-agnostic client interface, but the default provider is a mock client so the demo runs without external API access.

## What Is Implemented

- Synthetic investment memo and portfolio inputs in `data/`
- Shared domain models and config loading in `src/altintel/core/`
- Mock due-diligence extraction in `src/altintel/due_diligence/`
- Model-agnostic client interface in `src/altintel/llm/`
- Cash-flow forecast logic in `src/altintel/cashflows/`
- Portfolio summary and commitment impact logic in `src/altintel/portfolio/`
- Liquidity stress testing in `src/altintel/analytics/`
- End-to-end orchestration in `src/altintel/pipeline/`
- Demo entrypoints in `examples/`

## Repository Layout

```text
.
|-- configs/
|-- data/
|   |-- sample_documents/
|   `-- synthetic/
|-- docs/
|   `-- spec/
|-- examples/
|-- outputs/
|-- src/
|   `-- altintel/
|       |-- analytics/
|       |-- cashflows/
|       |-- core/
|       |-- data/
|       |-- due_diligence/
|       |-- llm/
|       |-- pipeline/
|       |-- portfolio/
|       `-- reporting/
`-- tests/
```

## Demo Data

The first vertical slice is centered on:

- `data/sample_documents/nordic_infrastructure_fund_v.md`
- `data/synthetic/proposed_commitment.json`
- `data/synthetic/portfolio_snapshot.json`
- `data/synthetic/cashflow_assumptions.json`

These files define a synthetic evaluation case for `Northlake Infrastructure Partners V`.

## Run

The code currently assumes Python 3.11+.

Install dependencies:

```bash
pip install -e .[dev]
```

Run the due-diligence demo:

```bash
python examples/run_ai_due_diligence.py
```

Run the full pipeline:

```bash
python examples/run_full_pipeline.py
```

If you are not installing the package in editable mode, set `PYTHONPATH=src` before running the examples.

## Current Output Shape

The full pipeline currently prints:

- extracted fund identity and risk rating
- portfolio NAV and unfunded commitments before and after the new commitment
- base-case forecast metrics
- downside-case forecast metrics
- liquidity stress result

The reporting layer for generated investment committee memos is planned but not implemented yet.

## Configuration

The main config files are:

- `configs/base.yml`
- `configs/model_config.yml`
- `configs/risk_taxonomy.yml`
- `configs/portfolio_policy.yml`

The default LLM provider is:

```text
mock
```

## Testing

Test files are present in `tests/`, but `pytest` must be installed in the active environment before running:

```bash
pytest
```

## Important Git Note

The current `.gitignore` ignores all `*.md` files. That means this `README.md` and other markdown documents will remain local unless the ignore rules are changed or explicit exceptions are added.

## Next Steps

- generate Markdown investment committee memos into `outputs/`
- enrich the cash-flow model with pacing and liquidity policy checks
- replace the mock due-diligence client with a real provider-backed implementation
- add broader tests around extraction, forecasting, and portfolio stress logic
