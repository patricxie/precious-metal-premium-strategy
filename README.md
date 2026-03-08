## Live Dashboard

(http://192.168.1.105:8501)
# Precious Metal Premium Mean-Reversion Strategy

This project analyzes the **premium spread between futures and spot prices of gold and silver** to identify potential mean-reversion trading opportunities.

The project includes:

- Data extraction (ETL pipeline)
- Premium calculation
- Z-score signal generation
- Backtesting framework
- Risk metrics evaluation
- Interactive Streamlit dashboard

---

# Project Overview

In commodity markets, the price difference between **futures and spot markets** (premium) can reflect market expectations, liquidity, and short-term demand.

This project studies whether **extreme deviations in premium** tend to revert to the mean and whether those signals can be used for trading.

Core idea:

When premium deviates significantly from its historical mean:

- **Z-score < -2 → BUY signal**
- **Z-score > +2 → SELL signal**

---

# Data Sources

The project collects data from the following APIs:

### Futures prices
Yahoo Finance

Gold Futures

Silver Futures

### Spot prices
Alpha Vantage API

Gold Spot  
Silver Spot

---

# ETL Pipeline

The data pipeline performs the following steps:

### Extract
Fetch futures and spot data

### Transform
Calculate:

- futures price
- spot price
- premium
- rolling mean
- rolling standard deviation
- Z-score signal

### Load
Store processed results in:

---

# Strategy Logic

Premium is defined as:

Z-score:

Trading rules:

| Condition | Signal |
|--------|--------|
| Z < -2 | BUY |
| Z > +2 | SELL |
| otherwise | HOLD |

---

# Backtest Results (2 Years)

Backtest window:

Key results:

| Strategy | Return |
|--------|--------|
Silver BUY 20D | **317%**
Silver BUY 10D | 111%
Gold BUY 20D | 73%

Average statistics include:

- win rate
- max drawdown
- volatility
- Sharpe ratio

---

# Risk Metrics

Example metrics:

| Asset | Signal | Holding | Win Rate | Max Drawdown | Sharpe |
|------|------|------|------|------|------|
Silver | BUY | 20D | 83% | -9.5% | 0.59
Gold | BUY | 20D | 68% | -4.4% | 0.56

---

# Strategy Visualization

Example outputs include:

### Equity Curve
Strategy capital growth comparison.

### Z-score signal chart
Shows premium deviations and trading signals.

### Backtest summary charts
Performance comparison across holding periods.

---

# Interactive Dashboard

This project includes a **Streamlit dashboard** to explore:

- backtest performance
- risk metrics
- strategy comparison
- equity curves

Run locally:

---

# Project Structure
Precious_Metal_ETL
│
├── extract
│
├── transform
│
├── load
│
├── analysis
│
├── dashboard_app.py
│
├── main.py
│
└── requirements.txt

---

# Installation

Clone repository:
git clone https://github.com/YOUR_USERNAME/precious-metal-premium-strategy.git

Run ETL pipeline:
python main.py

Launch dashboard:
streamlit run dashboard_app.py

---

# Skills Demonstrated

This project demonstrates the following data and quantitative skills:

### Data Engineering
- API data ingestion
- ETL pipeline design
- SQLite data storage

### Data Analysis
- statistical signal generation
- backtesting framework
- performance evaluation

### Visualization
- matplotlib charts
- Streamlit interactive dashboard

---

# Future Improvements

Potential extensions:

- multi-factor signals
- machine learning models
- portfolio allocation
- automated data pipeline scheduling
- cloud deployment

## Dashboard Features

- Live Market Panel
- Today Trading Signal
- Strategy Health Monitor
- Equity Curve Visualization
- Z-score Signal Chart
- Backtest Detail Table
- Strategy Ranking
- Portfolio Simulator
- Daily Auto Update
- CLI Launcher
---

# Author

Patric Xie

Data Engineering / Quantitative Analysis Project
