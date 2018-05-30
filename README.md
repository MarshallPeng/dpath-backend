# dpath-backend

scripts that handle the  machine learning / collaborative filtering aspects of dpath. Originally was supposed to be hosted on google app engine. But turns out google app engine does not allow the scipy library. Therefore, the flask API has been removed and now, to update the course recommendations, the scripts in the scripts folder are run on a cronjob.

