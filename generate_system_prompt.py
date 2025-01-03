from fetch_news import filter_news
from fetch_company_summary import generate_stock_summary
import pandas as pd
from datetime import datetime, timedelta

def news_prompt(ticker):

    news = pd.read_csv(f"{ticker.lower()}_csv.csv")
    last_week_date = datetime.today() - timedelta(days=7)
    

news_prompt("TSLA")