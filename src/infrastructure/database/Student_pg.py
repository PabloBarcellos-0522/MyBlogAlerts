from typing import List
from src.domain.repositories.Student_Repository import StudentRepository, Student
from src.infrastructure.database.Connection import Connection


class StudentDatabase(StudentRepository):
    def save(self, student: Student) -> None:
        values = (student.Phone_Number, student.Password, student.Registration)
        query = 'INSERT INTO student ("Phone_Number", "Password", "Registration") VALUES ' + str(values)

        try:
            with Connection() as db:
                db.run_query(query)
        finally:
            pass

    def get_students(self) -> List[tuple]:
        query = 'SELECT * FROM student'

        try:
            with Connection() as db:
                db.run_query(query)
                resp = db.catch_all()
        finally:
            return resp

    def chage_number(self, student: Student, new_phone: str) -> None:
        query = f'''
            UPDATE student
            SET "Phone_Number" = '{new_phone}'
            WHERE "idStudent" = '{student.Id_Student}';
        '''

        try:
            with Connection() as db:
                db.run_query(query)
        finally:
            pass

    def change_password(self, student: Student, password: str) -> None:
        query = f'''
            UPDATE student
            SET "Password" = '{password}'
            WHERE "idStudent" = '{student.Id_Student}';
        '''

        try:
            with Connection() as db:
                db.run_query(query)
        finally:
            pass

    def change_registration(self, student: Student, registration: str) -> None:
        query = f'''
            UPDATE student
            SET "Registration" = '{registration}'
            WHERE "idStudent" = '{student.Id_Student}';
        '''

        try:
            with Connection() as db:
                db.run_query(query)
        finally:
            pass

    def change_name(self, student: Student, name: str) -> None:
        query = f'''
            UPDATE student
            SET "Name" = '{name}'
            WHERE "idStudent" = '{student.Id_Student}';
        '''

        try:
            with Connection() as db:
                db.run_query(query)
        finally:
            pass

    def delete(self, student: Student) -> None:
        query = f'''
            DELETE FROM student 
            WHERE "idStudent" = '{student.Id_Student}';
        '''

        try:
            with Connection() as db:
                db.run_query(query)
        finally:
            pass
