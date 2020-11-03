from django.urls import path
from django.contrib import admin
from django.conf.urls import url, include
#from . import views
from katana.wapps.container import views
#from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('', views.HomePageView.as_view()),
    path('nePerModel_getAll/', views.nePerModel_getAll, name="nePerModel_getAll"),
    path('globalFTTD/', views.globalFTTD, name='globalFTTD'),
    path('synConfigPath/', views.synConfigPath, name='synConfigPath'),
    path('saveGlobalNeCreds/',views.saveGlobalNeCreds,name="saveGlobalNeCreds"),
    path('getGlobalNeCreds/',views.getGlobalNeCreds,name="getGlobalNeCreds"),
    path('getSFTPData/',views.getSFTPData,name="getSFTPData"),
    path('postSFTPData/',views.postSFTPData,name="postSFTPData"),
    path('savePerVendorConfiguration/',views.savePerVendorConfiguration,name="savePerVendorConfiguration"),
    path('fetchGlobalFileConfigs/',views.fetchGlobalFileConfigs,name="fetchGlobalFileConfigs"),
    path('saveGlobalFileCreditinals/',views.saveGlobalFileCreditinals,name="saveGlobalFileCreditinals"),
    path('getGlobalThresholdSettings/', views.getGlobalThresholdSettings, name="getGlobalThresholdSettings"),
    path('postGlobalThresholdSettings/',views.postGlobalThresholdSettings, name="postGlobalThresholdSettings"),
    path('getSubscribersEmail/', views.getSubscribersEmail, name="getSubscribersEmail"),
    path('postSubscribersEmail/', views.postSubscribersEmail, name="postSubscribersEmail"),
    path('getPerVendorFTTD/',views.getPerVendorFTTD,name='getPerVendorFTTD'),
    path('savePerVendorFTTD/',views.savePerVendorFTTD,name='savePerVendorFTTD'),
    path('fttd_Delete/',views.fttd_Delete, name="fttd_Delete"),
    path('postEmailReportData/',views.postEmailReportData, name="postEmailReportData")

]
