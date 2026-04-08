# pyinstaller --add-data "templates;templates" --add-data "static;static" AttendanceCheckin.py

from flask import Flask, render_template, request
from flaskwebgui import FlaskUI
from sqlalchemy import select, func

from classes.checkin_procs import getCheckinMessage, GetCurrentClass, InsertAttendanceRecord, SaveStudentImage, \
    getCheckinPanel
from classes.imports.import_students import importStudents
from classes.ranks_procs import getRanksMessage, getBadgeMessage, get_stripes_func, show_student_ranks_func, update_required_rank_func
from classes.sqlite_procs import getDbSession
from classes.table_procs import displayAllTables
from models import Students, EligibilityCounts, Attendance

app = Flask(__name__)
#app.config['EXPLAIN_TEMPLATE_LOADING'] = True

# ------------------------------------------------------------------------------------------
db_session = getDbSession()

@app.route('/')
@app.route('/checkin')
def checkin():
    return render_template('checkin.html')

@app.route('/tables')
def tables():
    return displayAllTables()

@app.route('/about')
def about():
    return render_template('about.html')


# --------------------------------------------------------------------
# Misc import actions
# --------------------------------------------------------------------
@app.route('/import_students')
def import_students():
    import_counts = importStudents("AttendanceV2.db", "AttendanceV3.db")
    return import_counts



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
        badge_number = request.form['badgeNumber']

        # check for valid badge format
        if not badge_number: return getCheckinMessage("error", "Badge number can not be blank!")
        if not badge_number.isdigit(): return getCheckinMessage("error", "Badge number must be all digits!")

        # check the badge matches a student record
        student_record = db_session.query(Students).filter_by(badgeNumber=badge_number).first()
        if not student_record: return getCheckinMessage("error", "Student record not found!")

        # check for multiple checkin actions

        # get the current class and insert the attendance record
        selected_class = GetCurrentClass()
        InsertAttendanceRecord(student_record, selected_class)

        # if the student does not have a rank entry, display the select rank dialog
        if not student_record.currentRankNum:
            return show_student_ranks_func()

        # get next promotion eligibility fields
        class_count_stmt    = select(func.count()).where(Attendance.badgeNumber == badge_number)
        student_class_count = db_session.scalar(class_count_stmt)

        eligibility_records = (db_session
                            .query(EligibilityCounts)
                            .where(EligibilityCounts.eligibleCount > student_class_count)
                            .order_by(EligibilityCounts.eligibleCount.asc())
                            .first())

        #  fetch the next promotion counts and message
        classes_until_next = eligibility_records.eligibleCount - student_class_count
        eligible_message = f'{classes_until_next} classes until eligible for {eligibility_records.stripeTitle}'

        # save the image to static directory, let html fetch large files
        student_image_name = SaveStudentImage(student_record)
        student_image_url  = f"/static/images/{student_image_name}"
        return getCheckinPanel(
            'success',
            'Checkin was completed',
            student_image_url,
            student_record,
            selected_class,
            promotion_message=eligible_message
        )

    except Exception as ex:
        print(str(ex))
        return getCheckinMessage('error', str(ex))



if __name__ == '__main__':
    #list_processes("attendance")
    #ui = FlaskUI(app=app, width=1250, height=900, fullscreen=False, server='flask')
    #ui.run()
    app.run()