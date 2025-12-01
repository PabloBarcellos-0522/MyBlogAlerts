from datetime import datetime
import threading
from time import sleep
from typing import Tuple, Callable

# --- Dependency Imports ---
from src.application.services.InMemory_Store import InMemoryStore
from src.application.use_cases.Sync_And_Notify import SyncAndNotifyUseCase
from src.application.services.Send_Whatsapp_Msg import WhatsappNotificationService
from src.application.use_cases.Save_Student import SaveStudent
from src.domain.models.Student import Student
from src.infrastructure.database.Student_pg import StudentPgRepository
from src.infrastructure.database.Discipline_pg import DisciplinePgRepository
from src.infrastructure.database.Student_Discipline_pg import StudentDisciplinePgRepository
from src.infrastructure.database.Post_pg import PostPgRepository
from src.infrastructure.scraping.Scraping_Adapter import ScrapingAdapter


def setup_dependencies() -> Tuple[SyncAndNotifyUseCase, SaveStudent, Callable[[], None]]:
    """Instantiates and wires up all the dependencies, including the recovery callback."""
    print("Setting up dependencies...")
    # 1. Instantiate repositories and the store
    repos = {
        'student': StudentPgRepository(),
        'discipline': DisciplinePgRepository(),
        'student_discipline': StudentDisciplinePgRepository(),
        'post': PostPgRepository()
    }
    store = InMemoryStore()

    # 2. Define the sync function which needs access to repos and store
    def perform_full_sync_wrapper():
        """A wrapper that captures store and repos to perform a full sync."""
        store.full_sync(
            student_repo=repos['student'],
            discipline_repo=repos['discipline'],
            post_repo=repos['post'],
            student_discipline_repo=repos['student_discipline']
        )

    # 3. Instantiate services
    scraping_service = ScrapingAdapter()
    notification_service = WhatsappNotificationService()

    # 4. Instantiate the main use case, injecting the sync callback
    sync_use_case = SyncAndNotifyUseCase(
        store=store,
        discipline_repo=repos['discipline'],
        student_discipline_repo=repos['student_discipline'],
        post_repo=repos['post'],
        scraping_service=scraping_service,
        notification_service=notification_service,
        sync_callback=perform_full_sync_wrapper  # Dependency Injection
    )

    # 5. Instantiate the student management use case
    student_use_case = SaveStudent(
        student_repo=repos['student'],
        student_discipline_repo=repos['student_discipline'],
        scraping_service=scraping_service
    )
    
    # 6. Return all necessary components for the main script
    return sync_use_case, student_use_case, perform_full_sync_wrapper


if __name__ == "__main__":
    # --- Dependency Injection ---
    sync_use_case, register_student_use_case, perform_full_sync = setup_dependencies()
    
    global running
    running = True

    def crawler_faculty():
        global running
        # Configuration
        sleep_time_seconds = 120
        sync_interval_minutes = 60
        cycles_for_resync = (sync_interval_minutes * 60) / sleep_time_seconds

        # Initial full sync before starting the loop
        try:
            print("--- Performing initial data synchronization... ---")
            perform_full_sync()
            print("--- Initial sync successful. ---")
        except Exception as e:
            print(f"!!! Initial full sync failed: {e}. The application might be in a degraded state. !!!")
        
        cycle_count = 1
        while running:
            now = datetime.now()
            # Resync periodically and reset the recovery state
            if cycle_count > cycles_for_resync:
                print(f"\n--- Scheduled Sync Triggered at: {now.strftime('%Y-%m-%d %H:%M:%S')} ---")
                # Reset the recovery state before attempting a full sync
                sync_use_case.reset_recovery_state()
                try:
                    perform_full_sync()
                except Exception as e:
                    print(f"!!! Scheduled sync failed: {e}. !!!")
                cycle_count = 1  # Reset counter

            # Run sync logic only outside of "quiet hours" (e.g., 23:00 to 05:00)
            if not (23 <= now.hour or now.hour < 5):
                print(f"\n--- Cycle {cycle_count}/{int(cycles_for_resync)} started at: {now.strftime('%Y-%m-%d %H:%M:%S')} ---")
                try:
                    sync_use_case.execute()
                    print(f"--- Cycle finished successfully. Next check in {sleep_time_seconds} seconds. ---")
                except Exception:
                    # The use case already logs the details of the error and recovery attempt.
                    # We just log that the cycle failed and continue the loop.
                    print(f"--- Cycle failed. See logs above for details. Next check in {sleep_time_seconds} seconds. ---")
                cycle_count += 1
            else:
                print(f"Quiet hours. Skipping synchronization. Current time: {now.strftime('%H:%M:%S')}")

            if not running:
                break

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
                        name = ScrapingAdapter().get_student_name(faculty_registration, password)
                        result = register_student_use_case.new_student(name, phone, faculty_registration, password)
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
