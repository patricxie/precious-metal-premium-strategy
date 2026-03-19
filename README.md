# Precious Metal Premium Strategy

Live dashboard:
[precious-metal-premium-strategy-aampauzxdfvbvwrafucckx.streamlit.app](https://precious-metal-premium-strategy-aampauzxdfvbvwrafucckx.streamlit.app/)

This project analyzes gold and silver futures data to generate mean-reversion trading signals, backtest those signals, and publish the results in a Streamlit dashboard.

## What This Project Does

- Extracts gold and silver futures prices from Yahoo Finance
- Builds rolling features and Z-score based signals
- Loads transformed data into SQLite
- Runs backtests and summary analytics
- Serves reports and charts through Streamlit

## Data Sources

- Futures: Yahoo Finance via `yfinance`
- Dashboard live market panel: Yahoo Finance symbols `GC=F`, `SI=F`, `GLD`, `SLV`

## Current ETL Flow

The primary ETL entrypoint is [`main.py`](/Users/patric/Desktop/資料工程師/Precious_Metal_ETL/main.py).

It runs:

1. [`extract/futures_yfinance.py`](/Users/patric/Desktop/資料工程師/Precious_Metal_ETL/extract/futures_yfinance.py)
2. [`transform/compute_signals.py`](/Users/patric/Desktop/資料工程師/Precious_Metal_ETL/transform/compute_signals.py)
3. [`load/to_sqlite.py`](/Users/patric/Desktop/資料工程師/Precious_Metal_ETL/load/to_sqlite.py)

Output locations:

- Raw futures CSV: [`extract/data`](/Users/patric/Desktop/資料工程師/Precious_Metal_ETL/extract/data)
- Transformed feature CSV: [`transform/data`](/Users/patric/Desktop/資料工程師/Precious_Metal_ETL/transform/data)
- SQLite database: [`database/precious_metal.db`](/Users/patric/Desktop/資料工程師/Precious_Metal_ETL/database/precious_metal.db)
- Processed reports and charts: [`data/processed`](/Users/patric/Desktop/資料工程師/Precious_Metal_ETL/data/processed)

## Health Check

[`check_pipeline.py`](/Users/patric/Desktop/資料工程師/Precious_Metal_ETL/check_pipeline.py) validates:

- Required CSV files exist
- Required columns exist
- Dates are valid and non-duplicated
- Latest rows are complete
- SQLite tables are populated

Run it with:

```bash
./.venv/bin/python check_pipeline.py
```

## Daily Update Flow

[`run_daily_update.py`](/Users/patric/Desktop/資料工程師/Precious_Metal_ETL/run_daily_update.py) runs:

1. ETL pipeline
2. Pipeline health check
3. Backtest analysis
4. Risk metrics
5. Summary tables
6. Equity curve comparison
7. Backtest charts
8. Z-score signal charts

It also updates:

- [`data/processed/daily_update_log.txt`](/Users/patric/Desktop/資料工程師/Precious_Metal_ETL/data/processed/daily_update_log.txt)
- [`data/processed/last_update.json`](/Users/patric/Desktop/資料工程師/Precious_Metal_ETL/data/processed/last_update.json)

Run it with:

```bash
./.venv/bin/python run_daily_update.py
```

## Strategy Logic

The signal generation in the current ETL pipeline is based on rolling deviation from MA20:

- `dev_ma20 = (close - ma_20) / ma_20`
- Rolling Z-score is computed from `dev_ma20`
- `BUY` when `dev_ma20_z <= -1.5` and trend is up
- `SELL` when `dev_ma20_z >= 1.5` and trend is down
- Otherwise `HOLD`

Feature output columns include:

- `close`
- `ret_1d`
- `ma_20`
- `ma_60`
- `dev_ma20`
- `dev_ma20_z`
- `trend_up`
- `trend_down`
- `signal`

## Local Setup

Clone the repository:

```bash
git clone https://github.com/patricxie/precious-metal-premium-strategy.git
cd precious-metal-premium-strategy
```

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run ETL:

```bash
./.venv/bin/python main.py
```

Run full daily update:

```bash
./.venv/bin/python run_daily_update.py
```

Launch the dashboard locally:

```bash
./.venv/bin/python -m streamlit run dashboard_app.py
```

## Streamlit Deployment

This app can be deployed on Streamlit Community Cloud.

Deployment settings:

- Repository: `patricxie/precious-metal-premium-strategy`
- Branch: `main`
- Main file path: `dashboard_app.py`

Deployment steps:

1. Sign in at [share.streamlit.io](https://share.streamlit.io)
2. Connect your GitHub account
3. Create a new app
4. Select the repository and branch
5. Set the main file path to `dashboard_app.py`
6. Deploy

Notes:

- Dependency changes in `requirements.txt` trigger reinstallation on Streamlit Community Cloud.
- The dashboard reads committed CSV outputs from [`data/processed`](/Users/patric/Desktop/資料工程師/Precious_Metal_ETL/data/processed), so the repo should contain fresh processed data before deployment.

Official docs:

- [Streamlit Community Cloud](https://docs.streamlit.io/deploy/streamlit-community-cloud)
- [Manage your app](https://docs.streamlit.io/deploy/streamlit-community-cloud/manage-your-app)

## Project Structure

```text
Precious_Metal_ETL/
├── extract/
│   ├── data/
│   └── futures_yfinance.py
├── transform/
│   ├── data/
│   ├── calculate_premium.py
│   └── compute_signals.py
├── load/
│   ├── save_to_csv.py
│   └── to_sqlite.py
├── data/
│   └── processed/
├── database/
├── dashboard_app.py
├── check_pipeline.py
├── main.py
├── run_daily_update.py
└── requirements.txt
```

## Dashboard Features

- Live market panel
- Latest signal summary
- Backtest detail table
- Risk metrics table
- Equity curve comparison
- Z-score signal charts
- Portfolio simulation
- Exported report artifacts

## Notes

- [`transform/calculate_premium.py`](/Users/patric/Desktop/資料工程師/Precious_Metal_ETL/transform/calculate_premium.py) and [`load/save_to_csv.py`](/Users/patric/Desktop/資料工程師/Precious_Metal_ETL/load/save_to_csv.py) are legacy premium-analysis scripts and are not part of the primary `main.py` ETL flow.
- The dashboard still reads processed premium-analysis outputs, so daily update artifacts should remain up to date if you want the hosted app to reflect the latest analytics.

## Author

Patric Xie
