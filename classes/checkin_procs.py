import base64
import io
import os
from datetime import datetime
from pathlib import Path
from PIL import Image

from flask import current_app, render_template, request
from flask_htmx import make_response

from classes.ranks_procs import show_student_ranks_func
from classes.sqlite_procs import getDbSession
from models import Classes, Attendance, Students, EligibilityCounts
from sqlalchemy import select, func

# ------------------------------------------------------------------------------------------
db_session = getDbSession()

def CheckinMain():
    print(f'badge_checkin was invoked')
    try:
        badge_number = request.form['badgeNumber']

        # check for valid badge format
        if not badge_number: return getCheckinMessage("error", "Badge number can not be blank!")
        if not badge_number.isdigit(): return getCheckinMessage("error", "Badge number must be all digits!")

        # check the badge matches a student record
        student_record = db_session.query(Students).filter_by(badgeNumber=badge_number).first()
        if not student_record: return getCheckinMessage("error", "Student record not found!")

        # check for multiple checkin actions, on a single day

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




# --------------------------------------------------------------------
# Search for class within the start and stop times
# --------------------------------------------------------------------
def GetCurrentClass():
    ## day of week in db starts with Sunday = 0, ends with Saturday = 6
    ## add 1 to adjust for that
    today = datetime.now().date().weekday() + 1

    #class_times = Classes.objects.filter(class_day_of_week=today).order_by('class_start_time')
    class_times = db_session.query(Classes).filter_by(classDayOfWeek=today)


    current_date = datetime.now()
    current_date_str = current_date.strftime("%m/%d/%Y")
    date_format = "%m/%d/%Y %I:%M %p"
    for class_record in class_times:
        checkin_start_str  = current_date_str + ' ' + class_record.classStartTime
        checkin_start_date = datetime.strptime(checkin_start_str, date_format)
        checkin_finis_str  = current_date_str + ' ' + class_record.classFinisTime
        checkin_finis_date = datetime.strptime(checkin_finis_str, date_format)
        if checkin_start_date <= current_date <= checkin_finis_date:
            return class_record
    return None

# --------------------------------------------------------------------
# Insert the attendance checkin record
# --------------------------------------------------------------------
def InsertAttendanceRecord(student_record: Students, class_record: Classes):
    currentTime     = datetime.now()
    checkinDateTime = currentTime.strftime("%Y-%m-%d %H:%M:%S")
    checkinDate     = currentTime.strftime("%m/%d/%Y")
    checkinTime     = currentTime.strftime("%I:%M %p")

    attendance_record = Attendance()
    attendance_record.badgeNumber       = student_record.badgeNumber
    attendance_record.checkinDateTime   = checkinDateTime
    attendance_record.checkinDate       = checkinDate
    attendance_record.checkinTime       = checkinTime

    attendance_record.studentFirstName  = student_record.firstName
    attendance_record.studentLastName   = student_record.lastName
    attendance_record.studentRankNum    = student_record.currentRankNum
    attendance_record.studentRankName   = student_record.currentRankName
    attendance_record.studentStripeId   = student_record.currentStripeId
    attendance_record.studentStripeName = student_record.currentStripeName
    if class_record:
        attendance_record.classNum         = class_record.classNum
        attendance_record.className        = class_record.className
        attendance_record.classStartTime   = class_record.classStartTime
        attendance_record.styleNum         = class_record.styleNum
        attendance_record.appliesPromotion = class_record.isPromotions
    db_session.add(attendance_record)
    db_session.commit()

# --------------------------------------------------------------------
# Save the student image to the django static dir, can't pass
# very large strings to html
# --------------------------------------------------------------------
def SaveStudentImage(student_record: Students):
    try:
        if not student_record.studentImageName:
            return 'RSM_Logo_002.jpg'

        image_name   = student_record.studentImageName.split('.')[0] + '.webp'
        output_path  = os.path.join(current_app.root_path, 'static', 'images', image_name)
        file_path = Path(output_path)
        if file_path.exists():
            return image_name
        else:
            image_data = base64.b64decode(student_record.studentImageBase64)
            image = Image.open(io.BytesIO(image_data))
            quality      = '80'
            image.save(output_path, 'WEBP', quality=quality)
            return image_name
    except Exception as e:
        print(f"Error decoding base64: {str(e)}. Check for valid Base64 characters and padding.")
        raise e

# --------------------------------------------------------------------
# Various htmx response helpers
# --------------------------------------------------------------------
def getCheckinMessage(status, message):
    alert_class = "text-danger" if status == 'error' else "text-success"
    badge_message = render_template(
        "partials/badgeMessage.html",
        alert_class=alert_class,
        badge_message_str = message
    )
    response = make_response(badge_message)
    response.headers['HX-Retarget'] = '#badgeMessage'  # CSS Selector
    response.headers['HX-Trigger-After-Settle'] = 'checkin_message'
    return response

# --------------------------------------------------------------------
def getCheckinPanel(
        status,
        message,
        student_image_url,
        student_record: Students,
        selected_class: Classes,
        promotion_message: str
):
    try:
        alert_class    = "text-danger" #  if status == 'error' else ""
        if selected_class:
            badge_message  = f'{student_record.firstName} {student_record.lastName} has checked in to {selected_class.className}'
        else:
            badge_message  = f'{student_record.firstName} {student_record.lastName} not checked in, no class at this time.'

        #class_message  = f'Checked in to {selected_class.className}'

        badge_message = render_template(
            "partials/checkin_response_panel.html",
            alert_class       = alert_class,
            badge_message_str = message,
            checkinMessage    = badge_message,
            promotionMessage  = promotion_message,
            otherMessage      = '',   #"Other message content",
            image_srce_url    = student_image_url
        )
        response = make_response(badge_message)
        response.headers['HX-Retarget'] = '#checkin_response_panel'  # CSS Selector
        response.headers['HX-Swap']     = 'innerHTML'
        response.headers['HX-Trigger-After-Settle'] = 'checkin_panel'
        return response
    except Exception as ex:
        print(str(ex))
        raise ex

# --------------------------------------------------------------------
def getCheckinError(status, message):
    alert_class = "text-danger" if status == 'error' else "text-success"
    badge_message = render_template(
        "partials/badgeMessage.html",
        alert_class=alert_class,
        badge_message_str = message
    )
    response = make_response(badge_message)
    response.headers['HX-Retarget'] = '#badgeMessage'  # CSS Selector
    response.headers['HX-Trigger-After-Settle'] = 'checkin_error'
    return response