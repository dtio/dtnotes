from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime, timedelta, date
from sqlalchemy import exc, and_
from sqlalchemy.orm import aliased, contains_eager 
from .models import db, Shift, User, Group, Inventory, ShiftInventory
import os
from .acknowledgements import acknowledge_bp 
from .checkout import checkout_bp

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://p3checkuser:p3checkpass@p3cldb.p3cl.svc.cluster.local/p3checklist')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'a_default_secret_key_for_dev_only') # Added for flash messages
db.init_app(app)  # Initialize the database with the app
app.register_blueprint(acknowledge_bp) 
app.register_blueprint(checkout_bp)

def add_todays_data():
    """
    Adds today's AM and PM shifts to the database if they don't already exist.
    """
    today = date.today()
    try:
        # Check if today's AM shift exists
        am_shift = Shift.query.filter_by(date=today, shift='AM').first()
        if not am_shift:
            new_am_shift = Shift(date=today, shift='AM')
            db.session.add(new_am_shift)
            app.logger.info("Added AM shift for today: %s", today)

        # Check if today's ND shift exists
        nd_shift = Shift.query.filter_by(date=today, shift='ND').first()
        if not nd_shift:
            new_nd_shift = Shift(date=today, shift='ND')
            db.session.add(new_nd_shift)
            app.logger.info("Added ND shift for today: %s", today)

        db.session.commit()  # Commit the session

    except exc.IntegrityError:
        db.session.rollback()
        app.logger.info("Attempted to add today's data, but it already exists for date: %s", today)


@app.route('/')
def p3_checklist():
    add_todays_data()  # Call the function to add today's data
    today = datetime.now()
    ten_days_ago = today - timedelta(days=10)

    data = Shift.query.filter(Shift.date >= ten_days_ago).order_by(
        Shift.date.desc(), Shift.shift.desc()).all()
    return render_template('index.html', data=data)


