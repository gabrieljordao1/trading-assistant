"""Command‑line entry point for the trading signals assistant."""

from __future__ import annotations

import argparse
import logging
import sys
from typing import List

from . import (
    autopilot,
    config,
    fundamentals,
    reddit,
    strategy,
    unusual_whales,
)


def setup_logging(verbose: bool = False) -> None:
    """Configure basic logging to stdout."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="[%(asctime)s] %(levelname)s:%(name)s:%(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
    )


def process_symbol(symbol: str, dry_run: bool = False) -> None:
    """Fetch data, generate a signal and optionally execute a trade."""
    logging.info("\nProcessing %s", symbol)
    flows = unusual_whales.get_recent_flow(symbol)
    sentiment_score = reddit.get_sentiment_for_symbol(symbol)
    fundamentals_data = fundamentals.get_fundamentals(symbol)
    signal_data = strategy.generate_signal(symbol, flows, sentiment_score, fundamentals_data)
    logging.info("Signal for %s: %s", symbol, signal_data["signal"])
    logging.info("Reason: %s", signal_data["reason"])
    # Decide whether to place an order
    if signal_data["signal"] in {"buy", "sell"}:
        # Determine a default quantity.  For demonstration we trade 1 share.
        quantity = 1
        autopilot.submit_order(symbol, signal_data["signal"], quantity, dry_run=dry_run)
    else:
        logging.info("No trade executed for %s.", symbol)


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the trading signals assistant.")
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose logging."
    )
    parser.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help="Do not execute trades; log actions instead.",
    )
    parser.add_argument(
        "--symbols",
        type=str,
        default=None,
        help="Comma separated list of ticker symbols to process (overrides WATCHLIST).",
    )
    args = parser.parse_args(argv)
    setup_logging(args.verbose)
    # Determine which symbols to process
    if args.symbols:
        symbols = [s.strip().upper() for s in args.symbols.split(",") if s.strip()]
    else:
        symbols = config.WATCHLIST
    logging.info("Starting trading assistant for symbols: %s", ", ".join(symbols))
    for symbol in symbols:
        process_symbol(symbol, dry_run=args.dry_run)
    logging.info("All symbols processed.  Exiting.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
