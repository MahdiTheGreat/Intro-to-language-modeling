from fetch_news import filter_news, get_raw_news
from fetch_company_summary import stock_info_to_text
import pandas as pd

def get_system_prompt(ticker):

    comp_name = get_raw_news(ticker, interval="1y")
    news_df = filter_news(ticker, relevance_score_threshold=0.7)
    company_summary = stock_info_to_text(ticker)
    # Start with the company summary
    prompt = (
        "You are a financial analyst. Your task is to analyze the given company summary and the latest news articles to decide whether the company's stock should be classified as 'Strong Buy', 'Buy', 'Hold', 'Sell' or 'Strong Sell'. "
        "Provide a clear decision and a detailed explanation based on the information provided.\n\n"
        f"The company name is {comp_name} and the ticker is {ticker}\n\n"
        f"Company Summary: {company_summary}\n\n"
        "Latest News Articles:\n"
    )   
    
    # Add summaries from each row of the DataFrame
    for index, row in news_df.iterrows():
        prompt += f"Title: {row['title']}\n"
        prompt += f"Summary: {row['summary']}\n"
        prompt += f"Article Sentiment: {row['sentiment_label']}\n\n"
    prompt += "Your response should include:\n1. A decision: 'Strong Buy', 'Buy', 'Hold', 'Sell' or 'Strong Sell'.\n2. A detailed explanation justifying your decision, citing specific points from the company summary and the articles."
    
    return prompt

if __name__ == "__main__":
    system_prompt = get_system_prompt("TSLA")
    print(system_prompt)