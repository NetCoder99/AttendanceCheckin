# --------------------------------------------------------------------
from flask import render_template
from flask_htmx import make_response

from models.models import Students, Classes


def getCheckinPanel(
        status: str,
        message: str,
        student_image_url: str,
        student_record: Students,
        other_message: str,
        promotion_message: str
):
    try:
        alert_class    = "text-danger" if status == 'error' else ""
        checkin_message  = f'{student_record.firstName} {student_record.lastName} {message}'

        badge_message = render_template(
            "partials/checkin_response_panel.html",
            alert_class       = alert_class,
            badge_message_str = message,
            checkinMessage    = checkin_message,
            promotionMessage  = promotion_message,
            otherMessage      = other_message,
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

