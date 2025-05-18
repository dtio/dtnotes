from datetime import date, timedelta
import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)
from p3checklist.app import app
from p3checklist.models import db, User, Group, Inventory, Shift, ShiftInventory

def initialize_database():
    """Drops existing tables, creates new ones, and populates with initial data."""
    with app.app_context(): # Operations need to be within an application context
        print("Dropping all tables...")
        db.drop_all()
        print("Creating all tables...")
        db.create_all()
        print("Populating database with initial data...")

        # --- Users ---
        users_data = ['Selina Aulia', 'David Tio']
        for username in users_data:
            user = User(username=username)
            db.session.add(user)
        db.session.commit() # Commit after adding all users
        print(f"Added {len(users_data)} users.")

        # --- Groups ---
        groups_data = [
            {'id': 1, 'groupname': 'Eye'},
            {'id': 2, 'groupname': 'ENT'},
            {'id': 3, 'groupname': 'Dental'}
        ]
        # To ensure specific IDs, we might need to query or handle them carefully.
        # For simplicity here, we'll add them and let SQLAlchemy assign IDs if 'id' is not a manual primary key.
        # If you need to set IDs manually and they are primary keys, ensure your model allows it
        # or insert them one by one and query them back if needed for foreign keys.
        # For this example, let's assume SQLAlchemy handles IDs or we fetch them.
        created_groups = {}
        for group_data in groups_data:
            group = Group(groupname=group_data['groupname'])
            # If you want to assign IDs manually and your model supports it:
            # group = Group(id=group_data['id'], groupname=group_data['groupname'])
            db.session.add(group)
        db.session.commit() # Commit after adding all groups

        # Fetch groups to get their IDs for inventory items
        eye_group = Group.query.filter_by(groupname='Eye').first()
        ent_group = Group.query.filter_by(groupname='ENT').first()
        dental_group = Group.query.filter_by(groupname='Dental').first()  # Corrected typo
        print(f"Added groups: Eye (ID: {eye_group.id}), ENT (ID: {ent_group.id}), Dental (ID: {dental_group.id})")


        # --- Inventory ---
        # Note: The 'quantity' column is removed from the Inventory model itself.
        # Quantity will be in ShiftInventoryLog.
        inventory_data = [
            {'name': 'Agar Plate', 'group': eye_group, 'fixed': True},
            {'name': 'Flexible Scope (Pentax)', 'group': ent_group, 'fixed': True},
            {'name': 'Flexible Scope (Olympus)', 'group': ent_group, 'fixed': True},
            {'name': 'FB Remover Device', 'group': ent_group, 'fixed': True},
            {'name': 'Light Source (Olympus)', 'group': ent_group, 'fixed': True},
            {'name': 'Scope Battery Cable', 'group': ent_group, 'fixed': True},
            {'name': 'Dental Chair', 'notes': 'verified working', 'group': dental_group, 'fixed': True},
            {'name': 'Ear Forceps (145mm)', 'group': ent_group, 'fixed': False},
            {'name': 'Killian Nasal Speculum', 'group': ent_group, 'fixed': False},
            {'name': 'Laryngeal Mirror(K4/6/8/10)', 'group': ent_group, 'fixed': False},
            {'name': 'Hartman Forceps', 'group': ent_group, 'fixed': False},
            {'name': 'West Dressing Forceps', 'group': ent_group, 'fixed': False},
            {'name': 'Ear Tampon Forceps', 'group': ent_group, 'fixed': False},
            {'name': 'Micro Forceps', 'group': ent_group, 'fixed': False},
            {'name': 'Jobson Probe', 'group': ent_group, 'fixed': False},
            {'name': 'Thudicum Nasal', 'group': ent_group, 'fixed': False},
            {'name': 'Tuning Fork (S)', 'group': ent_group, 'fixed': False},
            {'name': 'Tuning Fork (L)', 'group': ent_group, 'fixed': False},
            {'name': 'Tongue Depressor', 'group': ent_group, 'fixed': False},  # Ensure consistency
            {'name': 'Laryngeal Mirror', 'group': ent_group, 'fixed': False}, 
            {'name': 'Huber Handle', 'group': ent_group, 'fixed': False},
            {'name': 'Dental Syringes', 'group': dental_group, 'fixed': False},
            {'name': 'Dental Handpiece', 'group': dental_group, 'fixed': False},
            {'name': 'Dental Suturing Set', 'group': dental_group, 'fixed': False},
            {'name': 'I&D Set', 'group': dental_group, 'fixed': False},
            {'name': 'E&D Set', 'group': dental_group, 'fixed': False},
            {'name': 'Wiring Set', 'group': dental_group, 'fixed': False},
            {'name': 'Dental Spatula', 'group': dental_group, 'fixed': False},
            {'name': 'Adult Cuved Root Forceps', 'group': dental_group, 'fixed': False},
            {'name': 'Dental Pliers', 'group': dental_group, 'fixed': False},
            {'name': 'Adult Special 8 Forceps', 'group': dental_group, 'fixed': False},
            {'name': 'Pedo Lower Anterior Forceps', 'group': dental_group, 'fixed': False},
            {'name': 'Pedo Upper Anterior Forceps', 'group': dental_group, 'fixed': False},
            {'name': 'Coupland 1,2,3 / sets', 'group': dental_group, 'fixed': False},
            {'name': 'Straight Warmick James', 'group': dental_group, 'fixed': False},
            {'name': 'Warmick James(Left/Right)', 'group': dental_group, 'fixed': False},
            {'name': 'Dental Mouth Gag', 'group': dental_group, 'fixed': False},
            {'name': 'Dental Bone Rouger', 'group': dental_group, 'fixed': False},
            {'name': 'Adult Upper Anterior Forceps', 'group': dental_group, 'fixed': False},
            {'name': 'Tweezers', 'group': dental_group, 'fixed': False},
            {'name': 'Dental Mirror', 'group': dental_group, 'fixed': False},
            {'name': 'Adult Upper Rt Molar Forceps', 'group': dental_group, 'fixed': False},
            {'name': 'Adult Upper Lt Molar Forceps', 'group': dental_group, 'fixed': False},
            {'name': 'Plastic Six', 'group': dental_group, 'fixed': False},
            {'name': 'Adult Upper Pre-Molar Forceps', 'group': dental_group, 'fixed': False},
            {'name': 'Adult Lower Anterior Forceps', 'group': dental_group, 'fixed': False}
        ]
        created_inventory_items = {}
        for item_data in inventory_data:
            inventory_item = Inventory(
                name=item_data['name'],
                notes=item_data.get('notes'),
                groupid=item_data['group'].id, 
                fixed=item_data['fixed']
            )
            db.session.add(inventory_item)
        db.session.commit() # Commit after adding all inventory items
        print(f"Added {len(inventory_data)} inventory items.")

        # Fetch all inventory items and create a lookup map by name
        all_inventory_items_list = Inventory.query.all()
        inventory_map_by_name = {item.name: item for item in all_inventory_items_list}
        print(f"Fetched {len(all_inventory_items_list)} inventory items into a map for logging.")

        # --- Shifts (formerly MainData) ---
        # (Using 'shift_name' in dict keys for clarity, maps to 'shift' column in model)

        shifts_to_create = []  # Consistent naming
        for i in range(1, 2): 
            shifts_to_create.append({'date': date.today() - timedelta(days=i), 'shift_name': 'AM', 'acknowledged': False, 'checkout': False})
            shifts_to_create.append({'date': date.today() - timedelta(days=i), 'shift_name': 'ND', 'acknowledged': False, 'checkout': False})

        created_shifts = {}
        for shift_data in shifts_to_create:
            new_shift = Shift(
                date=shift_data['date'],
                shift=shift_data['shift_name'], 
                acknowledged=shift_data['acknowledged'],
                checkout=shift_data['checkout']
            )
            db.session.add(new_shift)
        db.session.commit()
        print(f"Added {len(shifts_to_create)} shift records.")  # Corrected message

        # Fetch a shift for ShiftInventoryLog - Improved naming
        shift_for_logs = Shift.query.filter_by(date=date.today() - timedelta(days=1), shift='AM').first()

        # --- ShiftInventory ---
        if shift_for_logs:
            # Define log data using item names for lookup
            shift_inventory_data = [
                {'item_name': 'Agar Plate', 'quantity': 3},
                {'item_name': 'Flexible Scope (Pentax)', 'quantity': 2},
                {'item_name': 'Flexible Scope (Olympus)', 'quantity': 1},
                {'item_name': 'FB Remover Device', 'quantity': 1},
                {'item_name': 'Light Source (Olympus)', 'quantity': 3},
                {'item_name': 'Scope Battery Cable', 'quantity': 1},
                {'item_name': 'Dental Chair', 'quantity': 1},
                {'item_name': 'Ear Forceps (145mm)', 'quantity': 1},
                {'item_name': 'Killian Nasal Speculum', 'quantity': 1},
                {'item_name': 'Laryngeal Mirror(K4/6/8/10)', 'quantity': 4},
                {'item_name': 'Hartman Forceps', 'quantity': 1},
                {'item_name': 'West Dressing Forceps', 'quantity': 1},
                {'item_name': 'Ear Tampon Forceps', 'quantity': 4},
                {'item_name': 'Micro Forceps', 'quantity': 1},
                {'item_name': 'Jobson Probe', 'quantity': 1},
                {'item_name': 'Thudicum Nasal', 'quantity': 5},
                {'item_name': 'Tuning Fork (S)', 'quantity': 1},
                {'item_name': 'Tuning Fork (L)', 'quantity': 1},
                {'item_name': 'Tongue Depressor', 'quantity': 4},
                {'item_name': 'Laryngeal Mirror', 'quantity': 1},
                {'item_name': 'Huber Handle', 'quantity': 1},
                {'item_name': 'Dental Syringes', 'quantity': 7},
                {'item_name': 'Dental Handpiece', 'quantity': 2},
                {'item_name': 'Dental Suturing Set', 'quantity': 10},
                {'item_name': 'I&D Set', 'quantity': 7},
                {'item_name': 'E&D Set', 'quantity': 9},
                {'item_name': 'Wiring Set', 'quantity': 3},
                {'item_name': 'Dental Spatula', 'quantity': 1},
                {'item_name': 'Adult Cuved Root Forceps', 'quantity': 1},
                {'item_name': 'Dental Pliers', 'quantity': 1},
                {'item_name': 'Adult Special 8 Forceps', 'quantity': 1},
                {'item_name': 'Pedo Lower Anterior Forceps', 'quantity': 2},
                {'item_name': 'Pedo Upper Anterior Forceps', 'quantity': 1},
                {'item_name': 'Coupland 1,2,3 / sets', 'quantity': 2},
                {'item_name': 'Straight Warmick James', 'quantity': 3},
                {'item_name': 'Warmick James(Left/Right)', 'quantity': 2},
                {'item_name': 'Dental Mouth Gag', 'quantity': 1},
                {'item_name': 'Dental Bone Rouger', 'quantity': 2},
                {'item_name': 'Adult Upper Anterior Forceps', 'quantity': 2},
                {'item_name': 'Tweezers', 'quantity': 2},
                {'item_name': 'Dental Mirror', 'quantity': 7},
                {'item_name': 'Adult Upper Rt Molar Forceps', 'quantity': 2},
                {'item_name': 'Adult Upper Lt Molar Forceps', 'quantity': 1},
                {'item_name': 'Plastic Six', 'quantity': 2},
                {'item_name': 'Adult Upper Pre-Molar Forceps', 'quantity': 3},
                {'item_name': 'Adult Lower Anterior Forceps', 'quantity': 3}
            ]

            logs_added_count = 0
            for log_data in shift_inventory_data:
                inventory_item_obj = inventory_map_by_name.get(log_data['item_name'])
                if inventory_item_obj:
                    log_entry = ShiftInventory(
                        shift_id=shift_for_logs.id, # 
                        inventory_id=inventory_item_obj.id,
                        quantity=log_data['quantity'],
                        shift_notes=log_data.get('shift_notes')
                    )
                    db.session.add(log_entry)
                    logs_added_count += 1
                else:
                    print(f"Warning: Inventory item '{log_data['item_name']}' not found in map. Skipping log entry.")
            
            db.session.commit()
            print(f"Added {logs_added_count} shift inventory entries for shift ID {shift_for_logs.id}.")
        else:
            print(f"Warning: Shift for date {date.today() - timedelta(days=1)} AM not found. Skipping ShiftInventory population.")

        print("Database initialized and populated successfully.")

if __name__ == '__main__':
    initialize_database()
