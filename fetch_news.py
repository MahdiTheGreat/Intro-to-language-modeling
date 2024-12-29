import pandas as pd
import requests
from datetime import datetime

# API-KEY1: PXC0JBLO9YVYWF9U
# API-KEY2: PJ5AMO1H8X3JCAEI
# API-KEY3: C2ARQRXUKFAUTVP1

def get_news_sentiment(API_KEY='C2ARQRXUKFAUTVP1', tickers=None, topics=None, relevance_score_threshold=0.5, limit=1000, sort_by='LATEST',
start_date='20241101T0000', end_date='20241108T0000'
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
        "time_from": start_date,
        "time_to": end_date
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

if __name__ == "__main__":
    
    print("running fetch_news.py")
    # Specify the stock ticker
    ticker = "AAPL"
    #ticker = input("Enter the stock ticker symbol: ").strip().upper()

    news = get_news_sentiment(tickers=ticker)

    data = {
        "title": [],
        "published": [],
        "source": [],
        "summary": [],
        "sentiment_label": [],
        "sentiment_score": [],
        "relevance_score": []
    }

    relevance_score_threshold = 0.5

    if news:
        print("Latest News:")
        
        for article in news:
            
            ticker_sentiment = article['ticker_sentiment']
            for i, sentiment in enumerate(ticker_sentiment):
                if sentiment['ticker'] == ticker and float(sentiment['relevance_score']) >= relevance_score_threshold:
                    ticker_idx = i
                    data['title'].append(article['title'])
                    data['published'].append(article['time_published'])
                    data['summary'].append(article['summary'])
                    data['source'].append(article['source'])
                    print(f"- {article['title']} (Published: {article['time_published']})")
                    print(f"  Source: {article['source']}")
                    print(f"  Summary: {article['summary']}")
                    
                    data['sentiment_label'].append(ticker_sentiment[ticker_idx]['ticker_sentiment_label'])
                    data['sentiment_score'].append(ticker_sentiment[ticker_idx]['ticker_sentiment_score'])
                    data['relevance_score'].append(ticker_sentiment[ticker_idx]['relevance_score'])
                    print(f"  Sentiment: {ticker_sentiment[ticker_idx]['ticker_sentiment_label']} (Score: {ticker_sentiment[ticker_idx]['ticker_sentiment_score']})")
                    print(f"  Relevance Score: {ticker_sentiment[ticker_idx]['relevance_score']}")
                    print(f"  URL: {article['url']}\n")

    ticker_df = pd.DataFrame(data)
    ticker_df.to_csv(f"{str(ticker).lower()}_csv.csv")
    

