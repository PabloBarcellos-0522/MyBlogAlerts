import threading
from datetime import datetime
from time import sleep
from typing import Dict, Any

import uvicorn
from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel

# --- Layer Imports ---
from src.application.services.InMemory_Store import InMemoryStore
from src.application.services.Send_Whatsapp_Msg import WhatsappNotificationService
from src.application.use_cases.Get_Student_Grades import GetStudentGrades
from src.application.use_cases.Save_Student import SaveStudent
from src.application.use_cases.Sync_And_Notify import SyncAndNotifyUseCase
from src.domain.models.Student import Student
from src.domain.services.Scraping_Service import ScrapingService
from src.infrastructure.database.Discipline_pg import DisciplinePgRepository
from src.infrastructure.database.Post_pg import PostPgRepository
from src.infrastructure.database.Student_Discipline_pg import StudentDisciplinePgRepository
from src.infrastructure.database.Student_pg import StudentPgRepository
from src.infrastructure.scraping.Scraping_Adapter import ScrapingAdapter
from contextlib import asynccontextmanager

# --- Global Services & State ---
in_memory_store = InMemoryStore()
dependencies: Dict[str, Any] = {}
running_thread = True


# --- Helper & Background Functions ---
def perform_full_sync_wrapper():
    """A wrapper that uses globally stored dependencies to perform a full sync."""
    if dependencies:
        print("--- Resynchronization triggered... ---")
        in_memory_store.full_sync(
            student_repo=dependencies['student_repo'],
            discipline_repo=dependencies['discipline_repo'],
            post_repo=dependencies['post_repo'],
            student_discipline_repo=dependencies['student_discipline_repo']
        )


def crawler_loop():
    """Main background loop for automatic synchronization."""
    global running_thread
    while 'sync_use_case' not in dependencies:
        sleep(1)

    sync_use_case: SyncAndNotifyUseCase = dependencies['sync_use_case']
    sleep_time_seconds = 120
    sync_interval_minutes = 60
    cycles_for_resync = (sync_interval_minutes * 60) / sleep_time_seconds
    cycle_count = 1

    while running_thread:
        now = datetime.now()
        if cycle_count > cycles_for_resync:
            print(f"\n--- Scheduled Full Sync Triggered at: {now.strftime('%Y-%m-%d %H:%M:%S')} ---")
            sync_use_case.reset_recovery_state()
            try:
                perform_full_sync_wrapper()
            except Exception as e:
                print(f"!!! Scheduled sync failed: {e}. !!!")
            cycle_count = 1

        if not (23 <= now.hour or now.hour < 5):  # Quiet hours
            print(
                f"\n--- Cycle {cycle_count}/{int(cycles_for_resync)} started at: {now.strftime('%Y-%m-%d %H:%M:%S')} ---")
            try:
                sync_use_case.execute()
                print(f"--- Cycle finished successfully. Next check in {sleep_time_seconds} seconds. ---")
            except Exception:
                print(f"--- Cycle failed. See logs above. Next check in {sleep_time_seconds} seconds. ---")
            cycle_count += 1
        else:
            print(f"Quiet hours. Skipping synchronization. Current time: {now.strftime('%Y-%m-%d %H:%M:%S')}")

        sleep(sleep_time_seconds)


# --- FastAPI Lifespan Manager ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles application startup and shutdown events.
    """
    global dependencies, running_thread
    print("API Startup: Setting up dependencies...")

    dependencies['student_repo'] = StudentPgRepository(in_memory_store)
    dependencies['discipline_repo'] = DisciplinePgRepository()
    dependencies['student_discipline_repo'] = StudentDisciplinePgRepository()
    dependencies['post_repo'] = PostPgRepository()
    dependencies['scraping_service'] = ScrapingAdapter()
    dependencies['notification_service'] = WhatsappNotificationService()

    dependencies['sync_use_case'] = SyncAndNotifyUseCase(
        store=in_memory_store,
        discipline_repo=dependencies['discipline_repo'],
        student_discipline_repo=dependencies['student_discipline_repo'],
        post_repo=dependencies['post_repo'],
        scraping_service=dependencies['scraping_service'],
        notification_service=dependencies['notification_service'],
        sync_callback=perform_full_sync_wrapper
    )
    dependencies['save_student_use_case'] = SaveStudent(
        student_repo=dependencies['student_repo'],
        student_discipline_repo=dependencies['student_discipline_repo'],
        scraping_service=dependencies['scraping_service']
    )
    dependencies['get_grades_use_case'] = GetStudentGrades(
        scraping_service=dependencies['scraping_service'],
        student_repository=dependencies['student_repo']
    )

    print("API Startup: Performing initial data synchronization...")
    perform_full_sync_wrapper()

    print("API Startup: Starting background crawler thread.")
    running_thread = True
    threading.Thread(target=crawler_loop, daemon=True).start()

    yield

    print("API Shutdown: Stopping background thread.")
    running_thread = False


# --- FastAPI App Initialization ---
app = FastAPI(
    title="MyBlogAlerts API",
    description="API para gerenciar scraping, notificações e alunos.",
    version="2.0.0",
    lifespan=lifespan
)


# --- API Endpoints ---
class StudentCreate(BaseModel):
    phone: str
    faculty_registration: str
    password: str


@app.get("/health", summary="Health check endpoint")
def health_check():
    return {"status": "ok"}


@app.get("/notas", summary="Busca as notas de um aluno via WhatsApp")
def get_grades_endpoint(
        sender_phone: str = Query(..., alias="from"),
):
    uc: GetStudentGrades = dependencies['get_grades_use_case']
    response_message = uc.execute(sender_phone)
    return {"data": response_message}


@app.post("/students", summary="Registra um novo aluno")
def create_student(student_data: StudentCreate):
    uc: SaveStudent = dependencies['save_student_use_case']
    scraping: ScrapingService = dependencies['scraping_service']
    try:
        name = scraping.get_student_name(student_data.faculty_registration, student_data.password)
        if not name:
            raise HTTPException(status_code=401, detail="Login failed. Check registration and password.")

        result = uc.new_student(name, student_data.phone, student_data.faculty_registration, student_data.password)
        if isinstance(result, Student):
            perform_full_sync_wrapper()  # Resync cache
            return {"status": "success", "detail": f"Student '{result.name}' registered.",
                    "student_id": result.id_student}
        else:
            raise HTTPException(status_code=400, detail=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/students/{registration}", summary="Remove um aluno")
def delete_student(registration: str):
    uc: SaveStudent = dependencies['save_student_use_case']
    was_deleted = uc.del_student(registration)
    if was_deleted:
        perform_full_sync_wrapper()  # Resync cache
        return {"status": "success", "detail": f"Student with registration {registration} deleted."}
    else:
        raise HTTPException(status_code=404,
                            detail=f"Student with registration {registration} not found or could not be deleted.")


# --- Main entry point for uvicorn ---
if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
