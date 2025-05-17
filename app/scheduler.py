# app/scheduler.py

from apscheduler.schedulers.background import BackgroundScheduler
from app.services.xml_to_faiss import fetch_and_index_all_products
import logging

logging.basicConfig()
logging.getLogger('apscheduler').setLevel(logging.DEBUG)

scheduler = BackgroundScheduler()

def start():
    # Run every day at 3 AM (you can change the time)
    scheduler.add_job(fetch_and_index_all_products, 'cron', hour=3, minute=0)
    scheduler.start()
    print("Scheduler started and job registered.")
