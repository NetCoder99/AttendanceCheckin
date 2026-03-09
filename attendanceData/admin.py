from django.contrib import admin

from attendanceData.models import Students, Classes, Belts

admin.site.register(Students)
admin.site.register(Classes)
admin.site.register(Belts)

# Register your models here.
