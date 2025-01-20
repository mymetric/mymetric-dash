import requests
import streamlit as st

def send_discord_message(message, username="Alert Bot"):

    webhook_url = st.secrets.general.discord_webhook_url

    """
    Sends a message to a Discord channel using a webhook.

    :param webhook_url: The Discord webhook URL.
    :param message: The message to send.
    :param username: The username to display for the bot.
    """
    data = {
        "content": message,
        "username": username
    }
    
    response = requests.post(webhook_url, json=data)
    
    if response.status_code == 204:
        print("Message sent successfully.")
    else:
        print(f"Failed to send message. Status code: {response.status_code}") 