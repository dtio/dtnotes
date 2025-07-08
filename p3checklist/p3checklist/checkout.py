from flask import Blueprint, request, flash, redirect, url_for, render_template, jsonify
from datetime import date, timedelta
from .models import db, ShiftInventory, Inventory, Shift, User

checkout_bp = Blueprint('checkout', __name__)

@checkout_bp.route('/checkout', methods=['POST'])
def checkout():
    date_str = request.form['date']
    shift_str = request.form['shift_type'] 
    frequently_used_items = Inventory.query.filter_by(frequently_used=True).all()
    inventory_items = Inventory.query.filter_by(frequently_used=False).all()
    users = User.query.order_by(User.username).all()
  
    return render_template('checkout.html', frequently_used_items=frequently_used_items, date=date_str, shift_type=shift_str, users=users, inventory_items=inventory_items)

@checkout_bp.route('/search_inventory', methods=['GET'])
def search_inventory():
    query = request.args.get('query', '').strip()
    if query:
        items = Inventory.query.filter(Inventory.name.ilike(f'%{query}%'), Inventory.frequently_used == False).all()
        return jsonify([{'id': item.id, 'name': item.name} for item in items])
    return jsonify([])

@checkout_bp.route('/update_inventory', methods=['POST'])
def update_inventory():
    try:
        # Get the shift type and date from the form
        date_str = request.form['date']
        shift_str = request.form['shift_type']
        username = request.form['name'] 

        shift_date = date.fromisoformat(date_str)

        # Get or create the user
        user = User.query.filter_by(username=username).first()
        if not user:
            user = User(username=username)
            db.session.add(user)
            db.session.flush() 

        # Determine the next shift
        if shift_str == 'AM':
            next_shift_date = shift_date
            next_shift_type = 'ND'
        elif shift_str == 'ND':
            next_shift_date = shift_date + timedelta(days=1)
            next_shift_type = 'AM'
        else:
            flash("Invalid shift type.", "error")
            return redirect(url_for('checkout.checkout'))

        # Get or create the next shift
        next_shift = Shift.query.filter_by(date=next_shift_date, shift=next_shift_type).first()
        if not next_shift:
            next_shift = Shift(date=next_shift_date, shift=next_shift_type, checkout=False)
            db.session.add(next_shift)
            db.session.flush()  # Flush to get the next_shift.id

        next_shift_id = next_shift.id

        # Get all inventory items for the current shift
        current_shift = Shift.query.filter_by(date=shift_date, shift=shift_str).first()
        current_shift_inventory = ShiftInventory.query.filter_by(
            shift_id=current_shift.id
        ).all()

        # Copy all items and quantities to the next shift
        for item in current_shift_inventory:
            new_inventory = ShiftInventory(
                shift_id=next_shift_id,
                inventory_id=item.inventory_id,
                quantity=item.quantity
            )
            db.session.add(new_inventory)

        # Adjust quantities for items listed in the form
        for key, value in request.form.items():
            if key.startswith('return_') or key.startswith('used_'):
                inventory_id = key.split('_')[1]
                quantity = int(value)

                # Find the item in the next shift inventory
                next_shift_inventory = ShiftInventory.query.filter_by(
                    shift_id=next_shift_id, inventory_id=inventory_id
                ).first()

                if next_shift_inventory:
                    if key.startswith('return_'):
                        next_shift_inventory.quantity += quantity  # Add returned quantity
                    elif key.startswith('used_'):
                        next_shift_inventory.quantity -= quantity  # Subtract used quantity

        # Handle dynamically added items
        new_item_names = request.form.getlist('new_item_name[]')
        new_item_returns = request.form.getlist('new_item_return[]')
        new_item_useds = request.form.getlist('new_item_used[]')

        for name, return_qty, used_qty in zip(new_item_names, new_item_returns, new_item_useds):
            inventory_item = Inventory.query.filter_by(name=name).first()
            if inventory_item:
                # Check if the item exists in the next shift inventory
                next_shift_inventory = ShiftInventory.query.filter_by(
                    shift_id=next_shift_id, inventory_id=inventory_item.id
                ).first()

                if next_shift_inventory:
                    next_shift_inventory.quantity += int(return_qty) - int(used_qty)
                else:
                    # Create a new inventory entry for the next shift
                    new_inventory = ShiftInventory(
                        shift_id=next_shift_id,
                        inventory_id=inventory_item.id,
                        quantity=int(return_qty) - int(used_qty)
                    )
                    db.session.add(new_inventory)

        # Mark the current shift as checked out
        current_shift.checkout = True
        current_shift.checkout_by = user.id
        db.session.commit()

        flash("Inventory updated successfully for the next shift!", "success")
        return redirect(url_for('p3_checklist'))
    except Exception as e:
        db.session.rollback()
        flash(f"Failed to update inventory: {str(e)}", "error")
        return redirect(url_for('p3_checklist'))