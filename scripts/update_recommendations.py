from controller.DPathController import DPathController

from apscheduler.schedulers.blocking import BlockingScheduler

import logging

controller = DPathController()
controller.get_recommendations()

def update_recommendations():
    print "Updating Recommendations..."
    controller.get_recommendations()
    print "Recommendations Updated!"

log = logging.getLogger('apscheduler.executors.default')
log.setLevel(logging.INFO)  # DEBUG

fmt = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
h = logging.StreamHandler()
h.setFormatter(fmt)
log.addHandler(h)

scheduler = BlockingScheduler()
scheduler.add_job(update_recommendations, 'interval', minutes=1)
scheduler.start()
