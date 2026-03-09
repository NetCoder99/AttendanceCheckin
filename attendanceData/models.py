from datetime import datetime

from django.db import models

# Create your models here.
from django.db import models

class Students(models.Model):
    badge_number = models.AutoField(db_column='badgeNumber', primary_key=True)  # Field name made lowercase.
    first_name = models.TextField(db_column='firstName', blank=True, null=True)  # Field name made lowercase.
    last_name = models.TextField(db_column='lastName', blank=True, null=True)  # Field name made lowercase.
    name_prefix = models.TextField(db_column='namePrefix', blank=True, null=True)  # Field name made lowercase.
    email = models.TextField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    address2 = models.TextField(blank=True, null=True)
    city = models.TextField(blank=True, null=True)
    country = models.TextField(blank=True, null=True)
    state = models.TextField(blank=True, null=True)
    zip = models.TextField(blank=True, null=True)
    birthdate = models.TextField(db_column='birthDate', blank=True, null=True)  # Field name made lowercase.
    phone_home = models.TextField(db_column='phoneHome', blank=True, null=True)  # Field name made lowercase.
    phone_mobile = models.TextField(db_column='phoneMobile', blank=True, null=True)  # Field name made lowercase.
    status = models.TextField(blank=True, null=True)
    member_since = models.TextField(db_column='memberSince', blank=True, null=True)  # Field name made lowercase.
    ethnicity = models.TextField(blank=True, null=True)
    student_image_bytes = models.BinaryField(db_column='studentImageBytes', blank=True, null=True)  # Field name made lowercase.
    student_image_path = models.TextField(db_column='studentImagePath', blank=True, null=True)  # Field name made lowercase.
    student_image_base64 = models.TextField(db_column='studentImageBase64', blank=True, null=True)  # Field name made lowercase.
    middle_name = models.TextField(db_column='middleName', blank=True, null=True)  # Field name made lowercase.
    student_image_name = models.TextField(db_column='studentImageName', blank=True, null=True)  # Field name made lowercase.
    student_image_type = models.TextField(db_column='studentImageType', blank=True, null=True)  # Field name made lowercase.
    current_rank_num = models.IntegerField(db_column='currentRankNum', blank=True, null=True)  # Field name made lowercase.
    current_rank_name = models.TextField(db_column='currentRankName', blank=True, null=True)  # Field name made lowercase.
    current_stripe_id = models.IntegerField(db_column='currentStripeId', blank=True, null=True)  # Field name made lowercase.
    current_stripe_name = models.TextField(db_column='currentStripeName', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'students'

class ClassesAbstract(models.Model):
    class_num = models.AutoField(db_column='classNum', primary_key=True)  # Field name made lowercase.
    class_name = models.TextField(db_column='className', blank=True, null=True)  # Field name made lowercase.
    style_num = models.IntegerField(db_column='styleNum', blank=True, null=True)  # Field name made lowercase.
    style_name = models.TextField(db_column='styleName', blank=True, null=True)  # Field name made lowercase.
    class_day_of_week = models.IntegerField(db_column='classDayOfWeek', blank=True, null=True)  # Field name made lowercase.
    class_start_time = models.TextField(db_column='classStartTime', blank=True, null=True)  # Field name made lowercase.
    class_finis_time = models.TextField(db_column='classFinisTime', blank=True, null=True)  # Field name made lowercase.
    class_duration = models.IntegerField(db_column='classDuration', blank=True, null=True)  # Field name made lowercase.
    allowed_ranks = models.TextField(db_column='allowedRanks', blank=True, null=True)  # Field name made lowercase.
    class_display_title = models.IntegerField(db_column='classDisplayTitle', blank=True, null=True)  # Field name made lowercase.
    allowed_ages = models.TextField(db_column='allowedAges', blank=True, null=True)  # Field name made lowercase.
    class_check_in_start = models.TextField(db_column='classCheckinStart', blank=True, null=True)  # Field name made lowercase.
    class_check_in_finis = models.TextField(db_column='classCheckInFinis', blank=True, null=True)  # Field name made lowercase.
    is_promotions = models.TextField(db_column='isPromotions', blank=True, null=True)  # Field name made lowercase.

    @property
    def check_in_start(self):
        if self.class_check_in_start:
            return datetime.strptime(str(self.class_check_in_start), "%H.%M").time()
        return None

    @property
    def check_in_finis(self):
        if self.class_check_in_finis:
            return datetime.strptime(str(self.class_check_in_finis), "%H.%M").time()
        return None

    class Meta:
        abstract = True
        managed  = False
        db_table = 'classes'

class Classes(ClassesAbstract):
    pass

class Belts(models.Model):
    belt_id = models.AutoField(db_column='beltId', primary_key=True)  # Field name made lowercase.
    belt_title = models.TextField(db_column='beltTitle', unique=True, blank=True, null=True)  # Field name made lowercase.
    stripe_title = models.TextField(db_column='stripeTitle', blank=True, null=True)  # Field name made lowercase.
    class_count = models.IntegerField(db_column='classCount', blank=True, null=True)  # Field name made lowercase.
    image_source = models.TextField(db_column='imageSource', blank=True, null=True)  # Field name made lowercase.
    stripe_count = models.IntegerField(db_column='stripeCount', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'belts'

class BeltsByRank(models.Model):
    stripe_id     = models.IntegerField (db_column='stripeId',     primary_key=True)
    stripe_name   = models.TextField    (db_column='stripeName',   blank=True, null=True)
    rank_num      = models.IntegerField (db_column='rankNum',      blank=True, null=True)
    seq_num       = models.IntegerField (db_column='seqNum',       blank=True, null=True)
    class_count   = models.IntegerField (db_column='classCount',   blank=True, null=True)
    next_stripe   = models.IntegerField (db_column='nextStripeCount', blank=True, null=True)
    belt_title    = models.TextField    (db_column='beltTitle',   blank=True, null=True)
    max_seq_num   = models.IntegerField (db_column='maxSeqNum',   blank=True, null=True)
    last_stripe_flag   = models.IntegerField(db_column='lastStripeFlag', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'vw_stripes_by_belt_id'
