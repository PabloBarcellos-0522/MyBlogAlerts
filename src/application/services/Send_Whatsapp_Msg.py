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
        try:
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
        except requests.exceptions.RequestException as e:
            print(f"Erro de rede: {e}\n\nSeguindo programa. . .")
            return None

    def group_msg(self, msg: str):
        try:
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
        except requests.exceptions.RequestException as e:
            print(f"Erro de rede: {e}\n\nSeguindo programa. . .")
            return None
