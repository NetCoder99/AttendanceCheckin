import json

from django.http import HttpResponse
from django.shortcuts import render

# --------------------------------------------------------------------
# Fetch the initial belts / ranks page
# --------------------------------------------------------------------
def get_belts(request):
    try:
        print(f'checkin_student was invoked')
        context = {
            'title': 'Belts / Ranks Maintenance',
        }
        return render(request, 'belts_main.html', context)
    except Exception as ex:
        print(str(ex))
        return getExceptionResponse(ex)



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
