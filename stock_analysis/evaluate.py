import yfinance as yf
import numpy as np
from llama_model import run_llama
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import re

def evaluate(response,ticker):
 
    weights=dict()
    recommendations = yf.Ticker(ticker).get_recommendations()
    
    rec_first = recommendations.iloc[0, 1:]
    
    for key in rec_first.keys():
        weights[key] = rec_first[key]/rec_first.sum()
    
    weights=list(weights.values())
    #print('weights:',weights)
    mean_value=np.average(a=np.linspace(1,len(weights),len(weights)),weights=weights)
    print('mean_value:',mean_value)
    floor_value = np.floor(mean_value)
    ceil_value = np.ceil(mean_value)
    majority_value = np.argmax(weights)+1
    print('majority_value:',majority_value)
    
    #response = run_llama(model, tokenizer, ticker)
    #print(response)

    # Find all start indices of the substring
    possible_sentiments=['Strong Buy', 'Buy', 'Hold', 'Sell' ,'Strong Sell']
    sentiment_location=[]
    for substring in possible_sentiments:
        matches = [match.start() for match in re.finditer(re.escape(substring), response, re.IGNORECASE)]
        if len(matches) == 0:
            sentiment_location.append(1000000000)
        else:
            sentiment_location.append(min(matches))
                 
    model_value = np.argmin(sentiment_location)+1
    #print('model_value:',model_value)
    print('model_sentiment:',possible_sentiments[model_value-1])
    
    if model_value == majority_value:
        correct = True

    elif model_value in [floor_value, ceil_value]:
        correct = True
    
    else:
        correct = False

    return correct

if __name__ == "__main__":
    evaluate("The decision is: 'hold'.", "AAPL")