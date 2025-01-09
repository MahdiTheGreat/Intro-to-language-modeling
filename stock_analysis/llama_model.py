from generate_system_prompt import get_system_prompt
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

def run_llama(model, tokenizer, ticker):

    # Create the prompt
    system_prompt = get_system_prompt(ticker=ticker)

    # Tokenize input
    inputs = tokenizer(system_prompt, return_tensors="pt").to("cuda")

    # Generate response
    output = model.generate(
        **inputs,
        max_length=2048,
        temperature=0.7,
        top_p=0.9,
        do_sample=True
    )

    # Decode and print the response
    response = tokenizer.decode(output[0], skip_special_tokens=True)

    response = response[len(system_prompt):]

    return response

if __name__ == "__main__":
    pass
    #response = main()
    #print(response)