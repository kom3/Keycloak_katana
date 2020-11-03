from django.urls import path
from django.contrib import admin
from django.conf.urls import url, include
#from django.views.decorators.csrf import csrf_exempt
from katana.wapps.container import views

urlpatterns = [
    path('', views.HomePageView.as_view()),
    path('getNes/',views.getNes,name="getNes"),
    path('export_NE/',views.export_NE,name="export_NE"),
    path('addNE/',views.addNE,name="addNE"),
    path('editNE/',views.editNE,name="editNE"),
    path('csv_commit/',views.csv_commit,name="csv_commit"),
    path('deleteNE/',views.deleteNE,name="deleteNE"),
    path('OndemandBackup/',views.OndemandBackup,name="OndemandBackup"),
    path('filterNE/',views.filterNE,name="filterNE"),
    path('logNE/',views.logNE,name="logNE"),
    path('csv_validation/', views.csv_validation, name='csv_validation'),
    path('load_tid/', views.getTid, name='load_tid'),
    path('getNesQuickFilterCount/', views.getNesQuickFilterCount, name='getNesQuickFilterCount'),
]

