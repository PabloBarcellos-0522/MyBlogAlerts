import threading
import time
from typing import List, Callable, Optional

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
    It includes a self-recovery mechanism with limited retries.
    """

    def __init__(self,
                 store: InMemoryStore,
                 discipline_repo: DisciplineRepository,
                 student_discipline_repo: StudentDisciplineRepository,
                 post_repo: PostRepository,
                 scraping_service: ScrapingService,
                 notification_service: NotificationService,
                 sync_callback: Optional[Callable[[], None]] = None):
        self.store = store
        self.discipline_repo = discipline_repo
        self.student_discipline_repo = student_discipline_repo
        self.post_repo = post_repo
        self.scraping_service = scraping_service
        self.notification_service = notification_service
        self.sync_callback = sync_callback

        # State for recovery mechanism
        self.max_recovery_attempts = 3
        self.recovery_attempts = 0

    def reset_recovery_state(self):
        """Resets the recovery attempt counter. To be called by an external scheduler."""
        if self.recovery_attempts > 0:
            print("--- Recovery state has been reset. ---")
            self.recovery_attempts = 0

    def execute(self):
        """
        Executes the main logic of the use case. If a critical error occurs
        (e.g., due to corrupted in-memory data), it will attempt to trigger a
        recovery sync via the provided callback.
        """
        try:
            # 1. Validate the store state before starting the expensive loop.
            if self.store.students is None or \
               self.store.disciplines is None or \
               self.store.student_disciplines is None or \
               self.store.posts is None:
                raise ValueError("In-memory store is in a corrupted state (contains None).")

            # 2. If validation passes, run the main processing logic.
            self._run_processing_loop()

            # 3. If the logic completes successfully, it means the system is healthy.
            # Reset the counter if it was previously in a failed state.
            if self.recovery_attempts > 0:
                print("--- System has recovered successfully. Resetting recovery counter. ---")
                self.reset_recovery_state()

        except Exception as e:
            # 4. If validation or the main loop fails, handle the failure.
            print(f"!!! A critical error occurred during execution: {e} !!!")
            self._handle_execution_failure()
            # Re-raise the exception so the caller knows the execution failed.
            raise

    def _run_processing_loop(self):
        """Contains the actual student processing loop."""
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
                # This handles non-critical errors for a single student (e.g., login failure).
                # The loop will continue to the next student.
                print(f"An error occurred while processing student {student.name}: {e}")
            finally:
                self.scraping_service.logout()
                print(f"Finished processing student: {student.name}")
                time.sleep(1)

        print("\nSynchronization process finished.")

    def _handle_execution_failure(self):
        """Handles the recovery logic when a critical error occurs."""
        if self.recovery_attempts < self.max_recovery_attempts:
            self.recovery_attempts += 1
            print(f"--- This is recovery attempt {self.recovery_attempts}/{self.max_recovery_attempts}. ---")
            if self.sync_callback:
                print("--- Triggering emergency recovery sync... ---")
                try:
                    self.sync_callback()
                    print("--- Emergency recovery sync callback completed. ---")
                except Exception as sync_error:
                    print(f"!!! The emergency recovery sync itself failed: {sync_error} !!!")
            else:
                print("--- No sync callback provided. Cannot attempt recovery. ---")
        else:
            print(f"--- Max recovery attempts ({self.max_recovery_attempts}) reached. Backing off. ---")

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

            db_discipline = next((d for d in self.store.disciplines if d.name == scraped_discipline.name and d.id_cripto == scraped_discipline.id_cripto), None)

            if db_discipline is None:
                print(f"    New discipline found: '{scraped_discipline.name}'. Saving...")
                saved_discipline = self.discipline_repo.save(scraped_discipline)
                self.store.add_discipline(saved_discipline)
                db_discipline = saved_discipline

            association_exists = any(
                sd.id_student == student.id_student and sd.id_discipline == db_discipline.id_discipline
                for sd in self.store.student_disciplines
            )
            if not association_exists:
                print(f"    Associating student with '{db_discipline.name}'...")
                new_association = StudentDiscipline(student.id_student, db_discipline.id_discipline)
                self.student_discipline_repo.save(new_association)
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

            for post in reversed(scraped_posts):
                existing_post = any(
                    p.post_url == post.post_url and p.post_date == post.post_date
                    for p in self.store.posts
                )
                if not existing_post:
                    print(f"      New post found in '{discipline.name}'. Saving and notifying...")

                    self.post_repo.save(post)
                    self.store.add_post(post)

                    message = f"Novo aviso em *{discipline.name}*:\n\n{post.content}\n\n*Url:* {post.post_url}"
                    threading.Thread(target=self.notification_service.send_notification, args=(message,)).start()
                    time.sleep(3)
