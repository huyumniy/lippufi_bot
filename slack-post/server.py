from flask import Flask, request, Response 
from slack_sdk import WebClient
from slackeventsapi import SlackEventAdapter
import json
from datetime import datetime
from slack_sdk.errors import SlackApiError
import sys, os
import requests

app = Flask(__name__)
to_run = True
# Set up Slack API client
slack_token = "xoxb-773919780944-7391942575508-odbMqkbYU0q6mGfoQXxcaxFc"
slack_signing_secret = '93ae3ecbef04bc658767b6feab0ce1f5'
client = WebClient(token=slack_token)
slack_events_adapter = SlackEventAdapter(slack_signing_secret, "/slack/events", app)

# Stops the 
@app.route('/stop', methods=['POST'])
def stop_server():
    print("Received stop request. Stopping server...")
    global to_run
    to_run = False
    return "Sever stopped!"


@app.route('/start', methods=['POST'])
def start_server():
    print("Received start request. Starting server...")
    global to_run
    to_run = True
    return "Server started!"


@app.route('/book', methods=['POST'])
def receive_message():
    # Parse and validate data
    name = request.json['name']
    description = request.json['description']
    date = datetime.strptime(request.json['date'], '%Y-%m-%dT%H:%M:%S.%f%z')
    amount = request.json['amount']
    price = request.json['price']
    currency = request.json['currency']
    category = request.json['category']
    bot_name = request.json['bot_name']
    cookies = request.json['cookies']
    user_agent = request.json['user_agent']
    data = f'*name:* {name}\n*description:* {description}\n*date:* {date}\n*amount:* {amount}\n*price:* {price}{currency}\n*category:* {category}'
    
    if to_run:
        send_to_group_channel(data, cookies, user_agent)
    return ''


def send_to_group_channel(data, cookies, ua):
    cookie_file = client.files_upload_v2(
            title="Cookies",
            filename="cookies.txt",
            content=str(cookies),
        )
    cookie_url = cookie_file.get("file").get("permalink")
    user_file = client.files_upload_v2(
        title="User-Agent",
        filename="userAgent.txt",
        content=str(ua),
    )
    user_url = user_file.get("file").get("permalink")
    
    client.chat_postMessage(
        channel="#lippufy-bot",
        text=f"{data}\n*User-Agent:* {user_url}\n*Cookie:* {cookie_url}",
        parse="mrkdwn"
    )

if __name__ == '__main__':
    app.run(debug=True, port=80)
    
