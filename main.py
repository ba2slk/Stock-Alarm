import requests
from datetime import datetime, timedelta
from twilio.rest import Client
import os  #how to create env variables?

#API KEY & ENDPOINT
STOCK = "TSLA"
ALPHA_VANTAGE_API_KEY = "SECRET"
ALPHA_VANTAGE_ENDPOINT = "https://www.alphavantage.co/query"

COMPANY_NAME = "Tesla Inc"
NEWS_API_KEY = "SECRET"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"

TWILIO_ACCOUNT_SID = "SECRET"
TWILIO_AUTH_TOKEN = "SECRET"
account_sid = TWILIO_ACCOUNT_SID
auth_token = TWILIO_AUTH_TOKEN
client = Client(account_sid, auth_token)

#time variables
time_now = datetime.now()
time_yesterday = time_now - timedelta(1)
time_before_yesterday = time_now - timedelta(2)

str_time_yesterday = time_yesterday.strftime("%Y-%m-%d 16:00:00")
str_time_before_yesterday = time_before_yesterday.strftime("%Y-%m-%d 16:00:00")


def get_news():
    news_parameters = {
        "apiKey": NEWS_API_KEY,
        "q": COMPANY_NAME,
        "searchin": "title,description",
        "sortBy": "popularity",
        "language": "en"
    }
    response_newsapi = requests.get(NEWS_ENDPOINT, params=news_parameters)
    response_newsapi.raise_for_status()
    news_data = response_newsapi.json()
    articles = news_data["articles"]
    return articles


def send_message(article):
    title = article["title"]
    description = article["description"]
    message = client.messages \
        .create(
        body=f"{COMPANY_NAME}: {arrow}{close_variation_percentage}%\n\nHeadline: {title}\n\nBrief: {description}",
        from_="+15855801125",
        to="+8201012345678"
    )
    print(message.sid)


stock_parameters = {
    "function": "TIME_SERIES_INTRADAY",
    "symbol": STOCK,
    "interval": "60min",
    "apikey": ALPHA_VANTAGE_API_KEY
    }
response_stock = requests.get(ALPHA_VANTAGE_ENDPOINT, stock_parameters)
response_stock.raise_for_status()
stock_data = response_stock.json()
stock_data_time_series = stock_data["Time Series (60min)"]

try:
    close_price_yesterday = float(stock_data_time_series[str_time_yesterday]["4. close"])
    close_price_before_yesterday = float(stock_data_time_series[str_time_before_yesterday]["4. close"])
except KeyError:
    print("Data has not been refreshed.")
else:
    close_variation_percentage = round((close_price_yesterday - close_price_before_yesterday)) / close_price_yesterday * 100
    print(close_variation_percentage)
    if close_variation_percentage >= 5 or close_variation_percentage <= -5:
        news_articles = get_news()

        if close_variation_percentage > 0:
            arrow = "▲"
        else:
            close_variation_percentage *= -1
            arrow = "▼"

        if len(news_articles) <= 2:
            if not news_articles:
                print("No Articles Found.")

            for article in news_articles:
                send_message(article)
        else:
            for article in news_articles[:3]:
                send_message(article)