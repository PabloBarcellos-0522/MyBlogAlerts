from datetime import datetime
from typing import List
from src.domain.models.Discipline import Discipline
from src.domain.repositories.Post_Repository import PostRepository, Post
from src.infrastructure.database.Connection import Connection


class PostDatabase(PostRepository):

    def save(self, post: Post) -> None:
        values = (post.Post_date, post.Post_Url, post.Discipline_id, post.Content)
        query = 'INSERT INTO post ("Post_Date", "Post_Url", "Discipline_id", "Text_Content") VALUES ' + str(values)

        try:
            with Connection() as db:
                db.run_query(query)
        finally:
            pass

    def get_posts(self) -> List[tuple]:
        query = 'SELECT * FROM post'

        try:
            with Connection() as db:
                db.run_query(query)
                resp = db.catch_all()
        finally:
            return resp

    def change_post_date(self, post: Post, date: datetime) -> None:
        query = f'''
            UPDATE post
            SET "Post_Date" = '{date}'
            WHERE "idPost" = '{post.idPost}';
        '''

        try:
            with Connection() as db:
                db.run_query(query)
        finally:
            pass

    def change_id_discipline(self, post: Post, discipline_id: Discipline.idDiscipline) -> None:
        query = f'''
            UPDATE post
            SET "Discipline_id" = '{discipline_id}'
            WHERE "idPost" = '{post.idPost}';
        '''

        try:
            with Connection() as db:
                db.run_query(query)
        finally:
            pass

    def change_url(self, post: Post, url: str) -> None:
        query = f'''
            UPDATE post
            SET "Post_Url" = '{url}'
            WHERE "idPost" = '{post.idPost}';
        '''

        try:
            with Connection() as db:
                db.run_query(query)
        finally:
            pass

    def delete(self, post: Post) -> None:
        query = f'''
            DELETE FROM post 
            WHERE "idPost" = '{post.idPost}';
        '''

        try:
            with Connection() as db:
                db.run_query(query)
        finally:
            pass
