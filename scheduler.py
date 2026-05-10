import os
import time as time_module
import threading
import schedule
from datetime import datetime
import pytz
from dotenv import load_dotenv
from supabase import create_client

load_dotenv(override=True)

def get_supabase():
    return create_client(
        os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_KEY")
    )

def convert_ist_to_utc(time_str: str) -> str:
    """Convert HH:MM IST to HH:MM UTC for the schedule library"""
    ist = pytz.timezone("Asia/Kolkata")
    utc = pytz.utc

    # Build a datetime with today's date and the given IST time
    hour, minute = map(int, time_str.split(":"))
    now_ist = datetime.now(ist).replace(hour=hour, minute=minute, second=0, microsecond=0)

    # Convert to UTC
    now_utc = now_ist.astimezone(utc)
    return now_utc.strftime("%H:%M")

def load_jobs(recipient_email: str = None) -> list:
    try:
        db = get_supabase()
        query = db.table("scheduled_jobs").select("*")

        if recipient_email:
            query = query.eq("recipient", recipient_email.strip().lower())
        
        result = query.execute()
        return result.data or []
    except Exception as e:
        print(f"Error loading jobs: {e}")
        return []

def save_job(job: dict) -> dict:
    try:
        db = get_supabase()
        result = db.table("scheduled_jobs").insert({
            "companies": job["companies"],
            "recipient": job["recipient"],
            "day":       job["day"],
            "time_str":  job["time"]
        }).execute()
        return result.data[0] if result.data else {}
    except Exception as e:
        print(f"Error saving job: {e}")
        return {}

def delete_job(job_id: str):
    try:
        db = get_supabase()
        db.table("scheduled_jobs").delete().eq("id", job_id).execute()
        print(f"✅ Deleted job: {job_id}")
    except Exception as e:
        print(f"Error deleting job: {e}")

def schedule_job(companies: list, recipient: str, day: str, time_str: str):
    utc_time = convert_ist_to_utc(time_str)
    print(f"⏰ IST {time_str} → UTC {utc_time}")

    def job_fn():
        from graph import run_stratumai
        from email_sender import send_report_email
        for company in companies:
            try:
                report = run_stratumai(company)
                send_report_email(company, report, recipient)
                time_module.sleep(10)
            except Exception as e:
                print(f"Scheduler error for {company}: {e}")

    getattr(schedule.every(), day.lower()).at(utc_time).do(job_fn)
    print(f"✅ Scheduled: {companies} every {day} at {utc_time}")

def start_scheduler():
    def run():
        while True:
            schedule.run_pending()
            time_module.sleep(30)
    t = threading.Thread(target=run, daemon=True)
    t.start()

# On import: reload all persisted jobs from Supabase
for job in load_jobs():
    schedule_job(
        job["companies"],
        job["recipient"],
        job["day"],
        job["time_str"]
    )

start_scheduler()