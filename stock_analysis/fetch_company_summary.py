import yfinance as yf
import numpy as np
from datetime import datetime, timedelta

def stock_info_to_text(ticker):
    """
    Converts Yahoo Finance stock information into qualitative text with generalized thresholds.

    Parameters:
        ticker (str): Stock ticker symbol.

    Returns:
        str: A qualitative text summary of the stock.
    """
    stock = yf.Ticker(ticker)
    info = stock.info

    if not info:
        return f"No information available for {ticker}."

    # Extract relevant information
    name = info.get("longName", ticker)
    sector = info.get("sector", "N/A")
    industry = info.get("industry", "N/A")
    market_cap = info.get("marketCap", None)
    pe_ratio = info.get("trailingPE", None)
    dividend_yield = info.get("dividendYield", None)
    fifty_two_week_high = info.get("fiftyTwoWeekHigh", None)
    fifty_two_week_low = info.get("fiftyTwoWeekLow", None)
    current_price = info.get("regularMarketPrice", None)

    # Generalized thresholds for market cap
    if market_cap:
        if market_cap > 50e9:
            market_cap_text = "a large-cap company"
        elif market_cap > 2e9:
            market_cap_text = "a mid-cap company"
        else:
            market_cap_text = "a small-cap company"
    else:
        market_cap_text = "an unknown-cap company"

    # Generalized thresholds for PE ratio using percentiles
    pe_description = "N/A"
    if pe_ratio:
        pe_percentiles = np.percentile([10, 15, 25, 40], [25, 50, 75])  # Hypothetical PE ranges
        if pe_ratio < pe_percentiles[0]:
            pe_description = "undervalued"
        elif pe_ratio < pe_percentiles[1]:
            pe_description = "fairly valued"
        elif pe_ratio < pe_percentiles[2]:
            pe_description = "slightly overvalued"
        else:
            pe_description = "highly overvalued"

    pe_ratio_text = (
        f"The stock has a price-to-earnings (PE) ratio of {pe_ratio:.2f}, indicating it is {pe_description}."
        if pe_ratio else
        "The PE ratio is unavailable."
    )

    # Generalized thresholds for dividend yield using percentiles
    if dividend_yield:
        if dividend_yield > 0.03:  # Example threshold for high yield
            dividend_text = f"The stock offers a high dividend yield of {dividend_yield * 100:.2f}%, appealing to income investors."
        else:
            dividend_text = f"The stock offers a dividend yield of {dividend_yield * 100:.2f}%, which is modest."
    else:
        dividend_text = "The stock does not currently pay dividends."

    
    # Fetch historical data
    end_date = datetime.today()
    start_date = end_date - timedelta(days=365)
    stock = yf.Ticker(ticker)
    data = stock.history(start=start_date, end=end_date)
    beta_value = stock.info.get("beta")
    
    # Analyse trend
    macd = (data['Close'].ewm(span=12, adjust=False).mean() - data['Close'].ewm(span=26, adjust=False).mean()).iloc[-1]
    signal = (data['Close'].ewm(span=12, adjust=False).mean() - data['Close'].ewm(span=26, adjust=False).mean()).ewm(span=9, adjust=False).mean().iloc[-1]
    
    if macd > signal and macd > 0 and signal > 0:
        trend = "trending upwards"
    elif macd < signal and macd < 0 and signal < 0:
        trend = "trending downwards"
    elif macd > signal and (macd <= 0 or signal <= 0):
        trend = "trending downwards, but recovering"
    elif macd < signal and (macd >= 0 or signal >= 0):
        trend = "trending upwards, but weakening"
    else:
        trend = "no trend"

    # Interpret beta for volatility
    if beta_value > 1.2:
        volatility_description = "highly volatile compared to the market"
    elif 0.8 <= beta_value <= 1.2:
        volatility_description = "as volatile as the market"
    else:
        volatility_description = "less volatile than the market"

    if data.empty:
        return f"No price data available for {ticker}."

    # Calculate metrics
    start_price = data['Close'].iloc[0]
    end_price = data['Close'].iloc[-1]
    annual_return = ((end_price - start_price) / start_price) * 100
    daily_returns = data['Close'].pct_change()
    max_price = data['Close'].max()
    min_price = data['Close'].min()
    max_drawdown = ((min_price - max_price) / max_price) * 100

    if current_price is None:
        current_price = data['Close'].iloc[-1]

    price_range_mid = (max_price + min_price) / 2
    price_range = max_price - min_price
    if current_price > (price_range_mid + price_range / 4):
        price_range_text = "near its yearly high"
    elif current_price < (price_range_mid - price_range / 4):
        price_range_text = "near its yearly low"
    else:
        price_range_text = "in the mid-range of its yearly performance"
    price_range_text = (
        f"Over the last year, the stock traded between ${fifty_two_week_low:.2f} and ${fifty_two_week_high:.2f}. "
        f"The current price is ${current_price:.2f}, which is {price_range_text}."
    )

    # Statistical thresholds (quartiles)
    return_percentiles = np.percentile(daily_returns.dropna(), [25, 50, 75])

    # Qualitative analysis of annual return
    if annual_return > return_percentiles[2]:
        performance = "strong growth"
    elif return_percentiles[1] <= annual_return <= return_percentiles[2]:
        performance = "moderate growth"
    elif return_percentiles[0] <= annual_return < return_percentiles[1]:
        performance = "stable performance"
    else:
        performance = "a decline"

    # Construct the summary
    summary = (
        f"{name} operates in the {sector} sector and the {industry} industry. It is {market_cap_text}. "
        f"{pe_ratio_text} {dividend_text} {price_range_text}"
        f"Over the past year, {ticker} showed {performance}, "
        f"with an annual return of approximately {annual_return:.2f}%. "
        f"The stock was {volatility_description}, "
        f"with a maximum price of ${max_price:.2f} and a minimum price of ${min_price:.2f}. "
        f"The largest drop during the year was {abs(max_drawdown):.2f}%, indicating the stock's maximum drawdown."
    )

    # Add trend if available
    if trend != "no trend":
        summary += f" The stock is currently {trend}."
        
    return summary

if __name__ == "__main__":
    # Example usage
    ticker = "AAPL"
    print(stock_info_to_text(ticker))
