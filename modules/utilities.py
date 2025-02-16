import requests
import streamlit as st

def send_zapi_message(message):
    zapi_payload = {
        "phone": "120363322379870288-group",
        # "phone": phone,
        "message": message
    }

    # Send to Z-API
    zapi_url = "https://api.z-api.io/instances/3CE918F241E11034C9538A74AFBCE7F1/token/33DD6E993D824A4F6506F9E9/send-text"
    headers = {
        "Client-Token": "F20791bc98f834faf975a53e26bf5eb74S"
    }

    requests.post(zapi_url, json=zapi_payload, headers=headers)


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

def send_message(message):
    send_zapi_message(message)
