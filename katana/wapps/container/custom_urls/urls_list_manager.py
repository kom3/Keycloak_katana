from django.urls import path
from django.contrib import admin
from django.conf.urls import url, include
#from . import views
from katana.wapps.container import views

#from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('', views.HomePageView.as_view()),
    path('list/', views.HomePageView.as_view()),
    path('nes/', views.getAPIdata, name='getAPIdata'),
    path('deleteList/', views.deleteListAPI, name='deleteListAPI'),
    path('createList/', views.createListAPI, name='createListAPI'),
    path('getListAllLists/',views.getListAllLists,name='getListAllLists'),
    path('getNesForSelectedList/', views.getNesForSelectedList, name='getNesForSelectedList'),
    path('retrieveAllLists/', views.retrieveAllLists, name='retrieveAllLists'),
    path('modifyList/', views.modifyList, name='modifyList'),
    path('retrieveList/', views.retrieveList, name='retrieveList'),
    path('addNEToList/',views.addNEToListAPI,name='addNEToListAPI'),
    path('getNesForSelectedList/',views.getNesForSelectedList,name='getNesForSelectedList'),
    path('lastRunInfo/',views.lastRunInfo,name='lastRunInfo'),

]
