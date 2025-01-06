import yfinance as yf
import numpy as np
from datetime import datetime, timedelta

def generate_stock_summary(ticker):
    """
    Generates a natural language summary of a stock's performance over the last year.

    Parameters:
        ticker (str): Stock ticker symbol.

    Returns:
        str: Natural language summary of the stock's performance.
    """
    # Fetch historical data
    end_date = datetime.today()
    start_date = end_date - timedelta(days=365)
    stock = yf.Ticker(ticker)
    data = stock.history(start=start_date, end=end_date)
    
    if data.empty:
        return f"No data available for {ticker}."

    # Calculate metrics
    start_price = data['Close'].iloc[0]
    end_price = data['Close'].iloc[-1]
    annual_return = ((end_price - start_price) / start_price) * 100
    volatility = data['Close'].pct_change().std() * np.sqrt(len(data))
    max_price = data['Close'].max()
    min_price = data['Close'].min()
    max_drawdown = ((min_price - max_price) / max_price) * 100
    
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

    # Generate a qualitative summary
    if annual_return > 20:
        performance = "a strong growth"
    elif 5 <= annual_return <= 20:
        performance = "moderate growth"
    elif -5 <= annual_return < 5:
        performance = "a stable performance"
    elif -20 <= annual_return < -5:
        performance = "a moderate decline"
    else:
        performance = "a significant decline"

    if volatility > 0.4:
        volatility_description = "highly volatile"
    elif 0.2 <= volatility <= 0.4:
        volatility_description = "moderately volatile"
    else:
        volatility_description = "relatively stable"

    # Construct the summary
    summary = (
        f"Over the past year, {ticker} experienced {performance}, "
        f"with an annual return of approximately {annual_return:.2f}%. "
        f"The stock has been {volatility_description}, "
        f"with a maximum price of ${max_price:.2f} and a minimum price of ${min_price:.2f}. "
        f"The largest drop during the year was {abs(max_drawdown):.2f}%, indicating the stock's maximum drawdown."
    )
    
    # Add trend if available
    if trend != "no trend":
        summary += f" The stock is currently {trend}."
    
    return summary