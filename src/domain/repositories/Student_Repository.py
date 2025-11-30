from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.models.Student import Student


class StudentRepository(ABC):
    @abstractmethod
    def get_all(self) -> Optional[List[Student]]:
        """
        Returns all students from the database.
        :return: A list of Student objects or None if no students are found.
        """
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, student_id: int) -> Optional[Student]:
        """
        Returns a student by its ID.
        :param student_id: The ID of the student.
        :return: A Student object or None if not found.
        """
        raise NotImplementedError

    @abstractmethod
    def find_by_registration(self, registration: str) -> Optional[Student]:
        """
        Finds a student by their registration number.
        :param registration: The registration number to search for.
        :return: A Student object or None if not found.
        """
        raise NotImplementedError

    @abstractmethod
    def save(self, student: Student) -> None:
        """
        Saves a student to the database.
        :param student: The student object to save.
        """
        raise NotImplementedError

    @abstractmethod
    def delete(self, student_id: int) -> None:
        """
        Deletes a student from the database by their ID.
        :param student_id: The ID of the student to delete.
        """
        raise NotImplementedError