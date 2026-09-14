import base64
import io
import logging
import os
from datetime import datetime, date, timedelta
from pathlib import Path
from PIL import Image

from flask import current_app, render_template, request
from flask_htmx import make_response

import constants
from classes.promotions_procs import GetNextPromotionDetails, GetNextStudentRank, GetCrntStudentRank
from classes.ranks_procs import show_student_ranks_func
from classes.sqlite_procs import getDbSession
from classes.students.checkin_panel_procs import getCheckinPanel
from models.models import Classes, Attendance, Students, EligibilityCounts
from sqlalchemy import select, func, text

# ------------------------------------------------------------------------------------------
logger = logging.getLogger(__name__)
db_session = getDbSession()
# ------------------------------------------------------------------------------------------

def CheckinMain():
    print(f'badge_checkin was invoked')
    try:
        badge_number = request.form['badgeNumber']
        checkin_datetime = datetime.now()

        # check for valid badge format
        if not badge_number:            return getCheckinMessage("error", "Badge number can not be blank!")
        if not badge_number.isdigit():  return getCheckinMessage("error", "Badge number must be all digits!")

        # check the badge matches a student record
        student_record = db_session.query(Students).filter_by(badgeNumber=badge_number).first()
        if not student_record:          return getCheckinMessage("error", "Student record not found!")

        if not student_record.currentRankNum or not student_record.studentPromotionDate:
            return show_student_ranks_func()


        # check for multiple checkin actions, on a single day
        daily_checkin_count_stmt = (select(func.count())
            .select_from(Attendance)
            .where(
                Attendance.badgeNumber == student_record.badgeNumber,
                Attendance.checkinDate == checkin_datetime.strftime(constants.fmtDate)
            )
        )
        daily_checkin_count = db_session.scalar(daily_checkin_count_stmt)

        ## day of week in db starts with Sunday = 0, ends with Saturday = 6
        ## add 1 to adjust for that
        day_of_week = checkin_datetime.date().weekday() + 1

        # save the image to static directory, let html fetch large files
        student_image_name = SaveStudentImage(student_record)
        student_image_url  = f"/static/images/{student_image_name}"

        eligible_message = GetPromotionMessage(student_record)

        if daily_checkin_count > 0:
            return getCheckinPanel(
                'error',
                'is already checked in for today!',
                student_image_url,
                student_record,
                GetCurrentClass(day_of_week),
                promotion_message=eligible_message
            )

        # get the current class and insert the attendance record
        selected_class = GetCurrentClass(day_of_week)
        next_class     = GetNextClass(checkin_datetime)
        if not selected_class:
            return getCheckinPanel(
                status   = 'error',
                message  = 'was not checked in, no class available',
                student_image_url = student_image_url,
                student_record    = student_record,
                other_message     = f'Next class is {next_class.className}',
                promotion_message = eligible_message
            )

        InsertAttendanceRecord(student_record, selected_class, day_of_week)

        # if the student does not have a rank entry, display the select rank dialog
        return getCheckinPanel(
            status       = 'success',
            message      =  'Checkin was completed',
            student_image_url = student_image_url,
            student_record    = student_record,
            other_message     = f'Current class is {selected_class.className}',
            promotion_message =eligible_message
        )

    except Exception as ex:
        print(str(ex))
        return getCheckinMessage('error', str(ex))

def GetPromotionMessage(student_record: Students) -> str:
    try:
        next_promotion_record = GetNextPromotionDetails(student_record)

        # get next promotion eligibility fields
        class_count_stmt = select(func.count()).where(Attendance.badgeNumber == student_record.badgeNumber)
        student_class_count = db_session.scalar(class_count_stmt)

        # if student rank exceeds class count required, show no class count message
        eligibility_counts = (db_session.execute(GetEligibilityCountsQuery(), {"badgeNumber": student_record.badgeNumber})) #.scalar()
        for row in eligibility_counts:
            print(f"badgeNumber: {row.badgeNumber}, classCount: {row.classCount}")

        eligibility_records = (db_session
                               .query(EligibilityCounts)
                               .where(EligibilityCounts.eligibleCount > student_class_count)
                               .order_by(EligibilityCounts.eligibleCount.asc())
                               .first())
        #  fetch the next promotion counts and message
        classes_until_next = eligibility_records.eligibleCount - student_class_count
        #eligible_message = f'{classes_until_next} classes until eligible for {eligibility_records.stripeTitle}'
        eligible_message = next_promotion_record.promotion_message
        return eligible_message
    except Exception as ex:
        print(f'Error: {str(ex)}')

def GetEligibilityCountsQuery() -> text:
    return text('''
select a.badgeNumber, 
       count(*) as classCount,
       s.currentRankNum,
       s.currentRankName,
       r.TotalRequiredClasses
from   attendance  a
join   students    s
  on   a.badgeNumber = s.badgeNumber
join   ranks       r
  on   r.beltId    = s.currentRankNum  
where  a.badgeNumber = :badgeNumber
order  by a.badgeNumber
    ''')

# --------------------------------------------------------------------
# Search for a class within the start and stop times
# --------------------------------------------------------------------
def GetCurrentClass(day_of_week: int, before_interval:int = 15, after_interval:int = 15):
    #class_times = Classes.objects.filter(class_day_of_week=today).order_by('class_start_time')
    class_times = db_session.query(Classes).filter_by(classDayOfWeek=day_of_week)

    current_date = datetime.now()
    current_date_str = current_date.strftime("%m/%d/%Y")
    date_format = "%m/%d/%Y %I:%M %p"
    for class_record in class_times:
        start_checkin_str  = current_date_str + ' ' + class_record.classStartTime
        start_checkin_date = datetime.strptime(start_checkin_str, date_format)
        finis_checkin_str  = current_date_str + ' ' + class_record.classFinisTime
        finis_checkin_date = datetime.strptime(finis_checkin_str, date_format)

        start_checkin_time = start_checkin_date - timedelta(minutes=before_interval)
        finis_checkin_time = start_checkin_date + timedelta(minutes=after_interval)

        DisplayClassDateTimes(start_checkin_time, finis_checkin_time, current_date)

        if start_checkin_time <= current_date <= finis_checkin_time:
            return class_record

        if start_checkin_date <= current_date <= finis_checkin_date:
            return class_record

    return None


def GetNextClass(checkin_datetime: datetime, before_interval: int = 15) -> Classes | None:
    try:
        day_of_week = checkin_datetime.date().weekday() + 1
        class_times = db_session.query(Classes).filter_by(classDayOfWeek=day_of_week)
        current_date_str = checkin_datetime.strftime("%m/%d/%Y")
        date_format = "%m/%d/%Y %I:%M %p"
        for class_record in class_times:
            start_checkin_str  = current_date_str + ' ' + class_record.classStartTime
            start_checkin_date = datetime.strptime(start_checkin_str, date_format)
            start_checkin_time = start_checkin_date - timedelta(minutes=before_interval)
            if start_checkin_time >= checkin_datetime:
                return class_record
        return None
    except Exception as ex:
        print(f'Error: {str(ex)}')
        raise ex
# --------------------------------------------------------------------
# Insert the attendance checkin record
# --------------------------------------------------------------------
def DisplayClassDateTimes(start_datetime: date, finis_datetime: date, checkin_date: date = None):
    if checkin_date:
        logger.info(
            f'{checkin_date.strftime(constants.dayNameAbbr)} - '
            f'{start_datetime.strftime(constants.fmtDateTime3)} '
            f'{finis_datetime.strftime(constants.fmtDateTime3)} '
            f'{checkin_date.strftime(constants.fmtDateTime3)}'
        )
    else:
        logger.info(
            f'{checkin_date.strftime(constants.dayNameAbbr)} - '
            f'{start_datetime.strftime(constants.fmtDateTime3)} '
            f'{finis_datetime.strftime(constants.fmtDateTime3)} '
        )

# --------------------------------------------------------------------
# Insert the attendance checkin record
# --------------------------------------------------------------------
def InsertAttendanceRecord(student_record: Students, class_record: Classes, day_of_week: int):
    currentTime     = datetime.now()
    checkinDateTime = currentTime.strftime("%Y-%m-%d %H:%M:%S")
    checkinDate     = currentTime.strftime("%m/%d/%Y")
    checkinTime     = currentTime.strftime("%I:%M %p")

    attendance_record = Attendance()
    attendance_record.badgeNumber       = student_record.badgeNumber
    attendance_record.checkinDayOfWeek  = day_of_week
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

