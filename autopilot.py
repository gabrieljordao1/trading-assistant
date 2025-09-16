"""Autopilot trade execution (stub).

This module contains placeholder code for executing trades.  In
production you would replace the stub functions with calls to your
brokerage's REST API or SDK.  For safety, the default implementation
only logs the intended actions and does not place any real orders.

To enable automated trading you must supply your broker credentials via
environment variables (see ``config.py``) and implement the
``submit_order`` function below.
"""

from __future__ import annotations

import logging
from typing import Optional

from . import config


logger = logging.getLogger(__name__)


def submit_order(symbol: str, side: str, quantity: int, dry_run: bool = False) -> None:
    """Send an order to the broker or log it if dry‑run.

    Parameters
    ----------
    symbol : str
        The ticker to trade.
    side : str
        Either ``"buy"`` or ``"sell"``.  Other values are ignored.
    quantity : int
        Number of shares to trade.  Must be a positive integer.
    dry_run : bool, default False
        When True the function logs the order but does not attempt to
        contact the broker.  This is useful for testing.
    """
    side = side.lower()
    if side not in {"buy", "sell"}:
        logger.error("Invalid order side: %s", side)
        return
    if quantity <= 0:
        logger.error("Quantity must be positive: %s", quantity)
        return
    if dry_run or not config.is_autopilot_enabled():
        logger.info("DRY RUN: Would %s %d shares of %s", side, quantity, symbol)
        return
    # Placeholder for broker integration.  Replace this with actual
    # calls to your broker's API.  For example, using the Alpaca SDK:
    #   import alpaca_trade_api as tradeapi
    #   api = tradeapi.REST(config.BROKER_API_KEY, config.BROKER_API_SECRET, paper=config.BROKER_PAPER)
    #   api.submit_order(symbol=symbol, qty=quantity, side=side, type='market', time_in_force='day')
    try:
        logger.warning(
            "Autopilot execution is not implemented.  No order was placed for %s %s %d.",
            side,
            symbol,
            quantity,
        )
    except Exception as exc:
        logger.error("Failed to submit order for %s: %s", symbol, exc)


__all__ = ["submit_order"]