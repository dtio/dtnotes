from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime, timedelta, date
from sqlalchemy import exc
from models import db, MainData  # Import db and MainData
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://p3checkuser:p3checkpass@localhost/p3checklist')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)  # Initialize the database with the app


def add_todays_data():
    """
    Adds today's AM and PM shifts to the database if they don't already exist.
    """
    today = date.today()
    try:
        # Check if today's AM shift exists
        am_shift = MainData.query.filter_by(date=today, shift='AM').first()
        if not am_shift:
            new_am_shift = MainData(date=today, shift='AM')
            db.session.add(new_am_shift)
            print("Added AM shift for today")

        # Check if today's PM shift exists
        nd_shift = MainData.query.filter_by(date=today, shift='ND').first()
        if not nd_shift:
            new_nd_shift = MainData(date=today, shift='ND')
            db.session.add(new_nd_shift)
            print("Added ND shift for today")

        db.session.commit()  # Commit the session

    except exc.IntegrityError:
        db.session.rollback()
        print("Today's data already exists.")  # added print


@app.route('/')
def p3_checklist():
    add_todays_data()  # Call the function to add today's data
    today = datetime.now()
    ten_days_ago = today - timedelta(days=10)

    data = MainData.query.filter(MainData.date >= ten_days_ago).order_by(
        MainData.date.desc(), MainData.shift.desc()).all()
    return render_template('index.html', data=data)


@app.route('/acknowledge')
def acknowledge():
    date_str = request.args.get('date')
    shift = request.args.get('shift')
    return render_template('acknowledge.html', date=date_str, shift=shift)

@app.route('/submit_acknowledgement', methods=['POST'])
def submit_acknowledgement():
    date_str = request.form['date']
    shift = request.form['shift']
    name = request.form['name']  # Get the name from the form

    try:
        shift_data = MainData.query.filter_by(date=datetime.strptime(date_str, '%Y-%m-%d'), shift=shift).first()
        if shift_data:
            shift_data.acknowledged = True
            shift_data.acknowledged_by = name # store the name
            db.session.commit()
            print(f"Acknowledgement for {shift} shift on {date_str} updated.")
        else:
            print(f"Shift data not found for {shift} shift on {date_str}.")
    except Exception as e:
        db.session.rollback()
        print(f"Error updating acknowledgement: {e}")

    return redirect(url_for('p3_checklist'))  # Redirect back to the main page

if __name__ == '__main__':
    with app.app_context():  # push an application context
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)