import requests
import os

# -----------------------------
# UNIVERSE BUILDER
# -----------------------------
def get_universe(key):

    url = f"https://finnhub.io/api/v1/stock/symbol?exchange=US&token={key}"
    r = requests.get(url, timeout=20)

    if r.status_code != 200:
        return []

    data = r.json()

    symbols = []

    for item in data:

        symbol = item.get("symbol")

        if not symbol:
            continue

        if len(symbol) > 6:
            continue

        if "." in symbol:
            continue

        symbols.append(symbol)

    return symbols[:20]


# -----------------------------
# SIGNAL CLASSIFICATION
# -----------------------------
def classify_stock(change_pct, range_pct, price, prev_close):

    trend = "UP" if price > prev_close else "DOWN"
    abs_change = abs(change_pct)

    if abs_change > 2 and range_pct > 2 and trend == "UP":
        return "🚀 STRONG BREAKOUT"

    if abs_change > 1.5 and trend == "UP":
        return "🔥 MOMENTUM UP"

    if abs_change > 1.5 and trend == "DOWN":
        return "⚠️ STRONG SELL PRESSURE"

    if abs_change < 0.5:
        return "💤 NOISE"

    return "📊 NORMAL"


# -----------------------------
# MOMENTUM SCORE
# -----------------------------
def momentum_score(change_pct, range_pct):

    score = abs(change_pct) * 2 + range_pct * 1.5

    if abs(change_pct) > 2:
        score += 2

    if abs(change_pct) < 0.5:
        score -= 2

    return round(score, 2)


# -----------------------------
# EXPLANATION ENGINE
# -----------------------------
def explain_signal(symbol, change_pct, range_pct, price, prev_close):

    trend = "bullish" if price > prev_close else "bearish"
    abs_change = abs(change_pct)

    parts = []

    if abs_change > 2:
        parts.append("strong price momentum with elevated volatility")
    elif abs_change > 1:
        parts.append("moderate directional momentum")
    else:
        parts.append("low directional pressure")

    if range_pct > 3:
        parts.append("high intraday volatility indicating active trading")
    elif range_pct > 1.5:
        parts.append("moderate volatility with stable flow")
    else:
        parts.append("low volatility environment")

    parts.append(f"overall {trend} bias vs previous close")

    return f"{symbol} shows " + ", ".join(parts) + "."


# -----------------------------
# MAIN SCREENER
# -----------------------------
def run_screener():

    key = os.environ.get("FINNHUB_API_KEY")

    symbols = get_universe(key)

    results = []

    for s in symbols:

        try:
            url = f"https://finnhub.io/api/v1/quote?symbol={s}&token={key}"
            r = requests.get(url, timeout=10)

            if r.status_code != 200:
                continue

            data = r.json()

            price = data.get("c")
            prev = data.get("pc")
            high = data.get("h")
            low = data.get("l")

            # -------------------------
            # SAFE VALIDATION (FIXED ORDER)
            # -------------------------
            if not price or not prev:
                continue

            # MID-CAP FILTER (FIXED LOCATION)
            if price < 15 or price > 300:
                continue

            change_pct = ((price - prev) / prev) * 100
            range_pct = ((high - low) / price) * 100 if high and low else 0

            signal = classify_stock(change_pct, range_pct, price, prev)
            score = momentum_score(change_pct, range_pct)
            explanation = explain_signal(s, change_pct, range_pct, price, prev)

            if signal == "💤 NOISE":
                continue

            results.append({
                "symbol": s,
                "price": round(price, 2),
                "change_pct": round(change_pct, 2),
                "range_pct": round(range_pct, 2),
                "score": score,
                "signal": signal,
                "explanation": explanation
            })

        except Exception:
            continue

    results.sort(key=lambda x: x["score"], reverse=True)

    # -----------------------------
    # TEXT OUTPUT
    # -----------------------------
    text_blocks = []

    for r in results[:10]:

        text_blocks.append(
            f"{r['symbol']} | ${r['price']} | {r['change_pct']}% | "
            f"{r['signal']} | Score: {r['score']}\n"
            f"→ {r['explanation']}"
        )

    pretty_text = "\n\n".join(text_blocks).strip()

    # -----------------------------
    # HTML OUTPUT
    # -----------------------------
    html_blocks = []

    for r in results[:10]:

        html_blocks.append(f"""
        <p>
            <b>{r['symbol']}</b> | ${r['price']} | {r['change_pct']}% | {r['signal']} | Score: {r['score']}<br>
            → {r['explanation']}
        </p>
        <hr>
        """)

    pretty_html = "".join(html_blocks)

    return {
        "count": len(results),
        "results": results[:10],
        "pretty_text": pretty_text,
        "pretty_html": pretty_html
    }
