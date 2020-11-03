from django.urls import path
from django.contrib import admin
from django.conf.urls import url, include
from katana.wapps.container import views
#from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('', views.HomePageView.as_view()),
    path('getSchedules/',views.getSchedules,name='getSchedules'),
    path('getCalendarData/',views.getCalendarData,name='getCalendarData'),
    path('deleteSchedule/',views.deleteSchedule,name='deleteSchedule'),
    path('suspendSchedule/',views.suspendSchedule,name='suspendSchedule'),
    path('activeSchedule/',views.activeSchedule,name='activeSchedule'),
    path('runSchedule/',views.runSchedule,name='runSchedule'),
    path('createSchedule',views.createSchedule,name='createSchedule'),
    path('update_schedule',views.update_schedule,name='update_schedule'),
]
