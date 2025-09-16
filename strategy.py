"""Simple rule‑based trading strategy.

This module implements a rudimentary strategy that combines options flow
data, Reddit sentiment and fundamental valuations to produce a
recommendation for each ticker symbol.  The strategy is intentionally
transparent: it returns not only a buy/hold/sell signal but also an
explanation of the factors that influenced the decision.

The aim of this module is to demonstrate how multiple data sources can
be fused together.  More advanced users can replace or augment
``generate_signal`` with machine learning models, probabilistic
approaches or custom heuristics.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from . import config


def _analyze_flows(flows: List[Dict[str, any]]) -> Optional[float]:
    """Compute a relative strength metric from options flow.

    The flow data returned by the Unusual Whales API may contain
    information about whether a trade is a call or a put.  This helper
    counts the occurrences of calls and puts to derive a simple ratio.
    A value greater than 0.5 indicates net bullish activity, while a
    value less than 0.5 indicates net bearish activity.  If flow data
    is empty or contains no type information, ``None`` is returned.
    """
    call_count = 0
    put_count = 0
    for item in flows:
        # Some flows include a 'type' field with values like 'call' or
        # 'put'.  Normalise to lower case.  If absent we ignore the
        # entry for the purposes of this metric.
        t = item.get("type")
        if isinstance(t, str):
            t_lower = t.lower()
            if "call" in t_lower:
                call_count += 1
            elif "put" in t_lower:
                put_count += 1
    total = call_count + put_count
    if total == 0:
        return None
    return call_count / total


def generate_signal(symbol: str, flows: List[Dict[str, any]], sentiment: float, fundamentals: Optional[Dict[str, float]]) -> Dict[str, any]:
    """Combine multiple inputs to produce a trading signal.

    Parameters
    ----------
    symbol : str
        Ticker symbol.
    flows : list of dict
        Recent options flow data for the symbol.  See
        ``unusual_whales.get_recent_flow`` for details.
    sentiment : float
        Aggregate Reddit sentiment score between –1 and +1.
    fundamentals : dict or None
        Basic fundamental metrics for the symbol.  See
        ``fundamentals.get_fundamentals`` for details.

    Returns
    -------
    dict
        Contains the symbol, a signal ("buy", "sell" or "hold") and a
        human‑readable reason summarising the inputs.
    """
    reason_parts: List[str] = []
    flow_strength = _analyze_flows(flows)
    if flow_strength is not None:
        reason_parts.append(f"Flow strength {flow_strength:.2f}")
    else:
        reason_parts.append("No flow data")
    # Interpret sentiment
    if sentiment > config.SENTIMENT_THRESHOLD:
        sent_desc = f"Bullish sentiment ({sentiment:+.2f})"
    elif sentiment < -config.SENTIMENT_THRESHOLD:
        sent_desc = f"Bearish sentiment ({sentiment:+.2f})"
    else:
        sent_desc = f"Neutral sentiment ({sentiment:+.2f})"
    reason_parts.append(sent_desc)
    # Evaluate fundamentals
    pe = None
    if fundamentals:
        pe = fundamentals.get("trailingPE") or fundamentals.get("forwardPE")
        if pe is not None:
            reason_parts.append(f"PE {pe:.1f}")
    # Decision logic
    signal: str = "hold"
    # Buy conditions: bullish flow, bullish sentiment, reasonable valuation
    if (
        flow_strength is not None
        and flow_strength > 0.6
        and sentiment > config.SENTIMENT_THRESHOLD
        and (pe is None or pe < 30)
    ):
        signal = "buy"
        reason_parts.append("High call activity + bullish sentiment + attractive PE")
    # Sell conditions: bearish flow, bearish sentiment, expensive valuation
    elif (
        flow_strength is not None
        and flow_strength < 0.4
        or sentiment < -config.SENTIMENT_THRESHOLD
        or (pe is not None and pe > 50)
    ):
        signal = "sell"
        reason_parts.append("Bearish conditions outweigh positives")
    else:
        signal = "hold"
        reason_parts.append("Mixed signals; stay neutral")
    return {"symbol": symbol, "signal": signal, "reason": "; ".join(reason_parts)}


__all__ = ["generate_signal"]