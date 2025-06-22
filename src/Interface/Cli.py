from src.application.use_cases.Save_Post import SavePost
from src.application.use_cases.Save_Student import SaveStudent
from src.domain.models.Student import Student

if __name__ == "__main__":
    from time import sleep
    import threading

    use_case = SavePost()
    register_student = SaveStudent()
