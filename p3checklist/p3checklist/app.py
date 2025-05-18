from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime, timedelta, date
from sqlalchemy import exc, and_
from sqlalchemy.orm import aliased, contains_eager # Added contains_eager
from .models import db, Shift, User, Group, Inventory, ShiftInventory
import os


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://p3checkuser:p3checkpass@p3cldb.p3cl.svc.cluster.local/p3checklist')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'a_default_secret_key_for_dev_only') # Added for flash messages
db.init_app(app)  # Initialize the database with the app


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


@app.route('/acknowledge_fixed')
def acknowledge_fixed():
    date_str = request.args.get('date')
    shift_str = request.args.get('shift') # Renamed for clarity

    inventory_group_with_quantities = []

    if date_str and shift_str:
        try:
            ack_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            current_shift_obj = Shift.query.filter_by(date=ack_date, shift=shift_str).first()

            # Proceed if the specific shift is found
            if current_shift_obj:
                fixed_inventory_alias = aliased(Inventory)
                inventory_group_query = Group.query.outerjoin(
                    fixed_inventory_alias,
                    and_(Group.id == fixed_inventory_alias.groupid, fixed_inventory_alias.fixed == True)
                ).options(
                    contains_eager(Group.inventories, alias=fixed_inventory_alias) # Populates group.inventories with only fixed items
                ).order_by(Group.id)
                inventory_group_result = inventory_group_query.all()
                for group in inventory_group_result:
                    if group.inventories:
                        group.inventories = ShiftInventory.get_inventory_with_quantities(current_shift_obj.id, group.inventories)
                inventory_group_with_quantities = inventory_group_result
            else:
                flash(f"Shift details not found for {date_str} - {shift_str}.", "warning")
        except ValueError:
            flash("Invalid date format provided.", "error")
    else:
        flash("Date and Shift are required to view fixed item acknowledgements.", "warning")
        return redirect(url_for('p3_checklist')) # Redirect if essential params are missing

    return render_template('acknowledge_fixed.html', date=date_str, shift=shift_str, inventory_group=inventory_group_with_quantities)


@app.route('/acknowledge_ent', methods=['POST']) # Changed to allow GET for consistency if needed
def acknowledge_ent():

    date_str = request.form.get('date')
    shift_str = request.form.get('shift')

    ent_inventory_with_quantities = []

    if date_str and shift_str:
        try:
            ack_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            current_shift_obj = Shift.query.filter_by(date=ack_date, shift=shift_str).first()

            if current_shift_obj:
                ent_items_query = Inventory.query.filter_by(fixed=False, groupid=2).order_by(Inventory.id).all()
                ent_inventory_with_quantities = ShiftInventory.get_inventory_with_quantities(current_shift_obj.id, ent_items_query)
            else:
                flash(f"Shift details not found for {date_str} - {shift_str}.", "warning")
        except ValueError:
            flash("Invalid date format provided.", "error")
    else:
        flash("Date and Shift are required to view ENT item acknowledgements.", "warning")
        return redirect(url_for('p3_checklist'))

    return render_template('acknowledge_ent.html', date=date_str, shift=shift_str, 
                           users=users, ent_inventory=ent_inventory_with_quantities)

@app.route('/acknowledge_dental', methods=['POST']) # Changed to allow GET for consistency
def acknowledge_dental():

    date_str = request.form.get('date')
    shift_str = request.form.get('shift')

    users = User.query.order_by(User.username).all()
    dental_inventory_with_quantities = []

    if date_str and shift_str:
        try:
            ack_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            current_shift_obj = Shift.query.filter_by(date=ack_date, shift=shift_str).first()

            if current_shift_obj:
                dental_items_query = Inventory.query.filter_by(fixed=False, groupid=3).order_by(Inventory.id).all()
                dental_inventory_with_quantities = ShiftInventory.get_inventory_with_quantities(current_shift_obj.id, dental_items_query)
            else:
                flash(f"Shift details not found for {date_str} - {shift_str}.", "warning")
        except ValueError:
            flash("Invalid date format provided.", "error")
    else:
        flash("Date and Shift are required to view Dental item acknowledgements.", "warning")
        return redirect(url_for('p3_checklist'))

    return render_template('acknowledge_dental.html', date=date_str, shift=shift_str, 
                           users=users, dental_inventory=dental_inventory_with_quantities)

@app.route('/submit_acknowledgement', methods=['POST'])
def submit_acknowledgement():
    date_str = request.form['date']
    shift_str = request.form['shift'] # Renamed for clarity
    username = request.form['name']  # Assuming 'name' from form is the username

    try:
        ack_date = datetime.strptime(date_str, '%Y-%m-%d').date()

        # Find or create the user
        user = User.query.filter_by(username=username).first()
        if not user:
            user = User(username=username)
            db.session.add(user)
            # We need the user's ID, so flush to get it assigned by the DB
            # Or commit here if you prefer, but flushing is often done before a larger commit.
            db.session.flush() 
            app.logger.info(f"New user '{username}' created with ID {user.id}.")
        
        # Find the shift record
        shift_to_acknowledge = Shift.query.filter_by(date=ack_date, shift=shift_str).first()

        if shift_to_acknowledge:
            shift_to_acknowledge.acknowledged = True
            shift_to_acknowledge.acknowledged_by = user.id # Assign user's ID
            db.session.add(shift_to_acknowledge)
            db.session.commit()
            flash(f"Shift on {date_str} ({shift_str}) acknowledged successfully by {username}.", "success")
            app.logger.info(f"Shift {shift_str} on {ack_date} acknowledged by user {username} (ID: {user.id}).")
        else:
            flash(f"Could not find the shift for {date_str} ({shift_str}) to acknowledge.", "error")
            app.logger.warning(f"Attempt to acknowledge non-existent shift: {date_str} - {shift_str} by user {username}.")

    except ValueError:
        flash("Invalid date format provided for acknowledgement.", "error")
        app.logger.error(f"Invalid date format '{date_str}' received in submit_acknowledgement.")
    except Exception as e:
        db.session.rollback() # Rollback in case of error before commit
        flash("An error occurred during the acknowledgement process. Please try again.", "error")
        app.logger.error(f"Error during submit_acknowledgement by {username} for {date_str}-{shift_str}: {e}", exc_info=True)

    return redirect(url_for('p3_checklist'))  # Redirect back to the main page
    
    
@app.route('/acknowledge_view')
def acknowledge_view():
    date_str = request.args.get('date')
    shift_str = request.args.get('shift')
    inventory_group_with_quantities = []
    acknowledger_name = "N/A" # Default value

    if date_str and shift_str:
        try:
            ack_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            current_shift_obj = Shift.query.filter_by(date=ack_date, shift=shift_str).first()

            if current_shift_obj:
                # Fetch the name of the user who acknowledged the shift
                if current_shift_obj.acknowledged_by:
                    user = User.query.get(current_shift_obj.acknowledged_by)
                    if user:
                        acknowledger_name = user.username
                fixed_inventory = aliased(Inventory)
                inventory_group_query = Group.query.outerjoin(
                    fixed_inventory,
                    and_(Group.id == fixed_inventory.groupid)
                ).options(
                    contains_eager(Group.inventories, alias=fixed_inventory) 
                ).order_by(Group.id, fixed_inventory.id)
                inventory_group_result = inventory_group_query.all()
                for group in inventory_group_result:
                    if group.inventories:
                        group.inventories = ShiftInventory.get_inventory_with_quantities(current_shift_obj.id, group.inventories)
                inventory_group_with_quantities = inventory_group_result
            else:
                flash(f"Shift details not found for {date_str} - {shift_str}.", "warning")
        except ValueError:
            flash("Invalid date format provided.", "error")
    else:
        flash("Date and Shift are required to view fixed item acknowledgements.", "warning")
        return redirect(url_for('p3_checklist')) # Redirect if essential params are missing

    return render_template('acknowledge_view.html', date=date_str, shift=shift_str, 
                           inventory_group=inventory_group_with_quantities, 
                           acknowledger_name=acknowledger_name)
