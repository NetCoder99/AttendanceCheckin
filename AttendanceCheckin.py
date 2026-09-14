# pyinstaller --add-data "templates;templates" --add-data "static;static" AttendanceCheckin.py
# pyinstaller --add-data "templates:templates" --add-data "static:static" AttendanceCheckin.py
# rsync -av --exclude '.venv' --exclude 'dist'  /home/johnd/AttendanceTracker/AttendancePromotions /media/johnd/USB31FD/PythonProjects/AttendancePromotions
import logging
import logging.config
import loggingConf

# sqlacodegen sqlite:///C:\Users\jdugger01\AppData\Roaming\Attendance\AttendanceV3.db --tables requirements > requirements.py

from flask import Flask, render_template
from flaskwebgui import FlaskUI
import tkinter as tk
from tkinter import messagebox

import constants
from classes.checkin_procs import getCheckinMessage, CheckinMain
from classes.processScanner import DisplayActiveProcesses, IsProcessActive
from classes.ranks_procs import getRanksMessage, getBadgeMessage, get_stripes_func, show_student_ranks_func, update_required_rank_func
from classes.sqlite_procs import getDbSession
#from classes.students.student_procs import displayAllStudents
#from classes.table_procs import displayAllTables

logging_config_dict = loggingConf.LOGGING_CONFIG
logging.config.dictConfig(logging_config_dict)
logger = logging.getLogger(__name__)


app = Flask(__name__)
#app.config['EXPLAIN_TEMPLATE_LOADING'] = True

# ------------------------------------------------------------------------------------------
db_session = getDbSession()

@app.route('/')
@app.route('/checkin')
def checkin():
    return render_template('checkin.html')

# --------------------------------------------------------------------
# Update stripe dropdown on Belt Id change event
# --------------------------------------------------------------------
@app.route('/get_stripes')
def get_stripes():
    try:
        return get_stripes_func()
    except Exception as ex:
        print(str(ex))
        return getRanksMessage('error', str(ex))

# --------------------------------------------------------------------
# Display the rank required dialog form
# --------------------------------------------------------------------
@app.route('/show_student_ranks_modal')
def show_student_ranks_modal():
    print(f'show_student_ranks_modal was invoked')
    try:
        return show_student_ranks_func()
    except Exception as ex:
        print(str(ex))
        return getBadgeMessage('error', str(ex))

# --------------------------------------------------------------------
@app.route('/update_required_rank', methods=['POST'])
def update_required_rank():
    print(f'update_required_rank was invoked')
    try:
        return update_required_rank_func()
    except Exception as ex:
        print(str(ex))
        return getRanksMessage('error', str(ex))

# --------------------------------------------------------------------
# Process the checkin activity
# --------------------------------------------------------------------
@app.route('/badge_checkin', methods=['POST'])
def badge_checkin():
    print(f'badge_checkin was invoked')
    try:
        return CheckinMain()
    except Exception as ex:
        print(str(ex))
        return getCheckinMessage('error', str(ex))

if __name__ == '__main__':
    DisplayActiveProcesses('attendance')
    ok_to_start = IsProcessActive(constants.applicationName)

    if ok_to_start['status'] == 'ok':
        ui = FlaskUI(app=app, width=1250, height=900, fullscreen=False, server='flask')
        ui.run()
    else:
        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo("AttendanceCheckin - Error", ok_to_start['message'])
        print(ok_to_start['message'])
    #app.run(debug=False,  port=5002)