import pandas as pd
import requests
from datetime import datetime, timedelta
import yfinance as yf
import re

# API-KEY1: PXC0JBLO9YVYWF9U
# API-KEY2: PJ5AMO1H8X3JCAEI
# API-KEY3: C2ARQRXUKFAUTVP1

def extract_company_name(company_string):
    """
    Extracts the main company name from a given string by removing common suffixes.

    Parameters:
        company_string (str): The full company name string.

    Returns:
        str: The cleaned company name.
    """
    # Define a regex pattern to match common suffixes
    pattern = r",?\s+(Inc\.|Incorporated|Corp\.|Corporation|Ltd\.|Limited|LLC|LLP|P\.L\.C\.|Co\.|Company|Group|Holdings)$"
    
    # Remove the suffix from the company name
    company_name = re.sub(pattern, "", company_string, flags=re.IGNORECASE)
    
    return company_name.strip()

def get_news_sentiment(API_KEY='C2ARQRXUKFAUTVP1', tickers=None, topics=None, limit=10000, sort_by='LATEST',
start_date=None
):
    """
    Fetch news and sentiment data from Alpha Vantage.

    Parameters:
        tickers (str): Comma-separated tickers (e.g., "AAPL,MSFT").
        topics (str): Topics of interest (e.g., "technology,finance").
        limit (int): Number of news articles to retrieve.
        sort_by (str): Sort order: 'LATEST', 'RELEVANCE', or 'EARLIEST'.

    Returns:
        list: News articles with metadata.
    """
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "NEWS_SENTIMENT",
        "apikey": API_KEY,
        "tickers": tickers,
        "topics": topics,
        "limit": limit,
        "sort_by": sort_by,
        "time_from": start_date,
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()

        if "feed" in data:
            return data["feed"]
        else:
            print("No news data available.")
            return []
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return []

def filter_news(ticker, relevance_score_threshold=0.7, interval="1w"):
    """
    Filter news articles based on relevance score and tickers.

    Parameters:
        news (list): List of news articles with metadata.
        relevance_score_threshold (float): Minimum relevance score for an article.
        tickers (list): List of tickers to filter.

    Returns:
        list: Filtered news articles.
    """

    if interval == "1w":
        start_date = datetime.today() - timedelta(days=7)
        start_date = start_date.strftime('%Y%m%dT%H%M')
    elif interval == "1m":
        start_date = datetime.today() - timedelta(days=31)
        start_date = start_date.strftime('%Y%m%dT%H%M')
    else:
        start_date = None

    news = get_news_sentiment(tickers=ticker, start_date=start_date)
    data = {
        "title": [],
        "published": [],
        "source": [],
        "summary": [],
        "sentiment_label": [],
        "sentiment_score": [],
        "relevance_score": []
    }

    # Fetch stock information
    stock = yf.Ticker(ticker)
    summary = stock.info

    comp_names = {"longName": extract_company_name(summary['longName']), 
                  "shortName": extract_company_name(summary['shortName'])}

    if news:
        
        for article in news:
            
            ticker_sentiment = article['ticker_sentiment']
            for i, sentiment in enumerate(ticker_sentiment):
                #if sentiment['ticker'] == ticker and float(sentiment['relevance_score']) >= relevance_score_threshold:
                    #if comp_names['longName'] in article['summary'] or ticker in article['summary']:
                ticker_idx = i
                data['title'].append(article['title'])
                data['published'].append(article['time_published'])
                data['summary'].append(article['summary'])
                data['source'].append(article['source'])
                data['sentiment_label'].append(ticker_sentiment[ticker_idx]['ticker_sentiment_label'])
                data['sentiment_score'].append(ticker_sentiment[ticker_idx]['ticker_sentiment_score'])
                data['relevance_score'].append(ticker_sentiment[ticker_idx]['relevance_score'])

    # Convert to pandas dataframe and save as csv
    ticker_df = pd.DataFrame(data)
    ticker_df.to_csv(f"data\{str(ticker).lower()}_csv.csv")
    return ticker_df, comp_names["longName"]
    
if __name__ == "__main__":
    blue_chip_stocks = ["AAPL","MSFT","KO","PG","JNJ","DIS","WMT","JPM","MCD","GE"]
    Growth_stocks = ["TSLA","AMZN","NVDA","GOOG","META","NFLX","SHOP","SQ","CRM","UBER"]
    tickers = blue_chip_stocks + Growth_stocks
    for ticker in tickers:
        filter_news(ticker = ticker, interval="1m")

    

   
    

