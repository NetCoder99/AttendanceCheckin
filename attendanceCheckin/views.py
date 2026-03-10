import json

from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from datetime import datetime

from attendanceCheckin.forms import CheckinForm, RequiredRanks
from attendanceData.models import Students, Classes, Belts, BeltsByRank, Stripes, Promotions, Attendance


# --------------------------------------------------------------------
# Display the main checkin page
# --------------------------------------------------------------------
def checkin_student(request):
    print(f'checkin_student was invoked')
    context = {
        'title' : 'Student Checkin',
        'form' : CheckinForm()
    }
    return render(request, 'checkin_student.html', context)

# --------------------------------------------------------------------
# Update stripe dropdown on Belt Id change event
# --------------------------------------------------------------------
def get_stripes(request):
    try:
        print(f'get_stripes was invoked')
        selected_rank = request.GET.get('required_ranks')
        stripes_query = f'select * from vw_stripes_by_belt_id where  rankNum = {selected_rank}'
        stripes_queryset = BeltsByRank.objects.raw(stripes_query)
        stripes_list = []
        for stripe_record in stripes_queryset:
            stripes_list.append((stripe_record.stripe_id, stripe_record.stripe_name))
        response = HttpResponse(status=204)
        events = {
            "update_stripes_list": {
                "stripes_list": stripes_list
            },
        }
        response["HX-Trigger"] = json.dumps(events)
        return response
    except Exception as ex:
        return getRankExceptionResponse(ex)

# --------------------------------------------------------------------
# Display the rank required dialog form
# --------------------------------------------------------------------
def show_required_ranks(request):
    print(f'show_required_ranks was invoked')
    try:
        response_error_type = "response_error_type"
        if 'badgeNumber' not in request.POST:
            return getResponseEvents(response_error_type, "error", "Badge number is required!")
        if not request.POST['badgeNumber']:
            return getResponseEvents(response_error_type, "error", "Badge number is required!")
        if not request.POST['badgeNumber'].isdigit():
            return getResponseEvents(response_error_type, "error", "Badge number must be all digits!")

        student    = Students.objects.filter(badge_number=request.POST['badgeNumber'])
        if len(student) == 0: return getResponseEvents(response_error_type, "error", "Student record not found!")
        if len(student) >  1: return getResponseEvents(response_error_type, "error", "Multiple student records found!")

        student_record  = student[0]
        initial_rank_data = {
            'badge_number'       : student_record.badge_number,
            'student_name'       : f'{student_record.first_name} {student_record.last_name}',
            'current_rank_num'   : student_record.current_rank_num,
            'current_rank_name'  : student_record.current_rank_name,
            'current_stripe_id'  : student_record.current_stripe_id,
            'current_stripe_name': student_record.current_stripe_name,
        }
        form = RequiredRanks(initial_rank_data=initial_rank_data)
        response = render(request, 'modal_rank_required.html', {'form': form})
        response['HX-Trigger']  = 'show_rank_required'
        response['HX-Retarget'] = '#modal_rank_required'
        response['HX-Reswap']   = 'outerHTML'
        response['HX-Trigger-After-Settle'] = 'show_rank_required_dialog'
        return response

    except Exception as ex:
        return getRankExceptionResponse(ex)

# --------------------------------------------------------------------
def update_required_rank(request):
    try:
        print(f'update_required_rank was invoked')
        response_destination = 'modal_rank_required_response'
        badge_number  = request.POST['badge_number']
        if 'required_ranks' not in request.POST:
            return getResponseEvents(response_destination, "error", "Please select a belt rank!")

        if 'required_stripes' not in request.POST:
            return getResponseEvents(response_destination, "error", "Please select a stipe level!")

        # check for valid badge format
        if not badge_number:           return getResponseEvents(response_destination, "error", "Badge number can not be blank!")
        if not badge_number.isdigit(): return getResponseEvents(response_destination, "error", "Badge number must be all digits!")

        # check the badge matches a student record
        student    = Students.objects.get(badge_number=badge_number)
        if not student: return getResponseEvents(response_destination, "error", "Student record not found!")

        # check the belt exists
        selected_belt_id  = request.POST['required_ranks']
        belts_list = Belts.objects.filter(belt_id=selected_belt_id)
        if len(belts_list) == 0: return getResponseEvents(response_destination, "error", "Belt record was not found!")
        if len(belts_list) > 1: return getResponseEvents(response_destination, "error", "Multiple belt records found!")
        belt_record = belts_list[0]

        # check the stripe exists and is valid for the belt
        selected_stripe_id  = request.POST['required_stripes']
        stripes_list = Stripes.objects.filter(stripe_id=selected_stripe_id)
        if len(stripes_list) == 0: return getResponseEvents(response_destination, "error", "Stripe record was not found!")
        if len(stripes_list) > 1: return getResponseEvents(response_destination, "error", "Multiple stripe records found!")
        stripe_record = stripes_list[0]

        if stripe_record.rank_num != int(selected_belt_id):
            return getResponseEvents(response_destination, "error", "Select stripe not valid for belt!")

        # update the student rank on the student record
        print(f'updating badge number:{badge_number} to {selected_belt_id} / {belt_record.belt_title}')
        student.current_rank_num    = int(selected_belt_id)
        student.current_rank_name   = belt_record.belt_title
        student.current_stripe_id   = int(stripe_record.stripe_id)
        student.current_stripe_name = stripe_record.stripe_name
        student.save()

        # insert into the promotions history
        insert_promotions_table(student, belt_record, stripe_record)

        return getRankUpdatedResponse(f"Rank was updated to {belt_record.belt_title} with {stripe_record.stripe_name}")
    except Exception as ex:
        print(str(ex))
        return getRankExceptionResponse(ex)

# --------------------------------------------------------------------
def insert_promotions_table(student_record, belt_record, stripe_record):
    promotion_record = Promotions()
    promotion_record.badge_number   = student_record.badge_number
    promotion_record.student_first_name   = student_record.first_name
    promotion_record.student_last_name    = student_record.last_name
    promotion_record.belt_id        = belt_record.belt_id
    promotion_record.belt_title     = belt_record.belt_title
    promotion_record.stripe_id      = stripe_record.stripe_id
    promotion_record.stripe_title   = stripe_record.stripe_name
    promotion_record.save()

# --------------------------------------------------------------------
# Process the checkin activity
# --------------------------------------------------------------------
def badge_checkin(request):
    print(f'badge_checkin was invoked')
    try:
        badgeNumber = request.POST["badgeNumber"]

        # check for valid badge format
        if not badgeNumber:           return getResponseEvents("error", "Badge number can not be blank!")
        if not badgeNumber.isdigit(): return getResponseEvents("error", "Badge number must be all digits!")

        # check the badge matches a student record
        student_records    = Students.objects.filter(badge_number=badgeNumber)
        if len(student_records) == 0: return getResponseEvents("error", "Student record not found!")
        if len(student_records) >  1: return getResponseEvents("error", "Multiple student records found!")
        student_record = student_records[0]

        # check if we should show the student rank/stripe required dialog
        rank_required = False
        if not student_record.current_rank_num:
            rank_required = True

        selected_class  = GetCurrentClass()
        insert_attendance_record(student_record, selected_class)

        response = HttpResponse(status=204)
        events = {
            "checkin_response": {
                "checkin_status"  : "success",
                "checkin_message" : f'{student_record.first_name} {student_record.last_name} was checked in.',
                "rank_required"   : True
            },
        }
        response['HX-Trigger'] = json.dumps(events)
        return response
    except Students.DoesNotExist:
        return getResponseEvents("error", "Student record not found!")


    except Exception as ex:
        print(str(ex))
        return getExceptionResponse(ex)

# --------------------------------------------------------------------
# Insert the attendance checkin record
# --------------------------------------------------------------------
def insert_attendance_record(student_record, class_record):
    currentTime     = datetime.now()
    checkinDateTime = currentTime.strftime("%Y-%m-%d %H:%M:%S")
    checkinDate     = currentTime.strftime("%m/%d/%Y")
    checkinTime     = currentTime.strftime("%I:%M %p")

    attendance_record = Attendance()
    attendance_record.badge_number       = student_record.badge_number
    attendance_record.checkin_datetime   = checkinDateTime
    attendance_record.checkin_date       = checkinDate
    attendance_record.checkin_time       = checkinTime

    attendance_record.student_first_name = student_record.first_name
    attendance_record.student_last_name  = student_record.last_name
    attendance_record.student_rank_num   = student_record.current_rank_num
    attendance_record.student_rank_name  = student_record.current_rank_name
    attendance_record.student_stripe_id  = student_record.current_stripe_id
    attendance_record.student_stripe_name = student_record.current_stripe_name
    if class_record:
        attendance_record.class_num          = class_record.class_num
        attendance_record.class_name         = class_record.class_name
        attendance_record.class_start_time   = class_record.class_start_time
        attendance_record.style_num          = class_record.style_num
        attendance_record.applies_promotion  = class_record.is_promotions
    attendance_record.save()

# --------------------------------------------------------------------
# Search for class within the start and stop times
# --------------------------------------------------------------------
def GetCurrentClass():
    ## day of week in db starts with Sunday = 0, ends with Saturday = 6
    ## add 1 to adjust for that
    today = datetime.now().date().weekday() + 1
    class_time = Classes.objects.filter(class_day_of_week=today).order_by('class_start_time')
    current_date = datetime.now()
    current_date_str = current_date.strftime("%m/%d/%Y")
    date_format = "%m/%d/%Y %I:%M %p"
    for class_record in class_time:
        checkin_start_str  = current_date_str + ' ' + class_record.class_start_time
        checkin_start_date = datetime.strptime(checkin_start_str, date_format)
        checkin_finis_str  = current_date_str + ' ' + class_record.class_finis_time
        checkin_finis_date = datetime.strptime(checkin_finis_str, date_format)
        if checkin_start_date <= current_date <= checkin_finis_date:
            return class_record
    return None

# -------------------------------------------------------
def getResponseEvents(
        event:   str = "checkin_response",
        status:  str = "success",
        message: str = ""):
    response = HttpResponse(status=204)
    events = {
        event: {
            "checkin_status": status,
            "checkin_message":message,
        },
    }
    response['HX-Trigger'] = json.dumps(events)
    return response

def getExceptionResponse(ex):
    response = HttpResponse(status=204)
    events = {
        "checkin_response": {
            "checkin_status": "error",
            "checkin_message": str(ex),
        },
    }
    response['HX-Trigger'] = json.dumps(events)
    return response

def getRankUpdatedResponse(message: str):
    response = HttpResponse(status=204)
    events = {
        "rank_update_response": {
            "rank_update_status": "success",
            "rank_update_message": message,
        },
    }
    response['HX-Trigger'] = json.dumps(events)
    return response


def getRankExceptionResponse(ex):
    response = HttpResponse(status=204)
    events = {
        "rank_update_response": {
            "rank_update_status": "error",
            "rank_update_message": str(ex),
        },
    }
    response['HX-Trigger'] = json.dumps(events)
    return response


