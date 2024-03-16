import os
from dotenv import load_dotenv
import websocket
import json
import requests

# Load environment variables from .env file
load_dotenv()

# Environment Variables
APCA_API_BASE_URL = os.getenv('APCA_API_BASE_URL')
APCA_API_KEY_ID = os.getenv('APCA_API_KEY_ID')
APCA_API_SECRET_KEY = os.getenv('APCA_API_SECRET_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Rest of the code remains the same as provided in the previous Python code snippet...
# Server < -- > Data Source
# Communication can go both ways
# Data source can send us information
# Send data to the data source (Authenticate, ask what data we want)

# WebSockets are like push notifications on your phone
# Whenever an event happens (texts you, snapchat, anything) you get a notification

def on_message(ws, message):
    print("Message is", message)
    current_event = json.loads(message)[0]

    if current_event['T'] == "n":  # This is a news event
        company_impact = 0

        # Ask ChatGPT its thoughts on the headline
        api_request_body = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "Only respond with a number from 1-100 detailing the impact of the headline."},
                {"role": "user", "content": f"Given the headline '{current_event['headline']}', show me a number from 1-100 detailing the impact of this headline."}
            ]
        }

        response = requests.post("https://api.openai.com/v1/chat/completions", headers={"Authorization": "Bearer " + OPENAI_API_KEY, "Content-Type": "application/json"}, json=api_request_body)
        data = response.json()
        print(data)
        company_impact = int(data['choices'][0]['message']['content'])

        # Make trades based on the output (of the impact saved in companyImpact)
        ticker_symbol = current_event['symbols'][0]

        # 1 - 100, 1 being the most negative, 100 being the most positive impact on a company.
        if company_impact >= 70:  # if score >= 70 : BUY STOCK
            # Buy stock
            pass  # Placeholder for actual trading logic in Python
        elif company_impact <= 30:  # else if impact <= 30: SELL ALL OF STOCK
            # Sell stock
            pass  # Placeholder for actual trading logic in Python

def on_error(ws, error):
    print(error)

def on_close(ws):
    print("### closed ###")

def on_open(ws):
    print("Websocket connected!")

    # We now have to log in to the data source
    auth_msg = {
        "action": 'auth',
        "key": APCA_API_KEY_ID,
        "secret": APCA_API_SECRET_KEY
    }
    ws.send(json.dumps(auth_msg))  # Send auth data to ws, "log us in"

    # Subscribe to all news feeds
    subscribe_msg = {
        "action": 'subscribe',
        "news": ['*']  # ["TSLA"]
    }
    ws.send(json.dumps(subscribe_msg))  # Connecting us to the live data source of news

if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("wss://stream.data.alpaca.markets/v1beta1/news",
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()
