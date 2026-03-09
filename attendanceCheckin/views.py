import json

from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from datetime import datetime

from attendanceCheckin.forms import CheckinForm, RequiredRanks
from attendanceData.models import Students, Classes, Belts, BeltsByRank

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
        return render(request, 'belt_stripes.html', {'stripes_choices': stripes_queryset})
    except Exception as ex:
        return getRankExceptionResponse(ex)

# --------------------------------------------------------------------
# Display the rank required dialog form
# --------------------------------------------------------------------
def show_required_ranks(request):
    print(f'show_required_ranks was invoked')
    try:
        if 'badgeNumber' not in request.POST:
            return getResponseEvents("rank_required_response", "error", "Badge number is required!")
        if not request.POST['badgeNumber']:
            return getResponseEvents("rank_required_response", "error", "Badge number is required!")

        student    = Students.objects.filter(badge_number=request.POST['badgeNumber'])
        if len(student) == 0: return getResponseEvents("rank_required_response", "error", "Student record not found!")
        if len(student) >  1: return getResponseEvents("rank_required_response", "error", "Multiple student records found!")

        student_record  = student[0]
        stripes_query = f'select * from vw_stripes_by_belt_id where  rankNum = {student_record.current_rank_num}'
        stripes_queryset = BeltsByRank.objects.raw(stripes_query)

        stripes_list = []
        for stripe_record in stripes_queryset:
            stripes_list.append((stripe_record.stripe_id, stripe_record.stripe_name))

        initial_rank_data = {
            'badge_number'       : student_record.badge_number,
            'student_name'       : f'{student_record.first_name} {student_record.last_name}',
            'current_rank_num'   : student_record.current_rank_num,
            'current_rank_name'  : student_record.current_rank_name,
            'current_stripe_id'  : student_record.current_stripe_id,
            'current_stripe_name': student_record.current_stripe_name,
            'required_stripes'   : stripes_queryset
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
        badge_number  = request.POST['badge_number']
        student_rank  = request.POST['required_ranks']
        stripe_count  = request.POST['required_stripes']

        # check for valid badge format
        if not badge_number:           return getResponseEvents("error", "Badge number can not be blank!")
        if not badge_number.isdigit(): return getResponseEvents("error", "Badge number must be all digits!")

        # check the badge matches a student record
        #student    = Students.objects.filter(badge_number=badge_number).first()
        student    = Students.objects.get(badge_number=badge_number)
        if not student: return getResponseEvents("error", "Student record not found!")

        # check the belt exists
        belts_list = Belts.objects.filter(belt_id=student_rank)
        if len(belts_list) == 0: return getResponseEvents("error", "Belt record was not found!")
        if len(belts_list) > 1: return getResponseEvents("error", "Multiple belt records found!")
        belt_record = belts_list[0]

        print(f'updating badge number:{badge_number} to {student_rank} / {belt_record.belt_title}')

        student.current_rank_num  = int(student_rank)
        student.current_rank_name = belt_record.belt_title
        student.save()
        #student.save(update_fields=['currentRankNum', 'currentRankName'])

# '''
# --currentRankNum     INTEGER,
# --currentRankName    TEXT,
# --currentStripeId    INTEGER,
# --currentStripeName  TEXT
# '''


        return getRankUpdatedResponse(f"Rank was updated to {belt_record.belt_title}")
    except Exception as ex:
        return getRankExceptionResponse(ex)

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
        student    = Students.objects.using('attendance_db').filter(badge_number=badgeNumber)
        if len(student) == 0: return getResponseEvents("error", "Student record not found!")
        if len(student) >  1: return getResponseEvents("error", "Multiple student records found!")

        # check if we should show the student rank/stripe required dialog
        rank_required = False
        if not student[0].current_rank_num:
            rank_required = True

        # check if we currently within a checkin window
        # crnt_class = Classes.objects.using('attendance_db').get(badge_number=badgeNumber)

        ## day of week in db starts with Sunday = 0, ends with Saturday = 6
        ## add 1 to adjust for that
        today = datetime.now().date().weekday() + 1

        checkin_times = Classes.objects.using('attendance_db').filter(class_day_of_week = today)
        for checkin_time in checkin_times:
            print(f'checkin_time: {checkin_time.class_num}:{checkin_time.class_display_title} - {checkin_time.check_in_start} <> {checkin_time.check_in_finis}')

        response = HttpResponse(status=204)
        events = {
            "checkin_response": {
                "checkin_status"  : "success",
                "checkin_message" : f'{student[0].first_name} {student[0].last_name} was checked in.',
                "rank_required"   : True
            },
        }
        response['HX-Trigger'] = json.dumps(events)
        return response
    except Students.DoesNotExist:
        return getResponseEvents("error", "Student record not found!")


    except Exception as ex:
        return getExceptionResponse(ex)


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


