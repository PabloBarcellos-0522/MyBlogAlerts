
from src.domain.models.Student import Student
from abc import ABC, abstractmethod


class StudentRepository(ABC):
    @abstractmethod
    def save(self, student: Student) -> None:
        pass

    @abstractmethod
    def chage_number(self, student: Student, new_phone: str) -> None:
        pass

    @abstractmethod
    def change_password(self, student: Student, password: str) -> None:
        pass

    @abstractmethod
    def change_registration(self, student: Student, registration: str) -> None:
        pass

    @abstractmethod
    def delete(self, student: Student) -> None:
        pass
