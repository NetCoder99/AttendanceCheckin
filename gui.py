from flaskwebgui import FlaskUI

from attendanceBase.wsgi import application

import threading
import webview

def run_django_server():
    # Code to start the Django server (e.g., using a WSGI server like Gunicorn/Waitress for production)
    # For development, you can use Django's built-in server:
    import os
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendanceBase.settings')
    try:
        from django.core.management import execute_from_command_line
        execute_from_command_line(['manage.py', 'runserver', '127.0.0.1:8002'])
    except ImportError:
        # Handle the error
        pass

# Create and start the Django server in a separate thread
t = threading.Thread(target=run_django_server)
t.daemon = True # Allows the thread to exit with the main program
t.start()

# Create the native PyWebView window pointing to the local server URL
webview.create_window('My Django Desktop App', 'http://127.0.0.1')
webview.start()
