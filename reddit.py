"""Reddit sentiment scraper.

This module provides a very lightweight interface for collecting
discussion from Reddit and computing a naive sentiment score for
individual ticker symbols.  It uses Reddit's public JSON endpoints
instead of the official API, which means no authentication is
required.  The sentiment analysis implemented here is intentionally
rudimentary; it counts positive and negative keywords and returns a
score between –1 and +1.
"""

from __future__ import annotations

import logging
import re
from typing import Dict, Iterable, List, Optional

import requests


logger = logging.getLogger(__name__)

# Base URL for Reddit's public API.  The `.json` suffix returns posts
# in JSON format.  We restrict the search to popular trading
# subreddits to minimise noise.
REDDIT_SEARCH_URL = (
    "https://www.reddit.com/r/wallstreetbets+stocks+options+investing/search.json"
)

# A simple lexicon for naive sentiment analysis.  Each keyword has a
# corresponding weight.  These weights were chosen heuristically and
# can be adjusted to better reflect the community's language.
POSITIVE_KEYWORDS: Dict[str, float] = {
    "call": 0.3,
    "calls": 0.3,
    "bull": 0.5,
    "bullish": 0.6,
    "long": 0.2,
    "yolo": 0.4,
    "moon": 0.3,
    "rocket": 0.3,
    "green": 0.2,
    "buy": 0.3,
    "pump": 0.2,
}
NEGATIVE_KEYWORDS: Dict[str, float] = {
    "put": 0.3,
    "puts": 0.3,
    "bear": 0.5,
    "bearish": 0.6,
    "short": 0.4,
    "down": 0.2,
    "dump": 0.3,
    "red": 0.2,
    "sell": 0.3,
    "crash": 0.4,
}


def fetch_recent_posts(symbol: str, limit: int = 50) -> List[str]:
    """Fetch recent Reddit post titles mentioning a symbol.

    Parameters
    ----------
    symbol : str
        The ticker symbol to search for.  The search is case
        insensitive and prefixed with a `$` when not already present.
    limit : int, default 50
        Maximum number of posts to retrieve.  Reddit's API may return
        fewer results depending on availability and rate limits.

    Returns
    -------
    list of str
        A list of post titles.  If an error occurs an empty list is
        returned.
    """
    query = symbol.upper()
    if not query.startswith("$"):
        query = f"${query}"
    params = {
        "q": query,
        "restrict_sr": "on",
        "sort": "new",
        "limit": str(limit),
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; TradingBot/1.0; +https://example.com)"
    }
    try:
        response = requests.get(REDDIT_SEARCH_URL, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        children = data.get("data", {}).get("children", [])
        posts: List[str] = []
        for child in children:
            post_data = child.get("data", {})
            title = post_data.get("title")
            if isinstance(title, str):
                posts.append(title)
        return posts
    except Exception as exc:
        logger.error("Failed to fetch Reddit posts for %s: %s", symbol, exc)
        return []


def compute_sentiment(texts: Iterable[str]) -> float:
    """Compute a naive sentiment score from a collection of texts.

    The algorithm sums the weights of positive keywords and subtracts
    the weights of negative keywords, then normalises by the number of
    texts.  The resulting score lies roughly between –1 and +1, where
    positive values indicate bullish sentiment and negative values
    indicate bearish sentiment.

    Parameters
    ----------
    texts : iterable of str
        Text strings to analyse.  Each entry is typically a post title
        from Reddit.

    Returns
    -------
    float
        Aggregate sentiment score.  Returns 0.0 if no texts are
        provided.
    """
    count = 0
    score = 0.0
    for text in texts:
        count += 1
        lowered = text.lower()
        # Tokenise by splitting on non‑alphanumeric characters.  This is
        # intentionally simple and should be replaced with a proper NLP
        # tokenizer when dependencies permit.
        tokens = re.split(r"[^a-z0-9$]+", lowered)
        # Compute scores for this text
        pos_score = sum(POSITIVE_KEYWORDS.get(tok, 0.0) for tok in tokens)
        neg_score = sum(NEGATIVE_KEYWORDS.get(tok, 0.0) for tok in tokens)
        score += pos_score - neg_score
    if count == 0:
        return 0.0
    # Normalise by the maximum possible absolute score per post to keep
    # values in a manageable range.  Here we use the sum of all weights.
    max_pos = sum(POSITIVE_KEYWORDS.values())
    max_neg = sum(NEGATIVE_KEYWORDS.values())
    max_score = max(max_pos, max_neg)
    return score / (count * max_score) if max_score > 0 else 0.0


def get_sentiment_for_symbol(symbol: str, limit: int = 50) -> float:
    """Fetch posts mentioning ``symbol`` and return the aggregate sentiment.

    Parameters
    ----------
    symbol : str
        The ticker symbol to analyse.
    limit : int, default 50
        Maximum number of posts to consider.

    Returns
    -------
    float
        Sentiment score.  Positive values indicate bullish sentiment
        while negative values indicate bearish sentiment.
    """
    posts = fetch_recent_posts(symbol, limit=limit)
    return compute_sentiment(posts)


__all__ = ["fetch_recent_posts", "compute_sentiment", "get_sentiment_for_symbol"]