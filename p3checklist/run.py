import os
from p3checklist.app import app # Import the app instance from your p3checklist package

if __name__ == '__main__':
    # It's good practice to ensure database tables are created if they don't exist.
    # However, for production, you'd typically use migrations (e.g., Flask-Migrate).
    # For development, you might have db.create_all() in your app factory or init_db.py.
    # If your init_db.py handles table creation, you might not need it here.
    
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)), debug=True)