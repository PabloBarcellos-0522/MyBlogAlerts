import os
import time
from dotenv import load_dotenv
import requests
from src.domain.services.Notification_Service import NotificationService


class WhatsappNotificationService(NotificationService):
    def __init__(self, max_retries=15, retry_delay=60):
        load_dotenv()
        self.connection = requests.session()
        self.url = os.getenv('API_URL')
        self.group_id = os.getenv('GROUP_ID')
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    def send_notification(self, message: str) -> None:
        """Sends a message to the configured WhatsApp group."""
        payload = {
            "chatId": f"{self.group_id}@g.us",
            "message": message,
            "linkPreview": False
        }
        headers = {'Content-Type': 'application/json'}

        for attempt in range(self.max_retries):
            try:
                response = self.connection.post(self.url, json=payload, headers=headers)
                response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
                print(f"  Notification sent successfully: {message.splitlines()[0]}")
                return
            except requests.exceptions.RequestException as e:
                print(f"Network error on attempt {attempt + 1}/{self.max_retries}: {e}")
                if attempt < self.max_retries - 1:
                    print(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    print("Max retries reached. Failed to send notification.")
                    # Optionally, re-raise the exception or handle the failure
                    # raise e

    def student_msg(self, phone: str, msg: str):
        """Sends a direct message to a student."""
        payload = {
            "chatId": f"{phone}@c.us",
            "message": msg,
            "linkPreview": False
        }
        headers = {'Content-Type': 'application/json'}

        for attempt in range(self.max_retries):
            try:
                response = self.connection.post(self.url, json=payload, headers=headers)
                response.raise_for_status()
                print(f"Direct message to {phone} sent successfully.")
                return
            except requests.exceptions.RequestException as e:
                print(f"Network error on attempt {attempt + 1}/{self.max_retries}: {e}")
                if attempt < self.max_retries - 1:
                    print(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    print("Max retries reached. Failed to send direct message.")
