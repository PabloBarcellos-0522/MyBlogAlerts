from abc import ABC, abstractmethod


class NotificationService(ABC):
    @abstractmethod
    def send_notification(self, message: str) -> None:
        """
        Sends a notification message.
        :param message: The content of the message to be sent.
        """
        raise NotImplementedError
