from datetime import datetime, date
from typing import Optional, List

import psycopg2

from src.domain.models.Discipline import Discipline
from src.domain.models.Post import Post
from src.domain.repositories.Post_Repository import PostRepository
from src.infrastructure.database.Connection import Connection


class PostPgRepository(PostRepository):

    def save(self, post: Post) -> None:
        query = 'INSERT INTO post ("Post_Date", "Post_Url", "Discipline_id", "Text_Content") VALUES (%s, %s, %s, %s)'
        # psycopg2 requires a tuple for values, even for one element.
        values = (post.post_date.strftime('%Y-%m-%d'), post.post_url, post.discipline_id, post.content)
        try:
            with Connection() as db:
                db.run_query(query, values)
        except Exception as e:
            print(f"Failed to save post: {e}")

    def find_by_url_and_date(self, url: str, post_date: date) -> Optional[Post]:
        query = 'SELECT "idPost", "Post_Date", "Post_Url", "Discipline_id", "Text_Content" FROM post WHERE "Post_Url" = %s AND "Post_Date" = %s'
        try:
            with Connection() as db:
                db.run_query(query, (url, post_date.strftime('%Y-%m-%d')))
                resp = db.catch_one()

            if not resp:
                return None

            return Post(id_post=resp[0], post_date=resp[1], post_url=resp[2], discipline_id=resp[3], content=resp[4])

        except psycopg2.OperationalError as e:
            print(f"\tDB Error while finding post: {e}. Returning None.")
            return None

    def get_all(self) -> Optional[List[Post]]:
        query = 'SELECT "idPost", "Post_Date", "Post_Url", "Discipline_id", "Text_Content" FROM post'
        posts = []
        try:
            with Connection() as db:
                db.run_query(query)
                resp = db.catch_all()

            if not resp:
                return None

            for row in resp:
                posts.append(Post(id_post=row[0], post_date=row[1], post_url=row[2], discipline_id=row[3], content=row[4]))

        except psycopg2.OperationalError as e:
            print(f"\tDB Error while fetching all posts: {e}. Returning None.")
            return None
        return posts

    def change_post_date(self, post_id: int, new_date: date) -> None:
        query = 'UPDATE post SET "Post_Date" = %s WHERE "idPost" = %s;'
        try:
            with Connection() as db:
                db.run_query(query, (new_date.strftime('%Y-%m-%d'), post_id))
        except Exception as e:
            print(f"Failed to change post date: {e}")

    def change_id_discipline(self, post_id: int, discipline_id: int) -> None:
        query = 'UPDATE post SET "Discipline_id" = %s WHERE "idPost" = %s;'
        try:
            with Connection() as db:
                db.run_query(query, (discipline_id, post_id))
        except Exception as e:
            print(f"Failed to change post discipline ID: {e}")

    def change_url(self, post_id: int, url: str) -> None:
        query = 'UPDATE post SET "Post_Url" = %s WHERE "idPost" = %s;'
        try:
            with Connection() as db:
                db.run_query(query, (url, post_id))
        except Exception as e:
            print(f"Failed to change post URL: {e}")

    def delete(self, post_id: int) -> None:
        query = 'DELETE FROM post WHERE "idPost" = %s;'
        try:
            with Connection() as db:
                db.run_query(query, (post_id,))
        except Exception as e:
            print(f"Failed to delete post: {e}")
