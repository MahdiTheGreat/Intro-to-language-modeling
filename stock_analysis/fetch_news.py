import pandas as pd
import requests
from datetime import datetime, timedelta
import yfinance as yf
import re
import os

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

def get_news_sentiment(API_KEY='C2ARQRXUKFAUTVP1', tickers=None, topics=None, limit=None, sort_by='LATEST',
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

def get_raw_news(ticker, interval="1y"):
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
    elif interval == "1y":
        start_date = datetime.today() - timedelta(days=365)
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
    # Check if the folder exists
    folder_name = "raw_data"
    if not os.path.exists(folder_name):
        # Create the folder
        os.makedirs(folder_name)
    ticker_df.to_csv(f"{folder_name}\{str(ticker).lower()}_raw.csv")
    return comp_names["longName"]

def filter_news(ticker, relevance_score_threshold=0.7):

    """
    Filter a DataFrame from a CSV file if it exists in the 'raw_data' folder.
    
    Parameters:
        ticker (str): Ticker symbol of the stock.
        filter_conditions (dict): Conditions to filter the DataFrame (e.g., column: value pairs).
    
    Returns:
        pd.DataFrame: Filtered DataFrame.
    
    Raises:
        FileNotFoundError: If the raw data CSV file does not exist.
    """
    file_path = f"raw_data/{str(ticker).lower()}_raw.csv"

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file '{file_path}' does not exist in the 'raw_data' folder.")
    
    # Load the CSV into a DataFrame
    df = pd.read_csv(file_path)
    
    # Apply filtering
    df[df['relevance_score'] > relevance_score_threshold]
    
    return df
    
if __name__ == "__main__":
    blue_chip_stocks = ["AAPL","MSFT","KO","PG","JNJ","DIS","WMT","JPM","MCD","GE"]
    Growth_stocks = ["TSLA","AMZN","NVDA","GOOG","META","NFLX","SHOP","SQ","CRM","UBER"]
    tickers = blue_chip_stocks + Growth_stocks
    #for ticker in tickers:
    #    filter_news(ticker = ticker, interval="1m")
    get_raw_news("TSLA")

    

   
    

