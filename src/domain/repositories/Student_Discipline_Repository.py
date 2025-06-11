from typing import List
from src.domain.models.Student_Discipline import StudentDiscipline
from abc import ABC, abstractmethod


class StudentDisciplineRepository(ABC):
    @abstractmethod
    def save(self, stu_disc: StudentDiscipline) -> None: pass

    @abstractmethod
    def get_students_disciplines(self) -> List[tuple]: pass

    @abstractmethod
    def chage_student(self, stu_disc: StudentDiscipline, new_id: int) -> None: pass

    @abstractmethod
    def change_discipline(self, stu_disc: StudentDiscipline, new_id: int) -> None: pass

    @abstractmethod
    def delete(self, stu_disc: StudentDiscipline) -> None: pass
