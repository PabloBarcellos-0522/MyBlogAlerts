from src.application.use_cases.Save_Post import SavePost
from src.application.use_cases.Save_Student import SaveStudent
from src.domain.models.Student import Student

if __name__ == "__main__":
    from time import sleep
    import threading

    use_case = SavePost()
    register_student = SaveStudent()

    def crawler_faculty():
        use_case.update_all_memory()
        sleep(10)
        stick = 10

        while True:
            use_case.search_scraping_disciplines()
            sleep(3)
            use_case.search_scraping_posts()
            sleep(3)

            stick += 1
            if stick >= 60:
                stick = 0
                use_case.update_all_memory()

            sleep(60)

    threading.Thread(target=crawler_faculty, daemon=True).start()

