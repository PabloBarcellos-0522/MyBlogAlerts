import threading
import time
from typing import List

from src.application.services.InMemory_Store import InMemoryStore
from src.domain.models.Discipline import Discipline
from src.domain.models.Student import Student
from src.domain.models.Student_Discipline import StudentDiscipline
from src.domain.repositories.Discipline_Repository import DisciplineRepository
from src.domain.repositories.Post_Repository import PostRepository
from src.domain.repositories.Student_Discipline_Repository import StudentDisciplineRepository
from src.domain.services.Notification_Service import NotificationService
from src.domain.services.Scraping_Service import ScrapingService


class SyncAndNotifyUseCase:
    """
    This use case orchestrates synchronizing data from the academic portal,
    using an in-memory store to minimize database reads and notifying new posts.
    """

    def __init__(self,
                 store: InMemoryStore,
                 discipline_repo: DisciplineRepository,
                 student_discipline_repo: StudentDisciplineRepository,
                 post_repo: PostRepository,
                 scraping_service: ScrapingService,
                 notification_service: NotificationService):
        self.store = store
        self.discipline_repo = discipline_repo
        self.student_discipline_repo = student_discipline_repo
        self.post_repo = post_repo
        self.scraping_service = scraping_service
        self.notification_service = notification_service

    def execute(self):
        """
        Executes the main logic of the use case using in-memory data.
        """
        print("Starting synchronization process using in-memory data...")
        students = self.store.students
        if not students:
            print("No students found in the in-memory store. A full sync may be required.")
            return

        for student in students:
            print(f"\nProcessing student: {student.name}")
            try:
                self.scraping_service.login(student.registration, student.password)
                self._sync_student_disciplines(student)

                # Get all disciplines for the student from the store
                student_discipline_ids = {
                    sd.id_discipline for sd in self.store.student_disciplines if sd.id_student == student.id_student
                }
                student_disciplines = [
                    d for d in self.store.disciplines if d.id_discipline in student_discipline_ids
                ]

                if not student_disciplines:
                    print(f"No disciplines found in store for student {student.name}. Skipping post search.")
                    continue

                self._sync_discipline_posts(student_disciplines)

            except Exception as e:
                print(f"An error occurred while processing student {student.name}: {e}")
            finally:
                self.scraping_service.logout()
                print(f"Finished processing student: {student.name}")
                time.sleep(1)

        print("\nSynchronization process finished.")

    def _sync_student_disciplines(self, student: Student):
        """
        Fetches disciplines from scraping, finds or creates them,
        and associates them with the student, updating the in-memory store.
        """
        print("  Syncing disciplines...")
        scraped_disciplines = self.scraping_service.get_disciplines()
        if not scraped_disciplines:
            print("  No disciplines found in scraping.")
            return

        for scraped_discipline in scraped_disciplines:
            if scraped_discipline.id_cripto is None:
                continue

            # Check if discipline already exists in the store
            db_discipline = next((d for d in self.store.disciplines if d.name == scraped_discipline.name and d.id_cripto == scraped_discipline.id_cripto), None)

            # If not, save it to DB and add to store
            if db_discipline is None:
                print(f"    New discipline found: '{scraped_discipline.name}'. Saving...")
                # Save to DB to get an ID
                saved_discipline = self.discipline_repo.save(scraped_discipline)
                # Add the new discipline with its ID to the store
                self.store.add_discipline(saved_discipline)
                db_discipline = saved_discipline

            # Check if the student is already associated with the discipline in the store
            association_exists = any(
                sd.id_student == student.id_student and sd.id_discipline == db_discipline.id_discipline
                for sd in self.store.student_disciplines
            )
            if not association_exists:
                print(f"    Associating student with '{db_discipline.name}'...")
                new_association = StudentDiscipline(student.id_student, db_discipline.id_discipline)
                # Save to DB
                self.student_discipline_repo.save(new_association)
                # Add to store
                self.store.add_student_discipline_association(new_association)

    def _sync_discipline_posts(self, disciplines: List[Discipline]):
        """
        Fetches posts, and for each new post, saves it, notifies,
        and updates the in-memory store.
        """
        print("  Syncing posts...")
        for discipline in disciplines:
            print(f"    Checking posts for '{discipline.name}'...")
            scraped_posts = self.scraping_service.get_posts(discipline)
            if not scraped_posts:
                continue

            for post in reversed(scraped_posts):  # Process oldest first
                # Check if post already exists in the store
                existing_post = any(
                    p.post_url == post.post_url and p.post_date == post.post_date
                    for p in self.store.posts
                )
                if not existing_post:
                    print(f"      New post found in '{discipline.name}'. Saving and notifying...")

                    # Save the new post to DB
                    self.post_repo.save(post)
                    # Add to store
                    self.store.add_post(post)

                    # Send notification
                    message = f"Novo aviso em *{discipline.name}*:\n\n{post.content}\n\n*Url:* {post.post_url}"
                    threading.Thread(target=self.notification_service.send_notification, args=(message,)).start()
                    time.sleep(3)
