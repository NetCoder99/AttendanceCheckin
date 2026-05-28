from flask import render_template

from classes.image_procs import get_rms_default_image
from classes.sqlite_procs import getDbSession
from models import Students

# ------------------------------------------------------------------------------------------
db_session = getDbSession()

def displayAllStudents():
    student_records = db_session.query(Students).all()
    for student_record in student_records:
        if not student_record.studentImageBase64:
            student_record.studentImageBase64 = get_rms_default_image()
            student_record.studentImageType   = "jpeg"

    return render_template('students_list.html', student_records=student_records)