from datetime import date, timedelta
import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Set up project root for relative imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Import app and db from your p3checklist application
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
        
        # Create groups. If your Group model auto-increments IDs,
        # the 'id' in groups_data is just for reference here.
        # We'll fetch them by name to ensure we get the correct SQLAlchemy objects.
        for group_data in groups_data:
            group = Group(groupname=group_data['groupname'])
            db.session.add(group)
        db.session.commit() # Commit after adding all groups

        # Fetch groups to get their IDs for inventory items
        eye_group = Group.query.filter_by(groupname='Eye').first()
        ent_group = Group.query.filter_by(groupname='ENT').first()
        dental_group = Group.query.filter_by(groupname='Dental').first()
        print(f"Added groups: Eye (ID: {eye_group.id}), ENT (ID: {ent_group.id}), Dental (ID: {dental_group.id})")

        # --- Inventory ---
        inventory_data = [
            {'name': 'Agar Plate', 'group': eye_group, 'location': 'P2C Fridge', 'parquantity': 3},
            {'name': 'Bronchoscope (Pentax)', 'group': ent_group, 'location': 'Trolley + Briefcase + Top', 'parquantity': 1},
            {'name': 'Flexible Scope (Olympus)', 'group': ent_group, 'location': 'Trolley + Briefcase + Top', 'parquantity': 1},
            {'name': 'FB Remover Device', 'group': ent_group, 'location': 'Trolley + Briefcase + Top', 'parquantity': 1},
            {'name': 'Light Source (Olympus)', 'group': ent_group, 'location': 'Trolley + Briefcase + Top', 'parquantity': 3},
            {'name': 'Scope Battery Cable', 'group': ent_group, 'location': 'Trolley + Briefcase + Top', 'parquantity': 1},
            {'name': 'Ear Forceps (145mm)', 'group': ent_group, 'location': 'Drawer 1', 'frequently_used': True, 'parquantity': 1},
            {'name': 'Killian Nasal Speculum', 'group': ent_group, 'location': 'Drawer 1', 'parquantity': 1},
            {'name': 'Laryngeal Mirror(K4/6/8/10)', 'group': ent_group, 'location': 'Drawer 1', 'parquantity': 8},
            {'name': 'Hartman Forceps', 'group': ent_group, 'location': 'Drawer 1', 'parquantity': 1},
            {'name': 'West Dressing Forceps', 'group': ent_group, 'location': 'Drawer 1', 'parquantity': 5},
            {'name': 'Ear Tampon Forceps', 'group': ent_group, 'location': 'Drawer 1', 'frequently_used': True, 'parquantity': 8},
            {'name': 'Micro Forceps', 'group': ent_group, 'location': 'Drawer 1', 'frequently_used': True, 'parquantity': 6},
            {'name': 'Jobson Probe', 'group': ent_group, 'location': 'Drawer 1', 'parquantity': 4},
            {'name': 'Thudicum Nasal', 'group': ent_group, 'location': 'Drawer 2', 'frequently_used': True, 'parquantity': 5},
            {'name': 'Tuning Fork (S)', 'group': ent_group, 'location': 'Drawer 2', 'parquantity': 1},
            {'name': 'Tuning Fork (L)', 'group': ent_group, 'location': 'Drawer 2', 'parquantity': 1},
            {'name': 'Tongue Depressor', 'group': ent_group, 'location': 'Drawer 2', 'frequently_used': True, 'parquantity': 9}, 
            {'name': 'Laryngeal Mirror', 'group': ent_group, 'location': 'Drawer 2', 'parquantity': 1}, 
            {'name': 'Huber Handle', 'group': ent_group, 'location': 'Drawer 2', 'parquantity': 1},
            {'name': 'Dental Suturing Set', 'group': dental_group, 'location': 'Top Cupboard', 'frequently_used': True, 'parquantity': 10},
            {'name': 'I&D Set', 'group': dental_group, 'location': 'Top Cupboard', 'parquantity': 7},
            {'name': 'E&D Set', 'group': dental_group, 'location': 'Top Cupboard', 'parquantity': 9},
            {'name': 'Wiring Set', 'group': dental_group, 'location': 'Top Cupboard', 'parquantity': 3},
            {'name': 'Tweezers', 'group': dental_group, 'location': 'Drawer 1', 'parquantity': 2},
            {'name': 'Adult Cuved Root Forceps', 'group': dental_group, 'location': 'Drawer 2', 'parquantity': 1},
            {'name': 'Dental Pliers', 'group': dental_group, 'location': 'Drawer 2', 'parquantity': 1},
            {'name': 'Adult Special 8 Forceps', 'group': dental_group, 'location': 'Drawer 2', 'parquantity': 1},
            {'name': 'Pedo Lower Anterior Forceps', 'group': dental_group, 'location': 'Drawer 2', 'parquantity': 2},
            {'name': 'Pedo Upper Anterior Forceps', 'group': dental_group, 'location': 'Drawer 2', 'parquantity': 1},
            {'name': 'Plastic Six', 'group': dental_group, 'location': 'Drawer 2', 'parquantity': 2},
            {'name': 'Coupland 1,2,3 / sets', 'group': dental_group, 'location': 'Drawer 3', 'parquantity': 2},
            {'name': 'Straight Warmick James', 'group': dental_group, 'location': 'Drawer 3', 'parquantity': 3},
            {'name': 'Warmick James(Left/Right)', 'group': dental_group, 'location': 'Drawer 3', 'parquantity': 2},
            {'name': 'Dental Mouth Gag', 'group': dental_group, 'location': 'Drawer 4', 'parquantity': 1},
            {'name': 'Dental Bone Rouger', 'group': dental_group, 'location': 'Drawer 4', 'parquantity': 2},
            {'name': 'Adult Upper Anterior Forceps', 'group': dental_group, 'location': 'Drawer 4', 'parquantity': 2},
            {'name': 'Dental Syringes', 'group': dental_group, 'location': 'Drawer 4', 'frequently_used': True, 'parquantity': 8},
            {'name': 'Dental Mirror', 'group': dental_group, 'location': 'Drawer 4', 'parquantity': 7},
            {'name': 'Adult Upper Rt Molar Forceps', 'group': dental_group, 'location': 'Drawer 5', 'parquantity': 2},
            {'name': 'Adult Upper Lt Molar Forceps', 'group': dental_group, 'location': 'Drawer 5', 'parquantity': 1},
            {'name': 'Dental Handpiece', 'group': dental_group, 'location': 'Drawer 5', 'parquantity': 2},
            {'name': 'Adult Upper Pre-Molar Forceps', 'group': dental_group, 'location': 'Drawer 5', 'parquantity': 3},
            {'name': 'Adult Lower Anterior Forceps', 'group': dental_group, 'location': 'Drawer 5', 'parquantity': 3},
            {'name': 'Dental Chair', 'notes': 'verified working', 'group': dental_group, 'location': 'Drawer 5', 'parquantity': 1}
        ]

        for item_data in inventory_data:
            inventory_item = Inventory(
                name=item_data['name'],
                notes=item_data.get('notes'),
                groupid=item_data['group'].id,
                location=item_data['location'],
                frequently_used=item_data.get('frequently_used', False),
                parquantity=item_data.get('parquantity', 0)
            )
            db.session.add(inventory_item)
        db.session.commit()
        print(f"Added {len(inventory_data)} inventory items.")

        # Fetch all inventory items for copying to ShiftInventory
        all_inventory_items_list = Inventory.query.all()
        print(f"Fetched {len(all_inventory_items_list)} inventory items for ShiftInventory population.")

        # --- Shifts (formerly MainData) ---
        shifts_to_create = []
        for i in range(1, 2):
            shifts_to_create.append({'date': date.today() - timedelta(days=i), 'shift_name': 'AM', 'acknowledged': False, 'checkout': False})
            shifts_to_create.append({'date': date.today() - timedelta(days=i), 'shift_name': 'ND', 'acknowledged': False, 'checkout': False})

        for shift_data in shifts_to_create:
            new_shift = Shift(
                date=shift_data['date'],
                shift=shift_data['shift_name'],
                acknowledged=shift_data['acknowledged'],
                checkout=shift_data['checkout']
            )
            db.session.add(new_shift)
        db.session.commit()
        print(f"Added {len(shifts_to_create)} shift records.")

        # Fetch a shift for ShiftInventory
        shift_for_logs = Shift.query.filter_by(date=date.today() - timedelta(days=1), shift='AM').first()

        # --- Populate ShiftInventory with all Inventory items using parquantity as quantity ---
        if shift_for_logs:
            logs_added_count = 0
            for inventory_item_obj in all_inventory_items_list:
                log_entry = ShiftInventory(
                    shift_id=shift_for_logs.id,
                    inventory_id=inventory_item_obj.id,
                    quantity=inventory_item_obj.parquantity,
                    shift_notes=inventory_item_obj.notes 
                )
                db.session.add(log_entry)
                logs_added_count += 1
            
            db.session.commit()
            print(f"Added {logs_added_count} shift inventory entries for shift ID {shift_for_logs.id} from all inventory items.")
        else:
            print(f"Warning: Shift for date {date.today() - timedelta(days=1)} AM not found. Skipping ShiftInventory population.")

        print("Database initialized and populated successfully.")

if __name__ == '__main__':
    initialize_database()