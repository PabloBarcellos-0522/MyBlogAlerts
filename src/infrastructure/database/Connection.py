import os
from typing import List, Optional
from dotenv import load_dotenv
import psycopg2


class Connection:
    def __init__(self):
        load_dotenv()
        self.database_url = os.getenv('DATABASE_URL')
        self.conn = None
        self.cur = None

    def __enter__(self):
        try:
            self.conn = psycopg2.connect(self.database_url)
            self.cur = self.conn.cursor()
            self.cur.execute('SET search_path TO "MyBlogAlerts"')
            return self
        except psycopg2.OperationalError as e:
            error_message = str(e)
            print(f"ERRO DE CONEXÃO OPERACIONAL:")
            print(f"Detalhes: {error_message}")
            raise e

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            if exc_type:
                self.conn.rollback()
                print("Transaction rolled back due to an exception.")
            else:
                self.conn.commit()
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()

    def run_query(self, query: str, values: Optional[tuple] = None):
        if self.cur:
            self.cur.execute(query, values)

    def catch_one(self) -> Optional[tuple]:
        if self.cur:
            return self.cur.fetchone()
        return None

    def catch_all(self) -> List[tuple]:
        if self.cur:
            return self.cur.fetchall()
        return []
