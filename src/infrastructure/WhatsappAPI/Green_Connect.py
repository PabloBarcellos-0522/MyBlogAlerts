import os
from dotenv import load_dotenv
import requests


class WhatsappConnect:
    def __init__(self):
        load_dotenv()
        self.connection = requests.session()
        self.url = os.getenv('API_URL')
        print(self.url)

    def send_msg(self, phone: str, msg: str):
        payload = {
            "chatId": phone + "@c.us",
            "message": msg,
            "linkPreview": False
        }
        headers = {
            'Content-Type': 'application/json'
        }

        response = self.connection.post(self.url, json=payload, headers=headers)
        return response.text.encode('utf8')

    def send_msg_on_group(self, chat_id: int, msg: str):
        payload = {
            "chatId": str(chat_id) + "@g.us",
            "message": msg,
            "linkPreview": False
        }
        headers = {
            'Content-Type': 'application/json'
        }

        response = self.connection.post(self.url, json=payload, headers=headers)
        return response.text.encode('utf8')
