import threading
import time
from typing import List, Callable, Optional
import requests
from bs4 import BeautifulSoup
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

            # Initialize a set to track posts handled in this cycle
            processed_posts_this_cycle = set()

            # 2. If validation passes, run the main processing logic.
            self._run_processing_loop(processed_posts_this_cycle)

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

    def _run_processing_loop(self, processed_posts_this_cycle: set):
        """Contains the actual student processing loop."""
        print("Starting synchronization process using in-memory data...")
        students = self.store.students
        if not students:
            print("No students found in the in-memory store. A full sync may be required.")
            return

        for student in students:
            print(f"\nProcessing student: {student.name}")
            session: Optional[requests.Session] = None
            try:
                login_result = self.scraping_service.login(student.registration, student.password)
                if not login_result:
                    print(f"Login failed for student {student.name}. Skipping this student.")
                    continue
                session, dashboard_html = login_result
                
                self._sync_student_disciplines(student, session, dashboard_html)

                student_discipline_ids = {
                    sd.id_discipline for sd in self.store.student_disciplines if sd.id_student == student.id_student
                }
                student_disciplines = [
                    d for d in self.store.disciplines if d.id_discipline in student_discipline_ids
                ]

                if not student_disciplines:
                    print(f"No disciplines found in store for student {student.name}. Skipping post search.")
                    continue

                self._sync_discipline_posts(student, student_disciplines, processed_posts_this_cycle, session)

            except Exception as e:
                # This handles non-critical errors for a single student (e.g., login failure).
                # The loop will continue to the next student.
                print(f"An error occurred while processing student {student.name}: {e}")
            finally:
                if session: # Only logout if login was successful
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

    def _sync_student_disciplines(self, student: Student, session: requests.Session, dashboard_html: BeautifulSoup):
        """
        Fetches disciplines from scraping, finds or creates them,
        and associates them with the student, updating the in-memory store.
        """
        print("  Syncing disciplines...")
        scraped_disciplines = self.scraping_service.get_disciplines(session, dashboard_html)
        if not scraped_disciplines:
            print("  No disciplines found in scraping.")
            return
        

        student_discipline_ids = {sd.id_discipline for sd in self.store.student_disciplines if sd.id_student == student.id_student}

        disciplines_of_student = [
            d for d in self.store.disciplines 
            if d.id_discipline in student_discipline_ids
        ]

        scraped_ids = {d.id_cripto for d in scraped_disciplines}
        subjects_to_remove = [d for d in disciplines_of_student if d.id_cripto not in scraped_ids]
        ids_to_remove = {d.id_discipline for d in subjects_to_remove}

        print("  Checking for deleted disciplines...")
        for d in subjects_to_remove:
            print(f"    Deleting discipline '{student.id_student, d.name}'...")
            self.student_discipline_repo.delete(student.id_student, d.id_discipline)
        if (len(ids_to_remove) > 0):
            self.store.student_disciplines = [
                sd for sd in self.store.student_disciplines 
                if sd.id_discipline not in ids_to_remove
            ]
            

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

    def _sync_discipline_posts(self, current_student: Student, disciplines: List[Discipline], processed_posts_this_cycle: set, session: requests.Session):
        """
        Fetches posts, and for each new post, finds all relevant students,
        notifies them, saves the post, and marks it as processed for this cycle.
        """
        print("  Syncing posts...")
        for discipline in disciplines:
            print(f"    Checking posts for '{discipline.name}'...")
            scraped_posts = self.scraping_service.get_posts(session, discipline)
            if not scraped_posts:
                continue

            for post in reversed(scraped_posts):
                # 1. Check if post is already in the main store (old post)
                is_old_post = any(
                    p.post_url == post.post_url and p.post_date == post.post_date
                    for p in self.store.posts
                )
                if is_old_post:
                    continue

                # 2. Check if post was already handled in this sync cycle
                if post.post_url in processed_posts_this_cycle:
                    continue

                # 3. This is a genuinely new post for this cycle. Process it.
                print(f"      New post found in '{discipline.name}'. Notifying all relevant students...")

                # Find all students for this discipline
                target_student_ids = {
                    sd.id_student
                    for sd in self.store.student_disciplines
                    if sd.id_discipline == discipline.id_discipline
                }
                target_students = [s for s in self.store.students if s.id_student in target_student_ids]

                if not target_students:
                    print("        Warning: New post found but no students are associated with the discipline.")
                    continue
                
                # Send notifications to all target students
                message = f"Novo aviso em *{discipline.name}*:\n\n{post.content}\n\n*Url:* {post.post_url}"
                for student_to_notify in target_students:
                    print(f"        Sending DM to {student_to_notify.name} ({student_to_notify.phone_number})")
                    # Send direct message using the notification service
                    threading.Thread(target=self.notification_service.student_msg, args=(student_to_notify.phone_number, message)).start()
                    time.sleep(1) # Small delay to avoid rate-limiting

                # 4. Save the post to DB and main store
                self.post_repo.save(post)
                self.store.add_post(post)

                # 5. Mark post as processed for this cycle to avoid duplicate notifications
                processed_posts_this_cycle.add(post.post_url)
                time.sleep(3) # A longer delay after a batch of notifications for a new post
