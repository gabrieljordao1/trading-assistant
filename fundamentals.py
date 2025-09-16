"""Fundamental data retrieval using Yahoo! Finance."""

from __future__ import annotations

import logging
from typing import Dict, Optional

import requests


logger = logging.getLogger(__name__)

# Yahoo Finance quote endpoint.  The public API does not require an
# authentication token but may be subject to rate limits.  You should
# avoid making excessive requests in quick succession.
YAHOO_QUOTE_URL = "https://query1.finance.yahoo.com/v7/finance/quote"


def get_fundamentals(symbol: str) -> Optional[Dict[str, float]]:
    """Return basic fundamental metrics for a stock symbol.

    The function fetches data from Yahoo! Finance's quote endpoint and
    extracts a handful of useful metrics.  If the request fails or the
    symbol is not found, ``None`` is returned.

    Parameters
    ----------
    symbol : str
        The ticker symbol to query.

    Returns
    -------
    dict or None
        A dictionary of metrics.  See the code for exact keys.  ``None``
        indicates that no data could be retrieved.
    """
    params = {"symbols": symbol.upper()}
    try:
        response = requests.get(YAHOO_QUOTE_URL, params=params, timeout=10)
        response.raise_for_status()
        quote_data = response.json()
        results = quote_data.get("quoteResponse", {}).get("result", [])
        if not results:
            return None
        info = results[0]
        # Select a subset of available metrics.  Additional fields can be
        # added here as needed.  Missing values default to None.
        fundamentals: Dict[str, float] = {}
        def _maybe_float(key: str) -> Optional[float]:
            value = info.get(key)
            return float(value) if isinstance(value, (int, float)) else None
        fundamentals["regularMarketPrice"] = _maybe_float("regularMarketPrice")
        fundamentals["marketCap"] = _maybe_float("marketCap")
        fundamentals["trailingPE"] = _maybe_float("trailingPE")
        fundamentals["forwardPE"] = _maybe_float("forwardPE")
        fundamentals["epsTrailingTwelveMonths"] = _maybe_float("epsTrailingTwelveMonths")
        fundamentals["epsForward"] = _maybe_float("epsForward")
        fundamentals["profitMargins"] = _maybe_float("profitMargins")
        fundamentals["pegRatio"] = _maybe_float("pegRatio")
        fundamentals["bookValue"] = _maybe_float("bookValue")
        return fundamentals
    except Exception as exc:
        logger.error("Failed to fetch fundamentals for %s: %s", symbol, exc)
        return None


__all__ = ["get_fundamentals"]