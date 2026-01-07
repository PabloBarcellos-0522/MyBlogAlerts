import threading
from datetime import datetime, timedelta
from time import sleep
from typing import Dict, Any, Annotated
import os
from dotenv import load_dotenv
import uvicorn
from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
import random
import string

# --- Layer Imports ---
from src.application.services.InMemory_Store import InMemoryStore
from src.application.services.Send_Whatsapp_Msg import WhatsappNotificationService
from src.application.use_cases.Get_Student_Absences import GetStudentAbsences
from src.application.use_cases.Get_Student_Grades import GetStudentGrades
from src.application.use_cases.Save_Student import SaveStudent, StudentCreationError
from src.application.use_cases.Sync_And_Notify import SyncAndNotifyUseCase
from src.domain.models.Student import Student
from src.domain.services.Scraping_Service import ScrapingService
from src.infrastructure.database.Discipline_pg import DisciplinePgRepository
from src.infrastructure.database.Post_pg import PostPgRepository
from src.infrastructure.database.Student_Discipline_pg import StudentDisciplinePgRepository
from src.infrastructure.database.Student_pg import StudentPgRepository
from src.infrastructure.scraping.Scraping_Adapter import ScrapingAdapter
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends

# --- Global Services & State ---
in_memory_store = InMemoryStore()
dependencies: Dict[str, Any] = {}
running_thread = True
scraping_lock = threading.Lock()
verification_codes: Dict[str, Dict[str, str]] = {}


# --- Helper & Background Functions ---
def generate_verification_code(length=6) -> str:
    """Generates a random, unique verification code."""
    characters = string.digits
    while True:
        code = ''.join(random.choice(characters) for _ in range(length))
        if code not in verification_codes:
            return code


def cleanup_expired_codes():
    """Periodically cleans up expired verification codes."""
    global running_thread
    while running_thread:
        now = datetime.now()
        expired_codes = []
        # Use a copy of items to avoid runtime errors during iteration
        for code, info in list(verification_codes.items()):
            if now - info["timestamp"] > timedelta(minutes=5):
                expired_codes.append(code)

        for code in expired_codes:
            try:
                del verification_codes[code]
                print(f"Removed expired verification code: {code}")
            except KeyError:
                # Code might have been used and deleted by another thread
                pass
        sleep(60)  # Run every minute


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
            with scraping_lock:
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
    dependencies['get_absences_use_case'] = GetStudentAbsences(
        scraping_service=dependencies['scraping_service'],
        student_repository=dependencies['student_repo']
    )

    print("API Startup: Performing initial data synchronization...")
    perform_full_sync_wrapper()

    print("API Startup: Starting background threads.")
    running_thread = True
    threading.Thread(target=crawler_loop, daemon=True).start()
    threading.Thread(target=cleanup_expired_codes, daemon=True).start()

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

load_dotenv()
origin_link = os.getenv('REGISTER_PAGE')
print(origin_link)
origins = [
    origin_link
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


# --- API Endpoints ---
class StudentCreate(BaseModel):
    phone: str
    faculty_registration: str
    password: str


class VerificationData(BaseModel):
    code: str


class StudentDelete(BaseModel):
    password: str


auth_scheme = HTTPBearer()


@app.get("/", summary="Health check endpoint")
def health_check():
    return {"status": "ok"}


@app.get("/notas", summary="Busca as notas de um aluno via WhatsApp")
def get_grades_endpoint(
        token: Annotated[HTTPAuthorizationCredentials, Depends(auth_scheme)],
        sender_phone: str = Query(..., alias="from"),
):
    load_dotenv()
    expected_token = os.getenv('ACESS_TOKEN')

    if not expected_token:
        raise HTTPException(status_code=500, detail="Variável de ambiente ACESS_TOKEN não configurada no servidor.")

    if token.credentials != expected_token:
        raise HTTPException(status_code=401, detail="Token de acesso inválido.")

    uc: GetStudentGrades = dependencies['get_grades_use_case']
    response_message = uc.execute(sender_phone)
    return {"data": response_message}


@app.get("/faltas", summary="Busca as faltas de um aluno via WhatsApp")
def get_absences_endpoint(
        token: Annotated[HTTPAuthorizationCredentials, Depends(auth_scheme)],
        sender_phone: str = Query(..., alias="from"),
):
    load_dotenv()
    expected_token = os.getenv('ACESS_TOKEN')

    if not expected_token:
        raise HTTPException(status_code=500, detail="Variável de ambiente ACESS_TOKEN não configurada no servidor.")

    if token.credentials != expected_token:
        raise HTTPException(status_code=401, detail="Token de acesso inválido.")

    uc: GetStudentAbsences = dependencies['get_absences_use_case']
    response_message = uc.execute(sender_phone)
    return {"data": response_message}


@app.get("/registrar", summary="retorna o link da página de registro")
def get_register_url_endpoint(
        token: Annotated[HTTPAuthorizationCredentials, Depends(auth_scheme)],
        sender_phone: str = Query(..., alias="from"),
):
    load_dotenv()
    expected_token = os.getenv('ACESS_TOKEN')
    register_page_url = os.getenv('REGISTER_PAGE_URL')

    if not expected_token:
        raise HTTPException(status_code=500, detail="Variável de ambiente ACESS_TOKEN não configurada no servidor.")

    if token.credentials != expected_token:
        raise HTTPException(status_code=401, detail="Token de acesso inválido.")

    uc: StudentPgRepository = dependencies['student_repo']

    print(sender_phone)
    print(uc.get_by_phone_number(sender_phone))
    if uc.get_by_phone_number(sender_phone) is None:
        return {"data": "Olá!, Você pode se registrar no MyBlogAlerts pelo site:\n\n" + register_page_url}
    else:
        return {"data": "Usuário já registrado no MyBlogAlerts. Página de registro: \n\n" + register_page_url}


@app.post("/students", summary="Registra um novo aluno")
def create_student(
        verification_data: VerificationData,
        token: Annotated[HTTPAuthorizationCredentials, Depends(auth_scheme)]
):
    load_dotenv()
    expected_token = os.getenv('ACESS_TOKEN')

    if not expected_token:
        raise HTTPException(status_code=500, detail="Variável de ambiente ACESS_TOKEN não configurada no servidor.")

    if token.credentials != expected_token:
        raise HTTPException(status_code=401, detail="Token de acesso inválido.")

    code = verification_data.code
    if code not in verification_codes:
        raise HTTPException(status_code=400, detail="Código de verificação inválido ou expirado.")

    stored_info = verification_codes[code]
    student_data = stored_info["data"]
    timestamp = stored_info["timestamp"]

    if datetime.now() - timestamp > timedelta(minutes=5):
        del verification_codes[code]
        raise HTTPException(status_code=400, detail="Código de verificação expirado.")

    uc: SaveStudent = dependencies['save_student_use_case']

    with scraping_lock:
        try:
            result = uc.new_student(
                phone=student_data["phone"],
                faculty_registration=student_data["faculty_registration"],
                password=student_data["password"]
            )

            if isinstance(result, Student):
                del verification_codes[code]
                perform_full_sync_wrapper()
                return {"status": "success", "detail": f"Aluno '{result.name}' registrado.",
                        "student_id": result.id_student}
            else:
                status_code = 401 if "credenciais" in result or "login" in result.lower() else 409
                raise HTTPException(status_code=status_code, detail=result)

        except StudentCreationError as e:
            raise HTTPException(status_code=500, detail=str(e))
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Um erro inesperado ocorreu no servidor: {e}")


@app.post("/verification-code", summary="Faz o envio do código de verificação para validar o número")
def send_verification_code(
        student_data: StudentCreate,
        token: Annotated[HTTPAuthorizationCredentials, Depends(auth_scheme)]
):
    load_dotenv()
    expected_token = os.getenv('ACESS_TOKEN')

    if not expected_token:
        raise HTTPException(status_code=500, detail="Variável de ambiente ACESS_TOKEN não configurada no servidor.")

    if token.credentials != expected_token:
        raise HTTPException(status_code=401, detail="Token de acesso inválido.")

    student_repo: StudentPgRepository = dependencies['student_repo']
    if student_repo.get_by_phone_number(
            student_data.phone) or student_repo.find_by_registration(
            student_data.faculty_registration):
        raise HTTPException(status_code=409, detail="Este número de telefone ou matrícula já está em uso.")

    code = generate_verification_code()
    verification_codes[code] = {
        "data": {
            "phone": student_data.phone,
            "faculty_registration": student_data.faculty_registration,
            "password": student_data.password
        },
        "timestamp": datetime.now()
    }

    notification_service: WhatsappNotificationService = dependencies['notification_service']
    message = f"Seu código de verificação do MyBlogAlerts é: *{code}*"
    try:
        notification_service.student_msg(student_data.phone, message)
        return {"status": "success", "detail": "Código de verificação enviado com sucesso."}
    except Exception as e:
        del verification_codes[code]
        raise HTTPException(status_code=500, detail=f"Falha ao enviar o código de verificação: {e}")


@app.delete("/students/{registration}", summary="Remove um aluno")
def delete_student(
        registration: str,
        delete_data: StudentDelete,
        token: Annotated[HTTPAuthorizationCredentials, Depends(auth_scheme)]
):
    load_dotenv()
    expected_token = os.getenv('ACESS_TOKEN')

    if not expected_token:
        raise HTTPException(status_code=500, detail="Variável de ambiente ACESS_TOKEN não configurada no servidor.")

    if token.credentials != expected_token:
        raise HTTPException(status_code=401, detail="Token de acesso inválido.")

    uc: SaveStudent = dependencies['save_student_use_case']
    
    with scraping_lock:
        result = uc.del_student(registration, delete_data.password)

    if result is True:
        perform_full_sync_wrapper()  # Resync cache
        return {"status": "success", "detail": f"Aluno com matrícula {registration} removido."}
    elif result is False:
        raise HTTPException(status_code=404,
                            detail=f"Aluno com matrícula {registration} não encontrado.")
    else:
        raise HTTPException(status_code=401, detail=result)


# --- Main entry point for uvicorn ---
if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
