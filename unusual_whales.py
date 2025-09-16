"""Unusual Whales API client (stub).

This module exposes functions to interact with the Unusual Whales API.
Because access to the official API requires an API key and paid
subscription, the functions in this file gracefully degrade to empty
results when a key is not provided.  They are structured to make
future extension simple once credentials are available.

The API endpoints used here are based on publicly available
documentation and may need adjustment if the service changes.  If a
request fails or returns invalid data, the functions will silently
return empty lists to avoid interrupting downstream processing.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional

import requests

from . import config


logger = logging.getLogger(__name__)

# Base URL for the Unusual Whales REST API.  This may change in future
# versions of the service; update as necessary.
BASE_URL = "https://api.unusualwhales.com"


def _get_headers() -> Dict[str, str]:
    """Return HTTP headers for API requests.

    If an API key is configured, it is included as an Authorization
    header using the bearer token format.  Without a key the header
    dictionary is empty.
    """
    if config.UNUSUAL_WHALES_API_KEY:
        return {"Authorization": f"Bearer {config.UNUSUAL_WHALES_API_KEY}"}
    return {}


def get_recent_flow(symbol: str, limit: int = 20) -> List[Dict[str, Any]]:
    """Retrieve recent options flow for a given stock symbol.

    Parameters
    ----------
    symbol : str
        Ticker symbol (e.g. ``"AAPL"``) for which to fetch flow data.
    limit : int, default 20
        Maximum number of flow entries to return.

    Returns
    -------
    list of dict
        Each dictionary contains details about a single options flow
        trade.  When no API key is configured or an error occurs an
        empty list is returned.
    """
    # Avoid making requests if no API key is present.
    if not config.UNUSUAL_WHALES_API_KEY:
        logger.debug("Unusual Whales API key not provided; returning empty flow data for %s", symbol)
        return []
    endpoint = f"{BASE_URL}/stock/flow/recent"
    params = {"symbol": symbol, "limit": limit}
    try:
        response = requests.get(endpoint, headers=_get_headers(), params=params, timeout=10)
        response.raise_for_status()
        data: Dict[str, Any] = response.json()
        # The API returns either {"data": [...] } or a raw list.  Normalize to a list.
        flows = data.get("data") if isinstance(data, dict) else data
        if not isinstance(flows, list):
            logger.warning("Unexpected flow response format for %s: %s", symbol, data)
            return []
        return flows  # type: ignore[return-value]
    except Exception as exc:
        logger.error("Failed to fetch flow data for %s: %s", symbol, exc)
        return []


def get_market_tide() -> Optional[Dict[str, Any]]:
    """Retrieve a market sentiment indicator from Unusual Whales.

    The market tide indicator provides a high‑level view of bullish vs
    bearish sentiment across the options market.  This can be used as
    an additional filter in the trading strategy.  When no API key is
    configured the function returns ``None``.

    Returns
    -------
    dict or None
        A dictionary of market tide values or ``None`` if unavailable.
    """
    if not config.UNUSUAL_WHALES_API_KEY:
        return None
    endpoint = f"{BASE_URL}/market/tide"
    try:
        response = requests.get(endpoint, headers=_get_headers(), timeout=10)
        response.raise_for_status()
        data: Dict[str, Any] = response.json()
        return data  # May contain fields like {'tide': 0.65, 'updated': '2025-09-16T16:00:00Z'}
    except Exception as exc:
        logger.error("Failed to fetch market tide data: %s", exc)
        return None


__all__ = ["get_recent_flow", "get_market_tide"]