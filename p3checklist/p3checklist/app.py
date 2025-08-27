from flask import Flask, render_template, request, redirect, url_for, flash
from flask_migrate import Migrate
from datetime import datetime, timedelta, date
from sqlalchemy import exc, and_
from sqlalchemy.orm import aliased, contains_eager 
from .models import db, Shift, User, Group, Inventory, ShiftInventory
import os
from .acknowledgements import acknowledge_bp 
from .checkout import checkout_bp
from .scheduler import init_scheduler

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://p3checkuser:p3checkpass@p3cldb.p3cl.svc.cluster.local/p3checklist')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'a_default_secret_key_for_dev_only') # Added for flash messages
db.init_app(app)  # Initialize the database with the app

migrate = Migrate(app, db)

app.register_blueprint(acknowledge_bp) 
app.register_blueprint(checkout_bp)

# Initialize scheduler for background tasks
init_scheduler(app)

# add_todays_data() moved to scheduler.py

@app.route('/')
def p3_checklist():
    today = datetime.now()
    ten_days_ago = today - timedelta(days=10)

    data = Shift.query.filter(Shift.date >= ten_days_ago).order_by(
        Shift.date.desc(), Shift.shift.desc()).all()
    return render_template('index.html', data=data)


