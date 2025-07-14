from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from datetime import datetime, timedelta, date
from sqlalchemy import exc, and_, or_
from sqlalchemy.orm import aliased, contains_eager
from .models import db, Shift, User, Group, Inventory, ShiftInventory

acknowledge_bp = Blueprint('acknowledgements', __name__)

@acknowledge_bp.route('/acknowledge_eyeent', methods=['GET'])
def acknowledge_eyeent():
    date_str = request.args.get('date')
    shift_str = request.args.get('shift')

    ent_inventory_with_quantities = []
    inventory_differences = {}

    if date_str and shift_str:
        try:
            ack_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            current_shift_obj = Shift.query.filter_by(date=ack_date, shift=shift_str).first()

            # Find previous shift
            prev_shift_obj = get_previous_shift(ack_date, shift_str)

            if current_shift_obj:
                ent_items_query = Inventory.query.filter(or_(Inventory.groupid==1, Inventory.groupid==2)).order_by(Inventory.id).all() 
                ent_inventory_with_quantities = ShiftInventory.get_inventory_with_quantities(current_shift_obj.id, ent_items_query)

                # Get current shift inventory
                current_inventory_map = get_inventory_map(current_shift_obj)

                # Get previous shift inventory
                prev_inventory_map = get_inventory_map(prev_shift_obj)

                # Calculate differences
                inventory_differences = calculate_inventory_differences(current_inventory_map, prev_inventory_map)

            else:
                flash(f"Shift details not found for {date_str} - {shift_str}.", "warning")
        except ValueError:
            flash("Invalid date format provided.", "error")
    else:
        flash("Date and Shift are required to view ENT item acknowledgements.", "warning")
        return redirect(url_for('p3_checklist'))

    return render_template('acknowledge_eyeent.html', date=date_str, shift=shift_str, 
                           ent_inventory=ent_inventory_with_quantities,
                           inventory_differences=inventory_differences)

@acknowledge_bp.route('/acknowledge_dental', methods=['POST'])
def acknowledge_dental():
    date_str = request.form.get('date')
    shift_str = request.form.get('shift')

    users = User.query.order_by(User.username).all()
    dental_inventory_with_quantities = []
    inventory_differences = {}

    if date_str and shift_str:
        try:
            ack_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            current_shift_obj = Shift.query.filter_by(date=ack_date, shift=shift_str).first()

            # Find previous shift
            prev_shift_obj = get_previous_shift(ack_date, shift_str)

            if current_shift_obj:
                dental_items_query = Inventory.query.filter_by(groupid=3).order_by(Inventory.id).all() 
                dental_inventory_with_quantities = ShiftInventory.get_inventory_with_quantities(current_shift_obj.id, dental_items_query)

                # Get current shift inventory
                current_inventory_map = get_inventory_map(current_shift_obj)

                # Get previous shift inventory
                prev_inventory_map = get_inventory_map(prev_shift_obj)

                # Calculate differences
                inventory_differences = calculate_inventory_differences(current_inventory_map, prev_inventory_map)

            else:
                flash(f"Shift details not found for {date_str} - {shift_str}.", "warning")
        except ValueError:
            flash("Invalid date format provided.", "error")
    else:
        flash("Date and Shift are required to view Dental item acknowledgements.", "warning")
        return redirect(url_for('p3_checklist'))

    return render_template('acknowledge_dental.html', date=date_str, shift=shift_str, 
                           users=users, dental_inventory=dental_inventory_with_quantities,
                           inventory_differences=inventory_differences)

@acknowledge_bp.route('/submit_acknowledgement', methods=['POST'])
def submit_acknowledgement():
    date_str = request.form['date']
    shift_str = request.form['shift'] 
    username = request.form['name']  

    try:
        ack_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        user = User.query.filter_by(username=username).first()
        if not user:
            user = User(username=username)
            db.session.add(user)
            db.session.flush() 
            current_app.logger.info(f"New user '{username}' created with ID {user.id}.")
        
        shift_to_acknowledge = Shift.query.filter_by(date=ack_date, shift=shift_str).first()

        if shift_to_acknowledge:
            shift_to_acknowledge.acknowledged = True
            shift_to_acknowledge.acknowledged_by = user.id 
            db.session.add(shift_to_acknowledge)
            db.session.commit()
            flash(f"Shift on {date_str} ({shift_str}) acknowledged successfully by {username}.", "success")
            current_app.logger.info(f"Shift {shift_str} on {ack_date} acknowledged by user {username} (ID: {user.id}).")
        else:
            flash(f"Could not find the shift for {date_str} ({shift_str}) to acknowledge.", "error")
            current_app.logger.warning(f"Attempt to acknowledge non-existent shift: {date_str} - {shift_str} by user {username}.")

    except ValueError:
        flash("Invalid date format provided for acknowledgement.", "error")
        current_app.logger.error(f"Invalid date format '{date_str}' received in submit_acknowledgement.")
    except Exception as e:
        db.session.rollback() 
        flash("An error occurred during the acknowledgement process. Please try again.", "error")
        current_app.logger.error(f"Error during submit_acknowledgement by {username} for {date_str}-{shift_str}: {e}", exc_info=True)

    return redirect(url_for('p3_checklist'))
    
@acknowledge_bp.route('/acknowledge_view')
def acknowledge_view():
    date_str = request.args.get('date')
    shift_str = request.args.get('shift')
    inventory_group_with_quantities = []
    acknowledger_name = "N/A"
    inventory_differences = {}

    if date_str and shift_str:
        try:
            ack_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            current_shift_obj = Shift.query.filter_by(date=ack_date, shift=shift_str).first()

            # Find previous shift
            prev_shift_obj = get_previous_shift(ack_date, shift_str)

            if current_shift_obj:
                if current_shift_obj.acknowledged_by:
                    user = User.query.get(current_shift_obj.acknowledged_by)
                    if user:
                        acknowledger_name = user.username

                # Get current shift inventory
                current_inventory_map = get_inventory_map(current_shift_obj)

                # Get previous shift inventory
                prev_inventory_map = get_inventory_map(prev_shift_obj)

                # Calculate differences
                inventory_differences = calculate_inventory_differences(current_inventory_map, prev_inventory_map)

                inventory_alias = aliased(Inventory)
                inventory_group_query = Group.query.outerjoin(
                    inventory_alias,
                    Group.id == inventory_alias.groupid
                ).options(
                    contains_eager(Group.inventories, alias=inventory_alias)
                ).order_by(Group.id, inventory_alias.id)
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
        flash("Date and Shift are required to view item acknowledgements.", "warning")
        return redirect(url_for('p3_checklist'))

    return render_template('acknowledge_view.html', date=date_str, shift=shift_str,
                           inventory_group=inventory_group_with_quantities,
                           acknowledge_by=acknowledger_name,
                           inventory_differences=inventory_differences)

def get_previous_shift(date_obj, shift_str):
    if shift_str == 'AM':
        prev_shift_date = date_obj - timedelta(days=1)
        prev_shift_type = 'ND'
    else:  # ND
        prev_shift_date = date_obj
        prev_shift_type = 'AM'
    return Shift.query.filter_by(date=prev_shift_date, shift=prev_shift_type).first()

def get_inventory_map(shift_obj):
    if not shift_obj:
        return {}
    inventory = ShiftInventory.query.filter_by(shift_id=shift_obj.id).all()
    return {inv.inventory_id: inv.quantity for inv in inventory}

def calculate_inventory_differences(current_map, previous_map):
    differences = {}
    for inventory_id, curr_qty in current_map.items():
        prev_qty = previous_map.get(inventory_id, 0)
        differences[inventory_id] = curr_qty - prev_qty
    return differences