import numpy as np
import scipy.io
from scipy.optimize import minimize


def cost_function(params, Y, R, num_users, num_movies, num_features, lambda_var):
    """
    Cost function to minimize
    :param params:
    :param Y: matrix of all ratings by all users of all courses
    :param R: matrix determining if user j has rated course i
    :param num_users:
    :param num_movies:
    :param num_features:
    :param lambda_var: regularization term
    :return:
    """
    # Unfold the U and W matrices from params
    x = np.reshape(params[:num_movies * num_features], (num_movies, num_features), order='F')
    theta = np.reshape(params[num_movies * num_features:], (num_users, num_features), order='F')

    # X * Theta performed according to low rank matrix vectorization
    squared_error = np.power(np.dot(x, theta.T) - Y, 2)

    # for cost function, sum only i,j for which R(i,j)=1
    J = (1 / 2.) * np.sum(squared_error * R)

    x_gradient = np.dot((np.dot(x, theta.T) - Y) * R, theta)
    theta_gradient = np.dot(((np.dot(x, theta.T) - Y) * R).T, x)

    # only add regularized cost to J now
    J = J + (lambda_var / 2.) * (np.sum(np.power(theta, 2)) + np.sum(np.power(x, 2)))

    # only add regularization terms
    x_gradient = x_gradient + lambda_var * x
    theta_gradient = theta_gradient + lambda_var * theta

    gradients = np.concatenate(
        (x_gradient.reshape(x_gradient.size, order='F'), theta_gradient.reshape(theta_gradient.size, order='F')))

    return J, gradients


def normalize_ratings(Y, R):
    """
    normalize each course to have an average rating of 0
    Allows for recommendations to be generated for users who haven't rated anything
    :param Y:
    :param R:
    :return:
    """
    m, n = Y.shape
    Ymean = np.zeros((m, 1))
    Ynorm = np.zeros(Y.shape)
    for i in xrange(m):
        idx = R[i, :] == 1
        Ymean[i] = np.mean(Y[i, idx])
        Ynorm[i, idx] = Y[i, idx] - Ymean[i]

    return Ynorm, Ymean


if __name__ == "__main__":

    course_names = {
        0: "COSC 1",
        1: "COSC 10",
        2: "COSC 30",
        3: "COSC 31",
        4: "COSC 50"
    }

    # load ratings table
    Y = scipy.io.loadmat('course_ratings.mat')["Y"]
    R = np.zeros(Y.shape)
    R[Y != 0] = 1  # determines if course has been rated by user

    new_user_ratings = np.zeros((5, 1))
    new_user_ratings[0] = 5   # CS 1
    new_user_ratings[1] = 0   # CS 10
    new_user_ratings[2] = 0   # CS 30
    new_user_ratings[3] = 0   # CS 31
    new_user_ratings[4] = 0   # CS 50

    # Add new user ratings to data set
    Y = np.column_stack((new_user_ratings, Y))
    R = np.column_stack(((new_user_ratings != 0).astype(int), R))

    # set stats
    num_users = Y.shape[1]
    num_courses = Y.shape[0]
    num_features = 3

    #  Normalize Ratings
    [Ynorm, Ymean] = normalize_ratings(Y, R)

    # set random initial parameters
    X = np.random.rand(num_courses, num_features)
    Theta = np.random.rand(num_users, num_features)

    params = np.concatenate((X.reshape(X.size, order='F'), Theta.reshape(Theta.size, order='F')))

    options = {
        'disp': True,
        'maxiter': 100
    }
    lambda_var = 1.5


    # reworded for minimize function
    def cost(params):
        return cost_function(params, Y, R, num_users, num_courses, num_features, lambda_var)


    # minimize
    result = minimize(cost, x0=params, options=options, method="L-BFGS-B", jac=True)
    theta = result["x"]

    # get X and Theta from minimization results
    X = np.reshape(theta[:num_courses * num_features], (num_courses, num_features), order='F')
    Theta = np.reshape(theta[num_courses * num_features:], (num_users, num_features), order='F')

    # create prediction matrix
    predictions_matrix = np.dot(X, Theta.T)
    new_user_predictions = predictions_matrix[:, 2] + Ymean.flatten()

    print Y
    print predictions_matrix

    print "Top Recommendations for New User:"

    # sort predictions
    sorted_predictions = new_user_predictions.argsort()[::-1]
    for i in xrange(3):
        print course_names[sorted_predictions[i]]
