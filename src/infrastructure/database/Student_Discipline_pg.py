from typing import List, Optional

import psycopg2

from src.domain.models.Discipline import Discipline
from src.domain.models.Student_Discipline import StudentDiscipline
from src.domain.repositories.Student_Discipline_Repository import StudentDisciplineRepository
from src.infrastructure.database.Connection import Connection


class StudentDisciplinePgRepository(StudentDisciplineRepository):
    def save(self, stu_disc: StudentDiscipline) -> None:
        query = 'INSERT INTO student_discipline ("Student_idStudent", "Discipline_idDiscipline") VALUES (%s, %s)'
        values = (stu_disc.id_student, stu_disc.id_discipline)

        try:
            with Connection() as db:
                db.run_query(query, values)
        except Exception as e:
            print(f"Failed to save student-discipline association: {e}")

    def exists(self, student_id: int, discipline_id: int) -> bool:
        query = 'SELECT 1 FROM student_discipline WHERE "Student_idStudent" = %s AND "Discipline_idDiscipline" = %s'
        try:
            with Connection() as db:
                db.run_query(query, (student_id, discipline_id))
                return db.catch_one() is not None
        except psycopg2.OperationalError as e:
            print(f"\tDB Error while checking student-discipline existence: {e}.")
            return False

    def get_disciplines_by_student_id(self, student_id: int) -> Optional[List[Discipline]]:
        query = """
            SELECT d."idDiscipline", d."Name", d."Id_Cripto"
            FROM discipline d
            JOIN student_discipline sd ON d."idDiscipline" = sd."Discipline_idDiscipline"
            WHERE sd."Student_idStudent" = %s
        """
        disciplines = []
        try:
            with Connection() as db:
                db.run_query(query, (student_id,))
                resp = db.catch_all()

            if not resp:
                return None

            for row in resp:
                disciplines.append(Discipline(id_discipline=row[0], name=row[1], id_cripto=row[2]))

        except psycopg2.OperationalError as e:
            print(f"\tDB Error while fetching disciplines for student {student_id}: {e}.")
            return None
        return disciplines

    def get_all(self) -> Optional[List[StudentDiscipline]]:
        query = 'SELECT "Student_idStudent", "Discipline_idDiscipline" FROM student_discipline'
        associations = []
        try:
            with Connection() as db:
                db.run_query(query)
                resp = db.catch_all()

            if not resp:
                return None

            for row in resp:
                associations.append(StudentDiscipline(id_student=row[0], id_discipline=row[1]))

        except psycopg2.OperationalError as e:
            print(f"\tDB Error while fetching all student-discipline associations: {e}.")
            return None
        return associations

    def get_students_disciplines(self) -> List[tuple]:
        query = 'SELECT * FROM student_discipline'

        resp = None
        try:
            with Connection() as db:
                db.run_query(query)
                resp = db.catch_all()
        except psycopg2.OperationalError as e:
            print("\tFalha ao obter Student_Disciplines devido a erro de DB. Retornando None.\n")
        # finally:
        #     return resp

    def get_this_student(self, stu_id: int) -> List[tuple]:
        query = 'SELECT * FROM student_discipline where "Student_idStudent" = %s'
        resp = None
        try:
            with Connection() as db:
                db.run_query(query, (stu_id,))
                resp = db.catch_all()
        except psycopg2.OperationalError as e:
            print("\tFalha ao obter Student_Disciplines devido a erro de DB. Retornando None.\n")
        # finally:
        #     return resp

    def change_student(self, student_id: int, discipline_id: int, new_student_id: int) -> None:
        query = 'UPDATE student_discipline SET "Student_idStudent" = %s WHERE "Student_idStudent" = %s AND "Discipline_idDiscipline" = %s;'
        try:
            with Connection() as db:
                db.run_query(query, (new_student_id, student_id, discipline_id))
        except Exception as e:
            print(f"Failed to change student in association: {e}")

    def change_discipline(self, student_id: int, discipline_id: int, new_discipline_id: int) -> None:
        query = 'UPDATE student_discipline SET "Discipline_idDiscipline" = %s WHERE "Student_idStudent" = %s AND "Discipline_idDiscipline" = %s;'
        try:
            with Connection() as db:
                db.run_query(query, (new_discipline_id, student_id, discipline_id))
        except Exception as e:
            print(f"Failed to change discipline in association: {e}")

    def delete(self, student_id: int, discipline_id: int) -> None:
        query = 'DELETE FROM student_discipline WHERE "Student_idStudent" = %s AND "Discipline_idDiscipline" = %s;'
        try:
            with Connection() as db:
                db.run_query(query, (student_id, discipline_id))
        except Exception as e:
            print(f"Failed to delete student-discipline association: {e}")

    def delete_by_student_id(self, student_id: int) -> None:
        query = 'DELETE FROM student_discipline WHERE "Student_idStudent" = %s;'
        try:
            with Connection() as db:
                db.run_query(query, (student_id,))
        except Exception as e:
            print(f"Failed to delete associations for student {student_id}: {e}")
