import tiktoken

tokenizer = tiktoken.get_encoding('o200k_base')

def token_size(text):
    return len(tokenizer.encode(text))
