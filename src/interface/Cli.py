from src.application.use_cases.Save_Post import SavePost
from src.application.use_cases.Save_Student import SaveStudent
from src.domain.models.Student import Student
from datetime import datetime

if __name__ == "__main__":
    from time import sleep
    import threading

    use_case = SavePost()
    register_student = SaveStudent()
    global running
    running = True

    def crawler_faculty():
        global running
        use_case.update_all_memory()
        sleep(10)
        stick = 0

        while running:
            if not (23 <= datetime.now().hour or datetime.now().hour < 5):
                print("\t=== Time: " + str(datetime.now()) + " ===")
                use_case.search_scraping_disciplines()
                use_case.search_scraping_posts()
                print("Finished stick " + str(stick) + "\n")

                if not running:
                    break
                stick += 1
                if stick >= 60:
                    stick = 0
                    use_case.update_all_memory()

                sleep(90)


    def add_or_remove_student():
        global running
        try:
            while True:
                input('\nPress any key\n')

                option = input('Register or Delete Students?:  1|2 ? \n(0 to quit) ')
                if option == '1':
                    print('-----Register-----\n')
                    phone = input('Phone: ')
                    faculty_registration = input('Login Registration: ')
                    password = input('Password: ')

                    print(phone, faculty_registration, password)
                    print('Correct Data? ')
                    resp = input('S | N: ')
                    if resp != 'n' or resp != 'N':
                        stu = register_student.new_student(phone, faculty_registration, password)
                        if type(stu) == Student:
                            sleep(3)
                            use_case.update_students()
                        else:
                            print('error: \n' + str(stu))
                    else:
                        print('Canceled Operation!')

                elif option == '2':
                    print('-----Delete-----\n')
                    faculty_registration = input('Login Registration: ')

                    print(faculty_registration)
                    print('Correct Data? ')
                    resp = input('S | N: ')
                    if resp == 's' or resp == 'S':
                        register_student.del_student(faculty_registration)
                        sleep(3)
                        use_case.update_students()
                    else:
                        print('Canceled Operation!')

                elif option == '0':
                    running = False
                    print('Finishing Program...')
                    break
                else:
                    print('Invalid Operation!')

        except (TypeError, ValueError) as e:
            print(f"Erro inesperado: {e}")

    threading.Thread(target=add_or_remove_student, daemon=True).start()
    crawler_faculty()
