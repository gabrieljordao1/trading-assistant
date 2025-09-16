"""Configuration for the trading signals assistant.

This module centralises all runtime configuration.  Each configurable
option has a sensible default and can be overridden via environment
variables.  Users are encouraged to edit this file when experimenting
locally or set environment variables when running in production.

Attributes
----------
UNUSUAL_WHALES_API_KEY : str or None
    API key for Unusual Whales.  Set via the ``UW_API_KEY`` environment
    variable or directly in this file.  When ``None`` the
    application will not attempt to query Unusual Whales and will
    instead return stub data.

BROKER_API_KEY : str or None
BROKER_API_SECRET : str or None
    Credentials for your brokerage API.  If these values are not
    supplied the autopilot module will operate in dry‑run mode and
    avoid placing any orders.  The application currently includes
    placeholders rather than a concrete broker implementation.

BROKER_PAPER : bool
    When ``True`` the autopilot will connect to paper trading or
    sandbox endpoints where available.  If no paper endpoint exists
    the autopilot will warn and skip order submission.

WATCHLIST : list[str]
    A list of ticker symbols to monitor.  These symbols should be
    recognised by the underlying data providers.  Defaults to a few
    widely traded equities.

SENTIMENT_THRESHOLD : float
    The minimum sentiment score required to consider Reddit sentiment
    bullish.  Values greater than this threshold indicate overall
    bullish discussion, while values less than the negative of this
    threshold indicate bearishness.

"""

import os
from typing import List


def _get_env(key: str, default: str | None = None) -> str | None:
    """Return the value of the environment variable ``key``.

    The helper normalises empty strings to ``None`` and falls back to
    the supplied default.  This makes it convenient to specify an empty
    environment variable to disable a particular feature.

    Parameters
    ----------
    key : str
        Name of the environment variable to read.
    default : str or None, optional
        Value to return if the environment variable is unset or empty.

    Returns
    -------
    str or None
        The value of the environment variable or ``default``.
    """
    value = os.getenv(key)
    if value is None or value == "":
        return default
    return value


UNUSUAL_WHALES_API_KEY: str | None = _get_env("UW_API_KEY")

# Placeholder broker credentials.  Replace these with your actual
# brokerage keys or set the corresponding environment variables.
BROKER_API_KEY: str | None = _get_env("BROKER_API_KEY")
BROKER_API_SECRET: str | None = _get_env("BROKER_API_SECRET")
BROKER_PAPER: bool = os.getenv("BROKER_PAPER", "1") not in {"", "0", "false", "False"}

# List of tickers to watch.  Use environment variable WATCHLIST to
# override as comma‑separated symbols.  Example:
# ``WATCHLIST="AAPL,MSFT,TSLA" python -m trading_project.main``
_watchlist_env = _get_env("WATCHLIST")
if _watchlist_env:
    WATCHLIST: List[str] = [symbol.strip().upper() for symbol in _watchlist_env.split(",") if symbol.strip()]
else:
    WATCHLIST: List[str] = ["AAPL", "MSFT", "TSLA"]

# Sentiment threshold.  The strategy will treat scores above this value
# as bullish and below the negative value as bearish.
SENTIMENT_THRESHOLD: float = float(os.getenv("SENTIMENT_THRESHOLD", "0.2"))


def is_autopilot_enabled() -> bool:
    """Return ``True`` if automatic trade execution is configured."""
    return BROKER_API_KEY is not None and BROKER_API_SECRET is not None


__all__ = [
    "UNUSUAL_WHALES_API_KEY",
    "BROKER_API_KEY",
    "BROKER_API_SECRET",
    "BROKER_PAPER",
    "WATCHLIST",
    "SENTIMENT_THRESHOLD",
    "is_autopilot_enabled",
]