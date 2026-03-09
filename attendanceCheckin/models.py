from django.db import models

##class StudentRecord(models.Model):

class CheckinStudentRecords(models.Model):
    badgeNumber = models.AutoField(db_column='badgeNumber', primary_key=True)
    firstName   = models.TextField(db_column='firstName',   blank=True, null=True)
    lastName    = models.TextField(db_column='lastName',    blank=True, null=True)
    status      = models.TextField(db_column='status',      blank=True, null=True)
    classNum    = models.IntegerField(db_column='classNum',  blank=True, null=True)
    studentImageBase64 = models.TextField(db_column='studentImageBase64', blank=True, null=True)
    studentImageField  = models.ImageField(
        db_column='studentImageField',
        default="rising-sun-martial-arts-logo.jpg",
        blank=True,
        null=True,
        upload_to="images/",
        max_length=512
    )

    class Meta:
        managed = True
        db_table = 'studentCheckins'

