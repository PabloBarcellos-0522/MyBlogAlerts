from typing import List
from src.domain.repositories.Discipline_Repository import DisciplineRepository, Discipline
from src.infrastructure.database.Connection import Connection


class DisciplineDatabase(DisciplineRepository):
    def save(self, discipline: Discipline) -> None:
        values = (discipline.Name, discipline.Id_Cipto)
        query = 'INSERT INTO discipline ("Name", "Id_Cripto") VALUES ' + str(values)

        try:
            with Connection() as db:
                db.run_query(query)
        finally:
            pass

    def get_disciplines(self) -> List[tuple]:
        query = 'SELECT "idDiscipline", "Name", "Id_Cripto" FROM discipline'

        try:
            with Connection() as db:
                db.run_query(query)
                resp = db.catch_all()
        finally:
            return resp

    def chage_name(self, discipline: Discipline, name: str) -> None:
        query = f'''
            UPDATE discipline
            SET "Name" = '{name}'
            WHERE "idDiscipline" = '{discipline.idDiscipline}';
        '''

        try:
            with Connection() as db:
                db.run_query(query)
        finally:
            pass

    def chage_id_cripto(self, discipline: Discipline, new_id: str) -> None:
        query = f'''
            UPDATE discipline
            SET "Id_Cripto" = '{new_id}'
            WHERE "idDiscipline" = '{discipline.idDiscipline}';
        '''

        try:
            with Connection() as db:
                db.run_query(query)
        finally:
            pass

    def delete(self, discipline: Discipline) -> None:
        query = f'''
            DELETE FROM discipline 
            WHERE "idDiscipline" = '{discipline.idDiscipline}';
        '''

        try:
            with Connection() as db:
                db.run_query(query)
        finally:
            pass
