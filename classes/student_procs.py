from flask import render_template

from classes.sqlite_procs import getDbSession
from models import Students

# ------------------------------------------------------------------------------------------
db_session = getDbSession()

def displayAllStudents():
    student_records = db_session.query(Students).all()
    return render_template('students.html', student_records=student_records)