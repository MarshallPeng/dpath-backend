from service.FirebaseService import FirebaseService
from service.RecommendationService import RecommendationService


class DPathController:
    """
    Controller for API endpoints
    Separates endpoints from business logic.
    """

    def __init__(self):
        # reverse order dictionary
        self.firebaseService = FirebaseService()
        self.index_to_course = {v: k for k, v in self.firebaseService.get_course_order().iteritems()}

        # initialize every user's ratings
        for user in self.firebaseService.get_all_users():
            self.firebaseService.initialize_user_ratings(user)

        # create recommendation service
        self.recommendationService = RecommendationService(self.firebaseService.get_all_ratings()[0], self.firebaseService)

    def get_recommendations(self):
        """
        Generates recommendations for all users and updates firebase
        :return:
        """
        (Y, users) = self.firebaseService.get_all_ratings()
        self.recommendationService.train()
        recommendations = self.recommendationService.get_all_recommendations(users, self.index_to_course)
        for user in recommendations:
            self.firebaseService.set_recommendation_list(recommendations[user], user)

