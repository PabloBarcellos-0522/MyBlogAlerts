
import os
from dotenv import load_dotenv
import psycopg2

class Connection:
    def __init__(self):
        load_dotenv()
        self.database_url = os.getenv('DATABASE_URL')

    def __enter__(self):
        self.conn = psycopg2.connect(self.database_url)
        self.cur = self.conn.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.commit()
        self.cur.close()
        self.conn.close()

    def run_query(self, query: str):
        self.cur.execute('SET search_path TO "MyBlogAlerts"')
        self.cur.execute(query)

    def send(self) -> tuple:
        result = self.cur.fetchone()
        return result
