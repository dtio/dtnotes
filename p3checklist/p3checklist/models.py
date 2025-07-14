from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Date, String, Boolean, Integer, Text, ForeignKey, UniqueConstraint

db = SQLAlchemy()

class Shift(db.Model): # Changed ShiftData to MainData
    __tablename__ = 'shift'
    id = db.Column(Integer, primary_key=True)
    date = db.Column(Date, nullable=False) # unique=True removed
    shift = db.Column(String(2), nullable=False)
    acknowledged = db.Column(Boolean, nullable=False, default=False)
    checkout = db.Column(Boolean, nullable=False, default=False)
    acknowledged_by = db.Column(Integer, ForeignKey('users.id'), nullable=True)
    checkout_by = db.Column(Integer, ForeignKey('users.id'), nullable=True)

    # Relationship to ShiftInventory logs
    inventory_logs = db.relationship('ShiftInventory', backref='shift_details', lazy='dynamic')

    # Reflects the constraint in init_db.sh
    __table_args__ = (UniqueConstraint('date', 'shift', name='uq_date_shift'),)

    def __repr__(self):
        return f'<Shift(date={self.date}, shift={self.shift}, acknowledged={self.acknowledged}, checkin={self.checkin})>' 

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(Integer, primary_key=True)
    username = db.Column(String(80), unique=True, nullable=False)
    # Add any other user-related fields here, e.g., password_hash, email

    def __repr__(self):
        return f'<User {self.username}>'

class Group(db.Model):
    __tablename__ = 'groups' # Aligns with DROP TABLE and FOREIGN KEY in init_db.sh
    id = db.Column(Integer, primary_key=True)
    groupname = db.Column(String(80), unique=True, nullable=False)

    inventories = db.relationship('Inventory', backref='group', lazy=True, order_by="Inventory.id")

    def __repr__(self):
        return f'<Group {self.groupname}>'

class Inventory(db.Model):
    __tablename__ = 'inventory'
    id = db.Column(Integer, primary_key=True)
    name = db.Column(String(255), nullable=False)
    notes = db.Column(Text, nullable=True)
    groupid = db.Column(Integer, ForeignKey('groups.id'), nullable=False)
    location = db.Column(Text, nullable=False)
    frequently_used = db.Column(Boolean, nullable=False, default=False)
    parquantity = db.Column(Integer, nullable=False) 
    
    # Relationship to ShiftInventory logs
    shift_logs = db.relationship('ShiftInventory', backref='item_details', lazy='dynamic')

    def __repr__(self):
        return f'<Inventory {self.name}>'

class ShiftInventory(db.Model):
    __tablename__ = 'shift_inventory' # Or 'shift_inventory_log' if you prefer, match init_db.py
    id = db.Column(Integer, primary_key=True)
    shift_id = db.Column(Integer, ForeignKey('shift.id'), nullable=False)
    inventory_id = db.Column(Integer, ForeignKey('inventory.id'), nullable=False)
    quantity = db.Column(Integer, nullable=False)
    shift_notes = db.Column(Text, nullable=True) # Optional notes for this item during this specific shift

    # Ensures one entry per item per shift
    __table_args__ = (UniqueConstraint('shift_id', 'inventory_id', name='uq_shift_inventory_item'),)

    @staticmethod
    def get_inventory_with_quantities(shift_id, inventory_items_list):
        shift_inventory_logs = ShiftInventory.query.filter_by(shift_id=shift_id).all()
        quantities_map = {log.inventory_id: log.quantity for log in shift_inventory_logs}
        for item in inventory_items_list:
            item.current_shift_quantity = quantities_map.get(item.id, 'N/A') # Or 0 if you prefer
        return inventory_items_list

    def __repr__(self):
        return f'<ShiftInventory ShiftID: {self.shift_id}, ItemID: {self.inventory_id}, Qty: {self.quantity}>'