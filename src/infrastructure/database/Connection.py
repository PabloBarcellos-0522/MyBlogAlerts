import os
from typing import List
from dotenv import load_dotenv
import psycopg2


class Connection:
    def __init__(self):
        load_dotenv()
        self.database_url = os.getenv('DATABASE_URL')

    def __enter__(self):
        try:
            self.conn = psycopg2.connect(self.database_url)
            self.cur = self.conn.cursor()
            return self
        except psycopg2.OperationalError as e:
            error_message = str(e)
            print(f"ERRO DE CONEXÃO OPERACIONAL:")
            print(f"Detalhes: {error_message}")
            raise e

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.cur and self.conn:
            self.conn.commit()
            self.conn.close()
        if self.cur:
            self.cur.close()

    def run_query(self, query: str):
        if self.cur:
            self.cur.execute('SET search_path TO "MyBlogAlerts"')
            self.cur.execute(query)

    def catch(self) -> tuple:
        result = ()
        if self.cur:
            result = self.cur.fetchone()
        return result

    def catch_all(self) -> List[tuple]:
        result = ()
        if self.cur:
            result = self.cur.fetchall()
        return result
