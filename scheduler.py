from apscheduler.schedulers.background import BackgroundScheduler
import atexit
from tasks import notification_job


def init_scheduler(app):
    if not hasattr(app, 'scheduler_initialized'):
        scheduler = BackgroundScheduler()
        scheduler.add_job(func=notification_job, trigger="interval", minutes=1)
        #scheduler.add_job(func=notification_job, trigger="interval", hours=1)
        scheduler.start()

        # Shut down the scheduler when exiting the app
        atexit.register(lambda: scheduler.shutdown())

        app.scheduler = scheduler
        app.scheduler_initialized = True