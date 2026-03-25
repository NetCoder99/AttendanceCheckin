from flask import render_template, request
from flask_htmx import make_response

from classes.sqlite_procs import getDbSession
from models import Belts, Stripes, Students, Promotions, Attendance, VwEligibilityCounts
from datetime import datetime
from sqlalchemy import select, literal, func

# ------------------------------------------------------------------------------------------
db_session = getDbSession()


# --------------------------------------------------------------------
# called from routes, help to encapsulate functionality
# --------------------------------------------------------------------
def get_stripes_func():
    selected_rank = request.args['id_required_ranks']
    stripes_list = getStripesForBelt(int(selected_rank))

    if selected_rank == '0':
        stripes_list = [("0", '-- Select a stripe --')]
    else:
        stripes_stmt = select(Stripes.stripeId, Stripes.stripeName).where(Stripes.rankNum == selected_rank)
        stripes_rows = db_session.execute(stripes_stmt).fetchall()
        stripes_list_db = [tuple(row) for row in stripes_rows]
        stripes_empty = [("0", '-- Select a stripe --')]
        stripes_list = stripes_empty + stripes_list_db

    belt_stripes = render_template(
        "partials/belt_stripes.html",
        stripes_list=stripes_list,
    )
    response = make_response(belt_stripes)
    return response

# --------------------------------------------------------------------
def show_student_ranks_func():
    print(f'show_student_ranks_func was invoked')
    # check the badge number is reasonable
    badge_number = ''
    if 'badgeNumber' in request.args:
        badge_number = request.args['badgeNumber']
    elif  'badgeNumber' in request.form:
        badge_number = request.form['badgeNumber']
    if not badge_number:
        return getBadgeMessage("error", "Badge number is required!")
    # if 'badgeNumber' not in request.args:
    #     return getBadgeMessage("error", "Badge number is required!")
    # if not request.args['badgeNumber']:
    #     return getBadgeMessage("error", "Badge number is required!")


    if not badge_number.isdigit():
        return getBadgeMessage("error", "Badge number must be all digits!")

    # ensure the student exists
    student_record = db_session.query(Students).filter_by(badgeNumber=badge_number).first()
    if not student_record: return getBadgeMessage("error", "Student record not found!")

    # fetch the belts / ranks for the dropdown
    belts_stmt = select(Belts.beltId, Belts.beltTitle, literal("").label("selected")).order_by(Belts.beltId)
    belts_rows = db_session.execute(belts_stmt).fetchall()
    belts_list_db = [tuple(row) for row in belts_rows]
    belt_empty = [("0", '-- Select a belt --')]
    belts_list = belt_empty + belts_list_db

    # if there is no assigned rank then pick the closest belt and stripe
    class_count_stmt = select(func.count()).where(Attendance.badgeNumber == student_record.badgeNumber)
    student_class_count = db_session.scalar(class_count_stmt)
    eligibility_records = (db_session
                           .query(VwEligibilityCounts)
                           .where(VwEligibilityCounts.eligibleCount <= student_class_count)
                           .order_by(VwEligibilityCounts.rowNum.desc())
                           .first())

    # pick, or guess, the student belt and stripe
    if not student_record.currentRankNum:
        student_record.currentRankNum = eligibility_records.beltId
    stripes_list = getStripesForBelt(student_record.currentRankNum)

    # render the modal form
    modal_rank = render_template(
        "partials/modal_rank.html",
        badge_number=student_record.badgeNumber,
        student_name=f'{student_record.firstName} {student_record.lastName}',
        belts_list=belts_list,
        stripes_list=stripes_list,
        current_rank_num=student_record.currentRankNum,
        current_stripe_id=student_record.currentStripeId,
    )

    # tell the ui to show the modal
    response = make_response(modal_rank)
    response.headers['HX-Retarget'] = '#modal-container'
    response.headers['HX-Reswap'] = 'innerHTML'
    response.headers['HX-Trigger-After-Settle'] = 'show_rank_required_dialog'
    return response

def update_required_rank_func():
    print(f'update_required_rank was invoked')
    badge_number = request.form['badge_number']
    # check for valid badge format
    if not badge_number:           return getRanksMessage("error", "Badge number can not be blank!")
    if not badge_number.isdigit(): return getRanksMessage("error", "Badge number must be all digits!")

    # ensure the student exists
    student_record = db_session.query(Students).filter_by(badgeNumber=badge_number).first()
    if not student_record: return getRanksMessage("error", "Student record not found!")

    # reset rank and stripes to null, mostly for testing gui behaviour
    selected_rank_id = request.form['id_required_ranks']
    if selected_rank_id == '0':
        reset_student_rank(student_record)
        return getRanksMessage('success', f"Rank was reset to nulls")

    # valid belt was selected, check the belt exists, etc...
    selected_stripe_id = request.form['id_required_stripes']
    if selected_stripe_id == '0':
        reset_student_rank(student_record)
        return getRanksMessage('error', "Please select a stripe!")

    belt_record = db_session.query(Belts).filter_by(beltId=selected_rank_id).first()
    if not belt_record: return getRanksMessage("error", "Belt record not found!")
    stripe_record = db_session.query(Stripes).filter_by(stripeId=selected_stripe_id).first()
    if not stripe_record: return getRanksMessage("error", "Stripe record not found!")

    update_student_rank(student_record, belt_record, stripe_record)
    return getRanksMessage('completed', 'Student rank was updated!')


# --------------------------------------------------------------------
# Various htmx response helpers
# --------------------------------------------------------------------
def getBadgeMessage(status, message):
    alert_class = "text-danger" if status == 'error' else "text-success"
    badge_message = render_template(
        "partials/badgeMessage.html",
        alert_class=alert_class,
        badge_message_str = message
    )
    response = make_response(badge_message)
    response.headers['HX-Retarget'] = '#badgeMessage'  # CSS Selector
    response.headers['HX-Trigger-After-Settle'] = 'show_ranks_error'
    return response

# -------------------------------------------------------
def getRanksMessage(status, message):
    alert_class = "text-danger" if status == 'error' else "text-success"
    html_snippet = f'<h5 id="rank_update_message" class="{alert_class} fw-bold text-center mb-3">{message}</h5>'
    response = make_response(html_snippet)
    response.headers['HX-Trigger'] = f'ranks_response_{status}'  # CSS Selector
    return response


# --------------------------------------------------------------------
# Misc rank / db get and update functions
# --------------------------------------------------------------------
def getStripesForBelt(beltId: int):
    stripes_stmt = select(Stripes.stripeId, Stripes.stripeName).where(Stripes.rankNum == beltId).order_by(Stripes.seqNum)
    stripes_rows = db_session.execute(stripes_stmt).fetchall()
    return [tuple(row) for row in stripes_rows]

def reset_student_rank(student_record: Students):
    print(f'resetting student rank for badge_number: {student_record.badgeNumber}')
    student_record.currentRankNum     = None
    student_record.currentRankName    = None
    student_record.currentStripeId    = None
    student_record.currentStripeName  = None
    belt_record = Belts()
    stripe_record = Stripes()
    db_session.commit()
    insert_promotions_table(student_record, belt_record, stripe_record, "Rank was reset")


def update_student_rank(student_record: Students, belt_record: Belts, stripe_record: Stripes):
    print(f'updating badge number:{student_record.badgeNumber} to {belt_record.beltId} / {belt_record.beltTitle}')
    student_record.currentRankNum    = belt_record.beltId
    student_record.currentRankName   = belt_record.beltTitle
    student_record.currentStripeId   = stripe_record.stripeId
    student_record.currentStripeName = stripe_record.stripeName
    db_session.commit()
    insert_promotions_table(student_record, belt_record, stripe_record, "Rank was updated")


def insert_promotions_table(student_record, belt_record, stripe_record, comments: str = "Promotion"):
    promotion_record = Promotions()
    promotion_record.badgeNumber      = student_record.badgeNumber
    promotion_record.studentFirstName = student_record.firstName
    promotion_record.studentLastName  = student_record.lastName
    promotion_record.beltId           = belt_record.beltId
    promotion_record.beltTitle        = belt_record.beltTitle
    promotion_record.stripeId         = stripe_record.stripeId
    promotion_record.stripeTitle      = stripe_record.stripeName
    promotion_record.promotionDate    = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    promotion_record.comments         = comments
    db_session.add(promotion_record)
    db_session.commit()
