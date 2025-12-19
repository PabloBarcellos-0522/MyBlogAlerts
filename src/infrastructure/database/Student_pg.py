from typing import List, Optional
from src.domain.repositories.Student_Repository import StudentRepository
from src.domain.models.Student import Student
from src.infrastructure.database.Connection import Connection
import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet
import base64
import psycopg2

from src.application.services.InMemory_Store import InMemoryStore


class StudentPgRepository(StudentRepository):

    def __init__(self, in_memory_store: InMemoryStore):
        load_dotenv()
        self.SECRET_KEY = Fernet(os.getenv("WEB_SCRAPER_SECRET_KEY"))
        self.store = in_memory_store

    def get_by_phone_number(self, phone_number: str) -> Optional[Student]:
        """
        Finds a student by their phone number from the in-memory cache.
        This operation is fast and does not query the database.
        """
        print(f"Searching for student with phone {phone_number} in cache.")
        return self.store.get_student_by_phone(phone_number)

    def get_all(self) -> Optional[List[Student]]:
        query = 'SELECT "idStudent", "Phone_Number", "Password", "Name", "Registration" FROM student;'
        students = []
        try:
            with Connection() as db:
                db.run_query(query)
                resp = db.catch_all()

            if not resp:
                return None

            for row in resp:
                try:
                    id_s = row[0]
                    phone = self.SECRET_KEY.decrypt(base64.urlsafe_b64decode(row[1].encode("utf-8"))).decode("utf-8")
                    password = self.SECRET_KEY.decrypt(base64.urlsafe_b64decode(row[2].encode("utf-8"))).decode("utf-8")
                    name = self.SECRET_KEY.decrypt(base64.urlsafe_b64decode(row[3].encode("utf-8"))).decode("utf-8")
                    registration = self.SECRET_KEY.decrypt(base64.urlsafe_b64decode(row[4].encode("utf-8"))).decode(
                        "utf-8")
                    students.append(
                        Student(phone_number=phone, registration=registration, password=password, id_student=id_s,
                                name=name))
                except Exception:
                    print(f"Warning: Could not decrypt data for student ID {row[0]}. Skipping.")
                    continue

        except psycopg2.OperationalError as e:
            print(f"\tDB Error while fetching students: {e}. Returning empty list.")
            return None
        return students

    def get_by_id(self, student_id: int) -> Optional[Student]:
        query = 'SELECT "idStudent", "Phone_Number", "Password", "Name", "Registration" FROM student WHERE "idStudent" = %s;'
        try:
            with Connection() as db:
                db.run_query(query, (student_id,))
                resp = db.catch_one()

            if not resp:
                return None

            id_s = resp[0]
            phone = self.SECRET_KEY.decrypt(base64.urlsafe_b64decode(resp[1].encode("utf-8"))).decode("utf-8")
            password = self.SECRET_KEY.decrypt(base64.urlsafe_b64decode(resp[2].encode("utf-8"))).decode("utf-8")
            name = resp[3]
            registration = self.SECRET_KEY.decrypt(base64.urlsafe_b64decode(resp[4].encode("utf-8"))).decode("utf-8")

            return Student(phone_number=phone, registration=registration, password=password, id_student=id_s, name=name)

        except Exception as e:
            print(f"\tAn unexpected error occurred while fetching student by ID {student_id}: {e}")
            return None

    def find_by_registration(self, registration: str) -> Optional[Student]:
        # Primeiro, checa o cache para uma busca rápida
        print(f"Searching for student with registration {registration} in cache.")
        if self.store.students:
            for student in self.store.students:
                if student.registration == registration:
                    print("Found student in cache.")
                    return student

        # Se não estiver no cache, busca no banco de dados como fallback.
        # Nota: Isso é ineficiente devido à criptografia, mas é a única maneira com o design atual.
        print(f"Student not in cache. Querying database for registration {registration}.")
        all_students = self.get_all()
        if not all_students:
            return None

        for student in all_students:
            if student.registration == registration:
                print("Found student in database.")
                # Opcional: Adicionar ao cache para futuras buscas.
                # self.store.add_student(student)
                return student

        return None

    def save(self, student: Student) -> Student:
        name = self.SECRET_KEY.encrypt(student.name.encode('utf-8'))
        password = self.SECRET_KEY.encrypt(student.password.encode('utf-8'))
        registration = self.SECRET_KEY.encrypt(student.registration.encode('utf-8'))
        phone_number = self.SECRET_KEY.encrypt(student.phone_number.encode('utf-8'))

        name = base64.urlsafe_b64encode(name).decode("utf-8")
        password = base64.urlsafe_b64encode(password).decode("utf-8")
        registration = base64.urlsafe_b64encode(registration).decode("utf-8")
        phone_number = base64.urlsafe_b64encode(phone_number).decode("utf-8")

        query = 'INSERT INTO student ("Phone_Number", "Password", "Registration", "Name") VALUES (%s, %s, %s, %s) RETURNING "idStudent";'
        values = (phone_number, password, registration, name)

        try:
            with Connection() as db:
                db.run_query(query, values)
                new_id = db.catch_one()

            if new_id and new_id[0]:
                student.id_student = new_id[0]
                # Adiciona o novo aluno ao cache para manter a consistência
                if self.store.students is None:
                    self.store.students = []
                self.store.students.append(student)
                print(f"Student {student.name} saved to DB with ID {student.id_student} and added to cache.")
                return student
            else:
                raise Exception("Falha ao recuperar o ID do aluno recém-salvo.")
        except Exception as e:
            print(f"Failed to save student: {e}")
            raise e

    def change_number(self, student_id: int, new_phone: str) -> None:
        phone_number = base64.urlsafe_b64encode(self.SECRET_KEY.encrypt(new_phone.encode('utf-8'))).decode("utf-8")
        query = 'UPDATE student SET "Phone_Number" = %s WHERE "idStudent" = %s;'
        try:
            with Connection() as db:
                db.run_query(query, (phone_number, student_id))
        except Exception as e:
            print(f"Failed to change phone number: {e}")

    def change_password(self, student_id: int, password: str) -> None:
        password_enc = base64.urlsafe_b64encode(self.SECRET_KEY.encrypt(password.encode('utf-8'))).decode("utf-8")
        query = 'UPDATE student SET "Password" = %s WHERE "idStudent" = %s;'
        try:
            with Connection() as db:
                db.run_query(query, (password_enc, student_id))
        except Exception as e:
            print(f"Failed to change password: {e}")

    def change_registration(self, student_id: int, registration: str) -> None:
        registration_enc = base64.urlsafe_b64encode(self.SECRET_KEY.encrypt(registration.encode('utf-8'))).decode(
            "utf-8")
        query = 'UPDATE student SET "Registration" = %s WHERE "idStudent" = %s;'
        try:
            with Connection() as db:
                db.run_query(query, (registration_enc, student_id))
        except Exception as e:
            print(f"Failed to change registration: {e}")

    def change_name(self, student_id: int, name: str) -> None:
        query = 'UPDATE student SET "Name" = %s WHERE "idStudent" = %s;'
        try:
            with Connection() as db:
                db.run_query(query, (name, student_id))
        except Exception as e:
            print(f"Failed to change name: {e}")

    def delete(self, student_id: int) -> None:
        query = 'DELETE FROM student WHERE "idStudent" = %s;'
        try:
            with Connection() as db:
                db.run_query(query, (student_id,))
            
            if self.store.students:
                initial_count = len(self.store.students)
                self.store.students = [s for s in self.store.students if s.id_student != student_id]
                if len(self.store.students) < initial_count:
                    print(f"Student with ID {student_id} removed from cache.")
            print(f"Student with ID {student_id} deleted from DB.")
        except Exception as e:
            print(f"Failed to delete student: {e}")
            raise e

