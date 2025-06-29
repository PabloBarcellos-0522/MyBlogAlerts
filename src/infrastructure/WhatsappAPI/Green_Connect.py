from abc import ABC, abstractmethod


class WhatsappConnect(ABC):
    @abstractmethod
    def student_msg(self, phone: str, msg: str): pass

    @abstractmethod
    def group_msg(self, msg: str): pass
