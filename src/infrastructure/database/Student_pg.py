from typing import List
from src.domain.repositories.Student_Repository import StudentRepository, Student
from src.infrastructure.database.Connection import Connection
import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet
import base64
import psycopg2


class StudentDatabase(StudentRepository):

    def __init__(self):
        load_dotenv()
        self.SECRET_KEY = Fernet(os.getenv("WEB_SCRAPER_SECRET_KEY"))

    def save(self, student: Student) -> None:
        password = self.SECRET_KEY.encrypt(student.Password.encode('utf-8'))
        registration = self.SECRET_KEY.encrypt(student.Registration.encode('utf-8'))
        phone_number = self.SECRET_KEY.encrypt(student.Phone_Number.encode('utf-8'))

        password = base64.urlsafe_b64encode(password).decode("utf-8")
        registration = base64.urlsafe_b64encode(registration).decode("utf-8")
        phone_number = base64.urlsafe_b64encode(phone_number).decode("utf-8")

        values = (phone_number, password, registration)
        query = 'INSERT INTO student ("Phone_Number", "Password", "Registration") VALUES ' + str(values)

        try:
            with Connection() as db:
                db.run_query(query)
        finally:
            pass

    def get_students(self) -> List[tuple]:
        query = 'SELECT "idStudent", "Phone_Number", "Password", "Name", "Registration" FROM student;'

        resp = []
        try:
            with Connection() as db:
                db.run_query(query)
                resp = db.catch_all()
            for i in range(len(resp)):
                phone = base64.urlsafe_b64decode(resp[i][1].encode("utf-8"))
                password = base64.urlsafe_b64decode(resp[i][2].encode("utf-8"))
                registration = base64.urlsafe_b64decode(resp[i][4].encode("utf-8"))

                phone = self.SECRET_KEY.decrypt(phone).decode("utf-8")
                password = self.SECRET_KEY.decrypt(password).decode("utf-8")
                registration = self.SECRET_KEY.decrypt(registration).decode("utf-8")

                resp[i] = (resp[i][0], phone, password, resp[i][3], registration)
        except psycopg2.OperationalError as e:
            print("\tFalha ao obter Estudantes devido a erro de DB. Retornando lista vazia.\n")
        finally:
            return resp

    def chage_number(self, student: Student, new_phone: str) -> None:
        phone_number = self.SECRET_KEY.encrypt(new_phone.encode('utf-8'))
        phone_number = base64.urlsafe_b64encode(phone_number).decode("utf-8")

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
        password = self.SECRET_KEY.encrypt(password.encode('utf-8'))
        password = base64.urlsafe_b64encode(password).decode("utf-8")

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
        registration = self.SECRET_KEY.encrypt(registration.encode('utf-8'))
        registration = base64.urlsafe_b64encode(registration).decode("utf-8")

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
