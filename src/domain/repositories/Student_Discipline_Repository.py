from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.models.Student_Discipline import StudentDiscipline
from src.domain.models.Discipline import Discipline


class StudentDisciplineRepository(ABC):
    @abstractmethod
    def save(self, student_discipline: StudentDiscipline) -> None:
        """
        Saves a new student-discipline association.
        :param student_discipline: The StudentDiscipline object to save.
        """
        raise NotImplementedError

    @abstractmethod
    def get_disciplines_by_student_id(self, student_id: int) -> Optional[List[Discipline]]:
        """
        Returns all disciplines associated with a student.
        :param student_id: The ID of the student.
        :return: A list of Discipline objects or None if none are found.
        """
        raise NotImplementedError

    @abstractmethod
    def exists(self, student_id: int, discipline_id: int) -> bool:
        """
        Checks if an association between a student and a discipline exists.
        :param student_id: The ID of the student.
        :param discipline_id: The ID of the discipline.
        :return: True if the association exists, False otherwise.
        """
        raise NotImplementedError

    @abstractmethod
    def get_all(self) -> Optional[List[StudentDiscipline]]:
        """
        Returns all student-discipline associations from the database.
        :return: A list of StudentDiscipline objects or None if none are found.
        """
        raise NotImplementedError

    @abstractmethod
    def delete_by_student_id(self, student_id: int) -> None:
        """
        Deletes all discipline associations for a given student ID.
        :param student_id: The ID of the student whose associations should be deleted.
        """
        raise NotImplementedError
    