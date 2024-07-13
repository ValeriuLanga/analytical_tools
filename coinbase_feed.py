import http.client
import json
from coinbase import jwt_generator
from coinbase.websocket import WSClient

def on_message(msg):
    print(msg)


with open('conf\\cdp_api_key.json') as file: 
    cdp_api_key = json.load(file)

request_method = "GET"
request_path = "/api/v3/brokerage/product_book"

# jwt_uri = jwt_generator.format_jwt_uri(request_method, request_path)
# jwt_token = jwt_generator.build_rest_jwt(jwt_uri, cdp_api_key['name'], cdp_api_key['privateKey'])
# print(jwt_token)

ws_client = WSClient(api_key=cdp_api_key['name'], api_secret=cdp_api_key['privateKey'], on_message=on_message, verbose=True)
ws_client.open()

ws_client.subscribe(["BTC-USD"], ["ticker"])
ws_client.sleep_with_exception_check(sleep=10)
# ws_client.run_forever_with_exception_check()
ws_client.close()