from typing import List
from src.domain.repositories.Student_Discipline_Repository import StudentDisciplineRepository, StudentDiscipline
from src.infrastructure.database.Connection import Connection


class StudentDisciplineDatabase(StudentDisciplineRepository):
    def save(self, stu_disc: StudentDiscipline) -> None:
        values = (stu_disc.Id_Student, stu_disc.Id_Discupline)
        query = 'INSERT INTO student_discipline ("Student_idStudent", "Discipline_idDiscipline") VALUES ' + str(values)

        try:
            with Connection() as db:
                db.run_query(query)
        finally:
            pass

    def get_students_disciplines(self) -> List[tuple]:
        query = 'SELECT * FROM student_discipline'

        try:
            with Connection() as db:
                db.run_query(query)
                resp = db.catch_all()
        finally:
            return resp

    def chage_student(self, stu_disc: StudentDiscipline, new_id: int) -> None:
        query = f'''
            UPDATE student_discipline
            SET "Student_idStudent" = '{new_id}'
            WHERE "Student_idStudent" = '{stu_disc.Id_Student}' and "Discipline_idDiscipline" = '{stu_disc.Id_Discupline}';
        '''

        try:
            with Connection() as db:
                db.run_query(query)
        finally:
            pass

    def change_discipline(self, stu_disc: StudentDiscipline, new_id: int) -> None:
        query = f'''
            UPDATE student_discipline
            SET "Discipline_idDiscipline" = '{new_id}'
            WHERE "Student_idStudent" = '{stu_disc.Id_Student}' and "Discipline_idDiscipline" = '{stu_disc.Id_Discupline}';
        '''

        try:
            with Connection() as db:
                db.run_query(query)
        finally:
            pass

    def delete(self, stu_disc: StudentDiscipline) -> None:
        query = f'''
            DELETE FROM student_discipline 
            WHERE "Student_idStudent" = '{stu_disc.Id_Student}' and "Discipline_idDiscipline" = '{stu_disc.Id_Discupline}';
        '''

        try:
            with Connection() as db:
                db.run_query(query)
        finally:
            pass
