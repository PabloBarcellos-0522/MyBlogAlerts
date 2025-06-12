import os
from dotenv import load_dotenv
import requests
from src.infrastructure.WhatsappAPI.Green_Connect import WhatsappConnect


class SendMensage(WhatsappConnect):
    def __init__(self):
        load_dotenv()
        self.connection = requests.session()
        self.url = os.getenv('API_URL')
        self.group_id = os.getenv('GROUP_ID')

    def student_msg(self, phone: str, msg: str):
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

    def group_msg(self, chat_id: int, msg: str):
        payload = {
            "chatId": str(self.group_id) + "@g.us",
            "message": msg,
            "linkPreview": False
        }
        headers = {
            'Content-Type': 'application/json'
        }

        response = self.connection.post(self.url, json=payload, headers=headers)
        return response.text.encode('utf8')
