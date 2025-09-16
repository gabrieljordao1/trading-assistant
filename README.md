# Trading Signals Assistant

This project implements a prototype of an algorithmic trading assistant.  The
goal is to combine several disparate data sources – options flow from
**Unusual Whales**, community sentiment from **Reddit**, and basic
fundamental metrics from **Yahoo! Finance** – into actionable trading
signals.  The code is designed to be easy to extend and replace in the
future with more sophisticated models or APIs once they become available.

## Components

| Module | Purpose |
| --- | --- |
| `config.py` | Centralises configuration values such as API keys, the list of tickers to watch and runtime settings.  Users should edit this file or set environment variables to customise behaviour. |
| `unusual_whales.py` | Contains a stub implementation for accessing options flow from the Unusual Whales API.  The functions gracefully fall back to dummy data when no API key is provided. |
| `reddit.py` | Implements a simple scraper for Reddit threads using the public JSON endpoints.  It extracts posts mentioning symbols and computes a naive sentiment score based on the presence of bullish and bearish keywords. |
| `fundamentals.py` | Fetches basic fundamental metrics from Yahoo! Finance via its quote endpoint.  This avoids external libraries and uses only the built‑in `requests` module. |
| `strategy.py` | Defines a simple rule‑based strategy that merges flow, sentiment and fundamental data.  The default strategy looks for high options activity, positive sentiment and reasonable valuation. |
| `autopilot.py` | Provides a stub for executing trades through a brokerage API.  For safety and compliance this module only logs planned trades and does not actually place any orders. |
| `main.py` | Orchestrates the workflow: loading configuration, polling data sources, generating signals and optionally executing trades.  It prints a summary of actions taken. |

## Usage

1. **Edit `config.py`**

   Populate your Unusual Whales API key, choose a brokerage integration and
   customise your watchlist.  You can also override these values by
   setting environment variables at runtime (see the docstring in
   `config.py`).

2. **Run the assistant**

   Activate your Python environment and execute:

   ```bash
   python -m trading_project.main
   ```

   The script will iterate through each ticker in your watchlist,
   download data, compute a signal and report the result.  In its
   current form it simply prints recommendations and does not place
   trades.

3. **Extending the project**

   The modular design makes it straightforward to add new data sources,
   improve the sentiment analysis or implement real trade execution.  For
   example, you could integrate a natural language processing library or
   replace the Unusual Whales stub with their official SDK once an API
   key is available.
