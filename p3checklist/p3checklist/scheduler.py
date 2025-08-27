from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, date
import atexit
from .models import db, Shift
from sqlalchemy import exc

def add_todays_data():
    """
    Adds today's AM and ND shifts to the database if they don't already exist.
    """
    today = date.today()
    try:
        # Check if today's AM shift exists
        am_shift = Shift.query.filter_by(date=today, shift='AM').first()
        if not am_shift:
            new_am_shift = Shift(date=today, shift='AM')
            db.session.add(new_am_shift)
            print(f"Added AM shift for today: {today}")

        # Check if today's ND shift exists
        nd_shift = Shift.query.filter_by(date=today, shift='ND').first()
        if not nd_shift:
            new_nd_shift = Shift(date=today, shift='ND')
            db.session.add(new_nd_shift)
            print(f"Added ND shift for today: {today}")

        db.session.commit()

    except exc.IntegrityError:
        db.session.rollback()
        print(f"Attempted to add today's data, but it already exists for date: {today}")

def init_scheduler(app):
    """Initialize the background scheduler for daily tasks."""
    scheduler = BackgroundScheduler()
    
    # Run at 12:01 AM every day
    scheduler.add_job(
        func=add_todays_data,
        trigger="cron",
        hour=0,
        minute=1,
        id='daily_shift_creation'
    )
    
    # Run once at startup
    with app.app_context():
        add_todays_data()
    
    scheduler.start()
    
    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())
    
    return scheduler
