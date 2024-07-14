import json

def load_api_key() -> dict:
    with open('conf\\cdp_api_key.json') as file: 
        cdp_api_key = json.load(file)
    
    return cdp_api_key
