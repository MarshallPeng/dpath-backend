import firebase_admin
import numpy as np
from firebase_admin import credentials, db
from numpy import array


class FirebaseService:
    """
    Service to handle CRUD operations on firebase
    """

    def __init__(self):
        self.cred = credentials.Certificate('../dpath-98b76-bfb35cce242d.json')
        firebase_admin.initialize_app(self.cred, {
            'databaseURL': 'https://dpath-98b76.firebaseio.com'
        })
        self.ref = db.reference()


    def initialize_user_ratings(self, user):
        """
        Creates entry for user if user hasn't rated a course with rating = 0
        :param user:
        :return:
        """
        ratings = self.ref.child('Users/' + user + '/ratings').get()
        courses = self.get_all_courses()
        if ratings is None:
            ratings = {}

        for course in courses:
            if ratings is None or course not in ratings:
                ratings[course] = 0
        self.ref.child('Users/' + user + '/ratings/').set(ratings)


    def get_user_course_ratings(self, user):
        """
        Gets course ratings for a user
        :param user:
        :return:
        """
        return self.ref.child('Users/' + user + '/ratings/').get()


    def set_rating(self, user, course, rating):
        """
        set ratings for user
        :param user:
        :param course:
        :param rating:
        :return:
        """
        return self.ref.child('Users/' + user + '/ratings/' + course).set(rating)


    def get_all_ratings(self):
        """
        Takes ratings of all users and creates numpy matrix
        Also returns the order of the columns, so we know which column corresponds to which user.
        :return:
        """
        order = self.get_course_order()
        users = self.get_all_users()
        num_rows = len(self.get_all_courses())

        existing_ratings = np.zeros((num_rows,))
        for user in users:
            user_ratings = self.get_user_course_ratings(user)
            column = np.zeros((num_rows,)).T
            for course in user_ratings:
                column[order[course]] = user_ratings[course]

            existing_ratings = np.column_stack((existing_ratings, column))

        return np.delete(existing_ratings, 0, axis=1), users


    def get_all_courses(self):
        """
        returns list of all courses
        :return:
        """
        courses = self.ref.child('Courses/').get()
        return [course for course in courses]


    def get_all_users(self):
        """
        returns list of all users
        :return:
        """
        users = self.ref.child('Users/').get()
        return [user for user in users]


    def get_course_order(self):
        """
        get order or courses, used to associate row with matrix.
        :return:
        """
        all_courses_info = self.ref.child('Courses/').get()
        return {name : all_courses_info[name]['row_number'] for name in all_courses_info}


    def set_recommendation_list(self, recommendations, user):
        self.ref.child('Users/' + user + '/recommendations/').set(recommendations)


    def set_course_info(self, course_info, course_title=""):
        """
        Sets course info after being scraped from ORC used in scrape_orc.py.
        :param course_info:
        :param course_title:
        :return:
        """
        if course_title == "":
            course_title = course_info['courseNumber'].replace('.', '-')  # firebase doesn't allow '.' in key.
        self.ref.child('Courses/' + course_title).set(course_info)
