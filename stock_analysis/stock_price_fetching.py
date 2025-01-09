import yfinance as yf
import pandas as pd
from datetime import datetime
from sklearn.linear_model import LinearRegression
import numpy as np
import time

def news_price_combiner(ticker,data):

    
    for i in range(len(data) - 1):
        #time.sleep(1)
        current_date = data.iloc[i]['published']
        next_date = data.iloc[i+1]['published']
        # Parse the string into a datetime object
        current_date_obj = datetime.strptime(current_date, "%Y%m%dT%H%M%S")
        next_date_obj = datetime.strptime(next_date, "%Y%m%dT%H%M%S")
        
        date_diff = current_date_obj - next_date_obj
        
        interval=None
        if date_diff.days > 0:
            interval = "1d"
        elif date_diff.seconds//3600 > 0:
            interval = "1h"
        elif date_diff.seconds//60 > 0:
            interval = "1m"

        start_date = current_date_obj.date()
        end_date = next_date_obj.date()

        # Fetch stock news data
        price_data = yf.Ticker(ticker).history(interval=interval, 
                                               start = start_date, 
                                               end = end_date)
        
        # Check if data is empty
        if price_data.empty:

            print(f"No price data found for {ticker} between {start_date} and {end_date}. The market may have been closed.")
            
        else:
            
            X = np.linspace(0, len(price_data), len(price_data)).reshape(-1,1)
            #X = price_data[['DateNumeric']].values  # Independent variable
            Y = price_data[['Close']].values  # Dependent variable (e.g., closing price)
            Y[-1]=price_data[['Open']].values[-1]
            
            data.loc[i, 'Price Change'] = (Y[-1]-Y[0])/Y[0]
            print("Change:",(Y[-1]-Y[0])/Y[0])

            
    
    # period: Specify the time range (e.g., "1d", "5d", "1mo", "1y", "5y", "max")
    # interval: Specify the frequency of data. Options: "1m", "2m", "5m", "15m", "30m", "60m", "1h", "1d", "5d", "1wk", "1mo", "3mo".
    # start and end: Specify custom date ranges (YYYY-MM-DD format).
    #data = yf.Ticker(ticker).history(start="2023-01-01", end="2023-12-31", interval="1wk") 
    # Fetch stock price data
    data.to_csv("aapl_csv_final.csv", index=False)
    
    
    # Combine the two datasets
    #combined_data = data.merge(price_data, left_index=True, right_index=True)
    return combined_data

if __name__ == "__main__":

    ticker = "AAPL"
    ticker_df = pd.read_csv("aapl_csv_cleaned.csv")
    sorted_df = ticker_df.sort_values(by="published")
    sorted_df = sorted_df.reset_index(drop=True)

    combined_data = news_price_combiner(ticker, sorted_df)

    # period: Specify the time range (e.g., "1d", "5d", "1mo", "1y", "5y", "max")
    # interval: Specify the frequency of data. Options: "1m", "2m", "5m", "15m", "30m", "60m", "1h", "1d", "5d", "1wk", "1mo", "3mo".
    # start and end: Specify custom date ranges (YYYY-MM-DD format).
    #data = yf.Ticker(ticker).history(start="2023-01-01", end="2023-12-31", interval="1wk")