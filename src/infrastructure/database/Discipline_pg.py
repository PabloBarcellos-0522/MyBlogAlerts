from typing import List, Optional
from src.domain.models.Discipline import Discipline
from src.domain.repositories.Discipline_Repository import DisciplineRepository
from src.infrastructure.database.Connection import Connection
import psycopg2


class DisciplinePgRepository(DisciplineRepository):
    def save(self, discipline: Discipline) -> Discipline:
        query = 'INSERT INTO discipline ("Name", "Id_Cripto") VALUES (%s, %s) RETURNING "idDiscipline";'
        values = (discipline.name, discipline.id_cripto)
        try:
            with Connection() as db:
                db.run_query(query, values)
                new_id = db.catch_one()[0]
                discipline.id_discipline = new_id
                return discipline
        except Exception as e:
            print(f"Failed to save discipline: {e}")
            raise e

    def get_all(self) -> Optional[List[Discipline]]:
        query = 'SELECT "idDiscipline", "Name", "Id_Cripto" FROM discipline'
        disciplines = []
        try:
            with Connection() as db:
                db.run_query(query)
                resp = db.catch_all()

            if not resp:
                return None

            for row in resp:
                disciplines.append(Discipline(id_discipline=row[0], name=row[1], id_cripto=row[2]))

        except psycopg2.OperationalError as e:
            print(f"\tDB Error while fetching disciplines: {e}. Returning None.")
            return None
        return disciplines

    def get_by_id(self, discipline_id: int) -> Optional[Discipline]:
        query = 'SELECT "idDiscipline", "Name", "Id_Cripto" FROM discipline WHERE "idDiscipline" = %s;'
        try:
            with Connection() as db:
                db.run_query(query, (discipline_id,))
                resp = db.catch_one()

            if not resp:
                return None

            return Discipline(id_discipline=resp[0], name=resp[1], id_cripto=resp[2])
        except psycopg2.OperationalError as e:
            print(f"\tDB Error while fetching discipline by ID: {e}. Returning None.")
            return None

    def find_by_name_and_id_cripto(self, name: str, id_cripto: str) -> Optional[Discipline]:
        query = 'SELECT "idDiscipline", "Name", "Id_Cripto" FROM discipline WHERE "Name" = %s AND "Id_Cripto" = %s;'
        try:
            with Connection() as db:
                db.run_query(query, (name, id_cripto))
                resp = db.catch_one()

            if not resp:
                return None

            return Discipline(id_discipline=resp[0], name=resp[1], id_cripto=resp[2])
        except psycopg2.OperationalError as e:
            print(f"\tDB Error while finding discipline: {e}. Returning None.")
            return None

    def change_name(self, discipline_id: int, name: str) -> None:
        query = 'UPDATE discipline SET "Name" = %s WHERE "idDiscipline" = %s;'
        try:
            with Connection() as db:
                db.run_query(query, (name, discipline_id))
        except Exception as e:
            print(f"Failed to change discipline name: {e}")

    def change_id_cripto(self, discipline_id: int, new_id_cripto: str) -> None:
        query = 'UPDATE discipline SET "Id_Cripto" = %s WHERE "idDiscipline" = %s;'
        try:
            with Connection() as db:
                db.run_query(query, (new_id_cripto, discipline_id))
        except Exception as e:
            print(f"Failed to change discipline crypto ID: {e}")

    def delete(self, discipline_id: int) -> None:
        query = 'DELETE FROM discipline WHERE "idDiscipline" = %s;'
        try:
            with Connection() as db:
                db.run_query(query, (discipline_id,))
        except Exception as e:
            print(f"Failed to delete discipline: {e}")
