from django.urls import path

from attendanceBelts import views

urlpatterns = [
    path('get_belts', views.get_belts, name='get_belts'),
]
