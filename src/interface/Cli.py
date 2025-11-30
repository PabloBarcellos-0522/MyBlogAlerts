from datetime import datetime
import threading
from time import sleep
from typing import Tuple

# --- Dependency Imports ---
# Application Layer
from src.application.services.InMemory_Store import InMemoryStore
from src.application.use_cases.Sync_And_Notify import SyncAndNotifyUseCase
from src.application.services.Send_Whatsapp_Msg import WhatsappNotificationService
from src.application.use_cases.Save_Student import SaveStudent

# Domain Layer
from src.domain.models.Student import Student

# Infrastructure Layer (Concrete Implementations)
from src.infrastructure.database.Student_pg import StudentPgRepository
from src.infrastructure.database.Discipline_pg import DisciplinePgRepository
from src.infrastructure.database.Student_Discipline_pg import StudentDisciplinePgRepository
from src.infrastructure.database.Post_pg import PostPgRepository
from src.infrastructure.scraping.Scraping_Adapter import ScrapingAdapter


def setup_dependencies() -> Tuple[SyncAndNotifyUseCase, InMemoryStore, SaveStudent, dict]:
    """Instantiates and wires up all the dependencies."""
    print("Setting up dependencies...")
    # Instantiate repositories
    repos = {
        'student': StudentPgRepository(),
        'discipline': DisciplinePgRepository(),
        'student_discipline': StudentDisciplinePgRepository(),
        'post': PostPgRepository()
    }
    # Instantiate services
    scraping_service = ScrapingAdapter()
    notification_service = WhatsappNotificationService()
    # Instantiate the in-memory store
    store = InMemoryStore()

    # Instantiate the main use case
    sync_use_case = SyncAndNotifyUseCase(
        store=store,
        discipline_repo=repos['discipline'],
        student_discipline_repo=repos['student_discipline'],
        post_repo=repos['post'],
        scraping_service=scraping_service,
        notification_service=notification_service
    )
    
    # Instantiate the student management use case
    student_use_case = SaveStudent(
        student_repo=repos['student'],
        student_discipline_repo=repos['student_discipline'],
        scraping_service=scraping_service
    )
    
    return sync_use_case, store, student_use_case, repos


if __name__ == "__main__":
    # --- Dependency Injection ---
    sync_use_case, in_memory_store, register_student_use_case, repositories = setup_dependencies()
    
    global running
    running = True


    def perform_full_sync():
        in_memory_store.full_sync(
            student_repo=repositories['student'],
            discipline_repo=repositories['discipline'],
            post_repo=repositories['post'],
            student_discipline_repo=repositories['student_discipline']
        )


    def crawler_faculty():
        global running
        # Configuration
        sleep_time_seconds = 90
        sync_interval_minutes = 30
        cycles_for_resync = (sync_interval_minutes * 60) / sleep_time_seconds

        # Initial full sync before starting the loop
        perform_full_sync()
        
        cycle_count = 1
        while running:
            now = datetime.now()
            # Resync periodically
            if cycle_count >= cycles_for_resync:
                print(f"\n--- Scheduled Sync Triggered at: {now.strftime('%Y-%m-%d %H:%M:%S')} ---")
                perform_full_sync()
                cycle_count = 1  # Reset counter

            # Run sync logic only outside of "quiet hours" (e.g., 23:00 to 05:00)
            if not (23 <= now.hour or now.hour < 5):
                print(f"\n--- Cycle {cycle_count}/{int(cycles_for_resync)} started at: {now.strftime('%Y-%m-%d %H:%M:%S')} ---")
                sync_use_case.execute()
                print(f"--- Cycle finished. Next check in {sleep_time_seconds} seconds. ---")
            else:
                print(f"Quiet hours. Skipping synchronization. Current time: {now.strftime('%H:%M:%S')}")

            if not running:
                break

            cycle_count += 1
            sleep(sleep_time_seconds)


    def add_or_remove_student():
        global running
        try:
            while True:
                input('\nPress Enter to manage students (or Ctrl+C to exit CLI)...\n')

                option = input('Register [1] or Delete [2] a Student? (0 to quit program): ')
                if option == '1':
                    print('----- Register Student -----')
                    phone = input('Phone: ')
                    faculty_registration = input('Login Registration: ')
                    password = input('Password: ')

                    print(f"\nPhone: {phone}\nRegistration: {faculty_registration}")
                    resp = input('Confirm data? (Y/n): ')
                    if resp.lower() != 'n':
                        result = register_student_use_case.new_student(phone, faculty_registration, password)
                        if isinstance(result, Student):
                            print('Student registered successfully! Triggering data resynchronization...')
                            perform_full_sync()  # Resync cache
                        else:
                            print(f'Error during registration: {result}')
                    else:
                        print('Operation canceled.')

                elif option == '2':
                    print('----- Delete Student -----')
                    faculty_registration = input('Login Registration of student to delete: ')

                    print(f"\nRegistration: {faculty_registration}")
                    resp = input('Are you sure you want to delete this student? (y/N): ')
                    if resp.lower() == 'y':
                        was_deleted = register_student_use_case.del_student(faculty_registration)
                        if was_deleted:
                            print('Student deleted. Triggering data resynchronization...')
                            perform_full_sync()  # Resync cache
                        else:
                            print('Could not delete student (maybe not found or an error occurred).')
                    else:
                        print('Operation canceled.')

                elif option == '0':
                    print('Finishing program...')
                    running = False
                    break
                else:
                    print('Invalid option.')

        except (TypeError, ValueError, KeyboardInterrupt):
            print(f"\nInput error or interruption. Shutting down...")
            running = False


    # Start the student management thread in daemon mode
    threading.Thread(target=add_or_remove_student, daemon=True).start()

    # Start the main crawler loop in the main thread
    print("Starting crawler. Press Enter to manage students.")
    crawler_faculty()

    print("Program has been terminated.")
