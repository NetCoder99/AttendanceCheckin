from django.urls import path

from attendanceCheckin import views

urlpatterns = [
    path('',      views.checkin_student, name='checkin_student'),
    path('get_stripes', views.get_stripes, name='get_stripes'),
    path('checkin_student/',      views.checkin_student, name='checkin_student'),
    path('badge_checkin/',        views.badge_checkin, name='badge_checkin'),
    path('show_required_ranks/',  views.show_required_ranks, name='show_required_ranks'),
    path('update_required_rank/', views.update_required_rank, name='update_required_rank'),
]
