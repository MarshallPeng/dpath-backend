import numpy as np
import scipy.io
from scipy.optimize import minimize
import collaborativeFiltering


class RecommendationService:
    """
    Service that handles the collaborative filtering algorithm and recommendations
    """

    def __init__(self, Y, firebaseService):
        self.firebaseService = firebaseService
        self.Y = Y
        R = np.zeros(Y.shape)
        R[Y != 0] = 1  # determines if course has been rated by user

        # set stats
        self.num_users = Y.shape[1]
        self.num_courses = Y.shape[0]
        self.num_features = 3

        #  Normalize Ratings
        [self.Ynorm, self.Ymean] = collaborativeFiltering.normalize_ratings(Y, R)
        self.Ymean = np.nan_to_num(self.Ymean)

        self.X = np.random.rand(self.num_courses, self.num_features)
        self.Theta = np.random.rand(self.num_users, self.num_features)

        self.predictions_matrix = None

    def train(self):
        """
        trains model and creates prediction matrix.
        :return:
        """
        params = np.concatenate(
            (self.X.reshape(self.X.size, order='F'), self.Theta.reshape(self.Theta.size, order='F')))

        options = {
            'disp': True,
            'maxiter': 100
        }
        lambda_var = 1.5

        # reworded for scipy minimize function
        def cost(params):
            R = np.zeros(self.Y.shape)
            R[self.Y != 0] = 1
            num_users = self.Y.shape[1]
            num_courses = self.Y.shape[0]
            num_features = 3

            return collaborativeFiltering.cost_function(params, self.Y, R, num_users, num_courses, num_features,
                                                        lambda_var)

        # minimize
        result = minimize(cost, x0=params, options=options, method="L-BFGS-B", jac=True)
        theta = result["x"]

        # get X and Theta from minimization results
        self.X = np.reshape(theta[:self.num_courses * self.num_features], (self.num_courses, self.num_features),
                            order='F')
        self.Theta = np.reshape(theta[self.num_courses * self.num_features:], (self.num_users, self.num_features),
                                order='F')

        # create prediction matrix
        self.predictions_matrix = np.dot(self.X, self.Theta.T)
        print self.predictions_matrix

    def get_all_recommendations(self, users, index_to_course):
        """
        creates a dictionary of recommended courses for each user.
        :param users:
        :param index_to_course:
        :return:
        """
        recommendations_dict = {}
        for i in range(len(users)):

            # mean normalization and sort results
            user_predictions = self.predictions_matrix[:, i] + self.Ymean.flatten()
            sorted_predictions = user_predictions.argsort()[::-1]

            recommendations_dict[users[i]] = {}
            index = 0
            user_ratings = self.firebaseService.get_user_course_ratings(users[i])
            for j in range(self.num_courses):
                if user_ratings[index_to_course[sorted_predictions[j]]] == 0:
                    recommendations_dict[users[i]][index] = index_to_course[sorted_predictions[j]]
                    index += 1
        return recommendations_dict
