from flask import Flask, request, jsonify
import logging

from controller.DPathController import DPathController
from service.FirebaseService import FirebaseService

app = Flask(__name__)

# To be run on a cron job
@app.route('/rec_update')
def update():
    controller = DPathController()
    controller.get_recommendations()









