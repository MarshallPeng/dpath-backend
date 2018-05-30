from service.FirebaseService import FirebaseService
import random

firebaseService = FirebaseService()
courses = firebaseService.get_all_courses()

def create_cs_user(user):
    for course in courses:
        if "COSC" in course:
            rating = random.randint(4,5)

        elif "BIO" in course or "ENGS" in course:
            rating = random.randint(3,5)

        elif "ECON" in course:
            rating = random.randint(2,4)
        else:
            rating = random.randint(1,2)

        firebaseService.set_rating(user, course, rating)

def create_humanities_user(user):
    for course in courses:
        if "HIST" in course or "GOVT" in course:
            rating = random.randint(4,5)
        elif "ECON" in course:
            rating = random.randint(3,5)
        else:
            rating = random.randint(1,3)

        firebaseService.set_rating(user, course, rating)


if __name__ == '__main__':
    for i in range(1,6):
        create_humanities_user("user_humanities" + str(i))

