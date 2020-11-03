from django.shortcuts import render
import requests
from requests.auth import HTTPBasicAuth
from django.http import HttpResponse, JsonResponse
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
from threading import Thread
import ast
import os
import time
import re
from cryptography.fernet import Fernet


config_settings_dns = '167.254.204.73' #'file-manager-svc.jx-ms-file-management-pr-jenkinsbuild'  #'db-backup-ne-mgmt-svc.list-manager'
config_pod = '30199' #'8004'
file_mgmt_dns = 'file-manager-svc.jx-ms-file-management-pr-jenkinsbuild'
file_pod = '8004'

headers = {'content-type': 'application/json'}

keyString = os.environ.get('CRYPTO_KEY')
if keyString is not None:
    key = bytes(os.environ.get('CRYPTO_KEY').strip(), 'utf-8')
    encrypter = Fernet(key)


class HomePageView(TemplateView):
    def get(self, request, **kwargs):
        return render(request, 'container/index.html', context=None)

def nePerModel_getAll(request):
    print('http://' + config_settings_dns + ':' + config_pod + '/api/config-management/v2/config/per-vendor/all/NE')
    try:
        res = requests.get('http://' + config_settings_dns + ':' + config_pod + '/api/config-management/v2/config/per-vendor/all/NE', auth=HTTPBasicAuth('fujitsu', 'fujitsu'))
        if res.status_code == 200:
            response = res.json()
            context = {'status':'success','data':response}
        else:
            context ={'status':'fail'}
    except:
        context = { 'status' :'fail with exception'}
    finally:
        return JsonResponse(context)


@csrf_exempt
def globalFTTD(request):
    if request.method == 'POST':
        buf = request.body.decode('utf-8')
        res = json.loads(buf)
        user = res["user"]
        print(user)
        passw =  res["pass"]
        passw= encrypter.encrypt(bytes(passw,'utf-8')).decode("utf-8")
        posts = {
                    "access_level": "GLOBAL",
                    
                    "config_data_type": "FTTD",
                    "data": {                   
                            "fttd_user":user ,
                            "fttd_passwd":passw
                            },
        }
    print(posts)
    headers = {'content-type': 'application/json'}
    print('http://'+config_settings_dns+':'+config_pod+'/api/config-management/v1/config/global/')
    try: 
          req = requests.post('http://'+config_settings_dns+':'+config_pod+'/api/config-management/v1/config/global/',data=json.dumps(posts), headers = headers, auth=HTTPBasicAuth('fujitsu', 'fujitsu'))
    except:
          context = { 'response': 'API Failed to fetch data' ,'status': 'failed'}
          return HttpResponse(json.dumps(context))
    if req.status_code == 200:
          globalfttd = json.loads(req.text)
          context = { 'results': globalfttd ,'status': 'success'}
    else:
        json_content = json.loads(req.text)
        context = { 'results': json_content["message"],'status':'fail' }
    return HttpResponse(json.dumps(context))

#syncpath
def synConfigPath(request):
      errorMessage = ''
      print('http://'+config_settings_dns+':'+config_pod+'/api/config-management/v1/config/global/SYNCNE')
      try: 
          req = requests.get('http://'+config_settings_dns+':'+config_pod+'/api/config-management/v1/config/global/SYNCNE', auth=HTTPBasicAuth('fujitsu', 'fujitsu'))
      except Exception as exc:
          context = { 'response': 'API Failed to fetch data' ,'status': 'failed', 'exce':exc}
          return HttpResponse(json.dumps(context))
      if req.status_code == 200:
          synconfigpath = json.loads(req.text)
          context = { 'results': synconfigpath ,'status': 'success','errMessage':errorMessage}
      elif req.status_code == 500:
          errorMessage = "Database service currently unavailable"
          context = { 'status': 'fail','errMessage':errorMessage}
      else:
          json_content = json.loads(req.text)
          context = { 'results': json_content["message"],'status':'fail','errMessage':errorMessage }
      return HttpResponse(json.dumps(context))

def getGlobalNeCreds(request):
    try:
        req = requests.get(
            'http://' + config_settings_dns + ':' + config_pod + '/api/config-management/v1/config/global/NE',auth=HTTPBasicAuth('fujitsu', 'fujitsu'))
    except Exception as e:
        context = {'globalNeCreditinals': 'API Failed to fetch data', 'status': 'fail'}
        return JsonResponse(context)
    if req.status_code == 200:
        if req.text.lower() == "GLOBAL NE was not configured".lower():
            globconfigsetdata = req.text
        else:
            globconfigsetdata = json.loads(req.text)
        context = {'results': globconfigsetdata, 'status': 'success'}
    else:
        json_content = json.loads(req.text)
        context = {'results': json_content["message"], 'status': 'fail'}
    return JsonResponse(context)


@csrf_exempt
def saveGlobalNeCreds(request):
    try:
        if request.method == 'POST':
            req_body = request.body.decode('utf-8')
            data = json.loads(req_body)
            user_id = data["user_id"]
            passwd = data["passwd"]
            passwd = encrypter.encrypt(bytes(passwd,'utf-8')).decode("utf-8")
            payload = {
                "access_level": "GLOBAL",
                "config_data_type": "NE",
                "data": {
                    "user_id": user_id,
                    "passwd": passwd,
                    # "conn_type":conn_type
                }
            }
            req = requests.post('http://' + config_settings_dns + ':' + config_pod + '/api/config-management/v1/config/global/',data=json.dumps(payload), headers=headers, auth=HTTPBasicAuth('fujitsu', 'fujitsu'))
            if req.status_code == 200:
                globconfigsetdata = json.loads(req.text)
                context = {'results': globconfigsetdata, 'status': 'success'}
            else:
                json_content = json.loads(req.text)
                context = {'results': json_content["message"], 'status': 'fail'}

        else:
            context = {'status':'fail','message':'You can not access this API over GET'}

    except Exception as e:
        context = {'status':'fail'}
    finally:
        return JsonResponse(context)

def getSFTPData(request):
    try:
        req = requests.get(
            'http://' + config_settings_dns + ':' + config_pod + '/api/config-management/v1/config/global/FTP',auth=HTTPBasicAuth('fujitsu', 'fujitsu'))
    except Exception as e:
        context = {'sftpData': 'API Failed to fetch data', 'status': 'fail'}
        return JsonResponse(context)
    if req.status_code == 200:
        sftpData = json.loads(req.text)
        context = {'result': sftpData, 'status': 'success'}
    else:
        json_content = json.loads(req.text)
        context = {'result': json_content["message"], 'status': 'fail'}
    return JsonResponse(context)

@csrf_exempt
def postSFTPData(request):
    try:
        if request.method == 'POST':
            req_body = request.body.decode('utf-8')
            data = json.loads(req_body)

            host = data["host"]
            user_id = data["user_id"]
            pawd = data["passwd"]
            passwd = encrypter.encrypt(bytes(pawd,'utf-8')).decode("utf-8")
            path = data["path"]

            payload = {
              "access_level": "GLOBAL",
              "config_data_type": "FTP",
              "data": {
                "host": host,
                "user_id": user_id,
                "passwd": passwd,
                "path": path
              },
            }
            req = requests.post('http://' + config_settings_dns + ':' + config_pod + '/api/config-management/v1/config/global/',data=json.dumps(payload), headers=headers, auth=HTTPBasicAuth('fujitsu', 'fujitsu'))
            if req.status_code == 200:
                sftpData = json.loads(req.text)
                context = {'result': sftpData, 'status': 'success'}
            else:
                json_content = json.loads(req.text)
                context = {'result': json_content["message"], 'status': 'fail'}

        else:
            context = {'status':'fail','message':'You can not access this API'}

    except Exception as e:
        context = {'status':'fail'}
    finally:
        return JsonResponse(context)

#savePerVendorConfiguration
@csrf_exempt
def savePerVendorConfiguration(request):
    buf = request.body.decode('utf-8')
    res = json.loads(buf)
    
    access_level = res["access_level"]
    config_data_type = res["config_data_type"]
    vendor = res["vendor"]
    model = res["model"]    
    conn_type = res["conn_type"]
    transfer_type = res["transfer_type"]
    file_sig = res["file_sig"]
    passwd = res["passwd"]
    user_id = res["user_id"]
    restore = res["restore"]
    
    print('http://' + config_settings_dns + ':' + config_pod + '/api/config-management/v1/config/per-vendor/NE/{0}/{1}'.format(vendor, model))
    try:
        req_sftp = requests.get('http://' + config_settings_dns + ':' + config_pod + '/api/config-management/v1/config/per-vendor/NE/{0}/{1}'.format(vendor, model), auth=HTTPBasicAuth('fujitsu', 'fujitsu'))
        if req_sftp.status_code == 200:
            json_content = req_sftp.json()
            sftp_flag = json_content["data"]["sftp"]
            ssh_flag = json_content["data"]["ssh"]
        else:
            context = {'response': 'API Failed to fetch data', 'status': 'failed'}
            return HttpResponse(json.dumps(context))
    except Exception as exc:
        context = {'response': 'API Failed with exception', 'status': 'failed', 'exception':exc}
        return HttpResponse(json.dumps(context))
    posts = {
            "access_level": access_level,
            "config_data_type": config_data_type,
            "data": {
                    "passwd":passwd,
                    "conn_type":conn_type,
                    "user_id":user_id ,
                    "sftp":sftp_flag,
                    "ssh":ssh_flag,
                    "transfer_type": transfer_type,
                    "file_sig": file_sig,
                    "restore":restore
                },
            "vendor":vendor,
            "model":model
        }
    print("post param is ----", posts)
    headers = {'content-type': 'application/json'}
    print('http://'+config_settings_dns+':'+config_pod+'/api/config-management/v1/config/per-vendor')
    try: 
        req = requests.post('http://'+config_settings_dns+':'+config_pod+'/api/config-management/v1/config/per-vendor',data=json.dumps(posts), headers = headers, auth=HTTPBasicAuth('fujitsu', 'fujitsu'))
    except Exception as exc:
        context = {'response': 'API Failed with exception', 'status': 'failed', 'exception':exc}
        return HttpResponse(json.dumps(context))
    if req.status_code == 200:
        pervendor = json.loads(req.text)
        context = { 'results': pervendor ,'status': 'success'}
    else:
        json_content = json.loads(req.text)
        context = { 'results': json_content["message"],'status':'fail' }
    return HttpResponse(json.dumps(context))

def getGlobalThresholdSettings(request):
    try:
        config_data_type = request.GET['configDataType']
        url = 'http://' + config_settings_dns + ':' + config_pod + '/api/config-management/v1/config/global/' + config_data_type
        req = requests.get(url, auth=HTTPBasicAuth('fujitsu', 'fujitsu'))
    except Exception as e:
        context = { 'status': 'fail', 'message': 'API Failed to fetch data' }
        return JsonResponse(context)
    if req.status_code == 200:
        ThresholdSettingsData = json.loads(req.text)
        context = { 'status': 'success', 'result': ThresholdSettingsData }
    else:
        json_content = json.loads(req.text)
        context = { 'status': 'fail', 'message': json_content["message"] }
    return JsonResponse(context)

@csrf_exempt
def postGlobalThresholdSettings(request):
    try:
        if request.method == 'POST':
            req_body = request.body.decode('utf-8')
            data = json.loads(req_body)
            headers = { "content-type": "application/json" }

            config_data_type = data["configDataType"]
            critical = data["critical"]
            major = data["major"]

            payload = {
                "access_level": "GLOBAL",
                "config_data_type": config_data_type,
                "data": {
                    "critical": critical,
                    "major": major,
                },
            }
            url = 'http://' + config_settings_dns + ':' + config_pod + '/api/config-management/v1/config/global'

            req = requests.post(url, data=json.dumps(payload), headers=headers, auth=HTTPBasicAuth('fujitsu', 'fujitsu'))

            if req.status_code == 200:
                ThresholdSettingsData = json.loads(req.text)
                context = { 'status': 'success', 'result': ThresholdSettingsData }
            else:
                json_content = json.loads(req.text)
                context = { 'status': 'fail', 'result': json_content["message"] }
        else:
            context = { 'status': 'fail', 'message': 'You can not access this API' }
    except Exception as e:
        context = { 'status': 'fail', 'message': 'API Failed with exception' }
    finally:
        return JsonResponse(context)

def getSubscribersEmail(request):
    try:
        config_data_type = 'SUBSCRIBERS'
        url = 'http://' + config_settings_dns + ':' + config_pod + '/api/config-management/v1/config/global/' + config_data_type
        req = requests.get(url, auth=HTTPBasicAuth('fujitsu', 'fujitsu'))
    except Exception as e:
        context = { 'status': 'fail', 'message': 'API Failed to fetch data' }
        return JsonResponse(context)
    if req.status_code == 200:
        SubscribersEmailData = json.loads(req.text)
        context = { 'status': 'success', 'result': SubscribersEmailData }
    else:
        json_content = json.loads(req.text)
        context = { 'status': 'fail', 'message': json_content["message"] }
    return JsonResponse(context)

@csrf_exempt
def postSubscribersEmail(request):
    try:
        if request.method == 'POST':
            req_body = request.body.decode('utf-8')
            data = json.loads(req_body)
            headers = { "content-type": "application/json" }

            email_ids = data["email_ids"]

            payload = {
                "access_level": "GLOBAL",
                "config_data_type": "SUBSCRIBERS",
                "data": {
                    "email_ids": email_ids,
                },
            }
            url = 'http://' + config_settings_dns + ':' + config_pod + '/api/config-management/v1/config/global'

            req = requests.post(url, data=json.dumps(payload), headers=headers, auth=HTTPBasicAuth('fujitsu', 'fujitsu'))

            if req.status_code == 200:
                SubscribersEmailData = json.loads(req.text)
                context = { 'status': 'success', 'result': SubscribersEmailData }
            else:
                json_content = json.loads(req.text)
                context = { 'status': 'fail', 'result': json_content["message"] }
        else:
            context = { 'status': 'fail', 'message': 'You can not access this API' }
    except Exception as e:
        context = { 'status': 'fail', 'message': 'API Failed with exception' }
    finally:
        return JsonResponse(context)

@csrf_exempt
def postEmailReportData(request):
    print("In postEmailReportData")
    try:
        if request.method == 'POST':
            req_body = request.body.decode('utf-8')
            data = json.loads(req_body)
            headers = { "content-type": "application/json" }

            email_enabled = data["emailEnabled"]
            recur_on = data["recuron"]
            report_date = data["reportDate"]
            report_day = data["reportDay"]
            report_subscribers = data["reportSubscribers"]
            report_types = data["reportTypes"]
            time_of_report = data["timeOfReport"]


            payload = {
                "access_level": "GLOBAL",
                "config_data_type": "EMAIL_REPORTS",
                "data": {
                    "day" : report_day,
                    "fromDate" : report_date,
                    "time" : time_of_report,
                    "notification" : email_enabled,
                    "recurOn" : recur_on,
                    "email_ids" : report_subscribers,
                    "reports" : report_types
                },
            }
            print("payload", payload)
            url = 'http://' + config_settings_dns + ':' + config_pod + '/api/config-management/v1/config/global'

            req = requests.post(url, data=json.dumps(payload), headers=headers, auth=HTTPBasicAuth('fujitsu', 'fujitsu'))

            if req.status_code == 200:
                EmailReportsData = json.loads(req.text)
                print("in IF")
                context = { 'status': 'success', 'result': EmailReportsData }
            else:
                json_content = json.loads(req.text)
                print("in Else")
                context = { 'status': 'fail', 'result': json_content["message"] }
        else:
            context = { 'status': 'fail', 'message': 'You can not access this API' }
    except Exception as e:
        context = { 'status': 'fail', 'message': 'API Failed with exception' , "exc" : e }
    finally:
        return JsonResponse(context)


def fetchGlobalFileConfigs(request):
    print('http://' + config_settings_dns + ':' + config_pod + '/api/config-management/v1/config/global/FILE_CONFIG')
    try:
        res = requests.get('http://' + config_settings_dns + ':' + config_pod + '/api/config-management/v1/config/global/FILE_CONFIG', auth=HTTPBasicAuth('fujitsu', 'fujitsu'))
        if res.status_code == 200:
            response = res.json()
            context = {'status':'success','data':response}
        else:
            context ={'status':'fail'}
    except Exception as exc:
        context = { 'status' :'fail with exception', "exc":exc}
    finally:
        return JsonResponse(context)

@csrf_exempt
def saveGlobalFileCreditinals(request):

    buf = request.body.decode('utf-8')
    res = json.loads(buf)

    access_level = res["access_level"]
    config_data_type = res["config_data_type"]
    backup_file_count = res["backup_file_count"]
    backup_zip_file_name = res["backup_zip_file_name"]
    file_size = res["file_size"]
    
    #conn_type=request.GET.get("conn_type")
    posts =  {
            "access_level": access_level,
            "config_data_type": config_data_type,
            "data": {
                "backup_file_count": backup_file_count,
                "backup_zip_file_name": backup_zip_file_name,
                "file_size": file_size
            }
        }

    print(posts)
            
    headers = {'content-type': 'application/json'}
    try: 
          req = requests.post('http://'+config_settings_dns+':'+config_pod+'/api/config-management/v1/config/global/',data=json.dumps(posts), headers = headers, auth=HTTPBasicAuth('fujitsu', 'fujitsu'))
    except:
          context = { 'response': 'API Failed to fetch data' ,'status': 'failed'}
          return HttpResponse(json.dumps(context))
    if req.status_code == 200:
          globconfigsetdata = json.loads(req.text)
          context = { 'results': globconfigsetdata ,'status': 'success'}
    else:
        json_content = json.loads("req.text")
        context = { 'results': json_content["message"],'status':'fail' }
    return HttpResponse(json.dumps(context))

#get pervendor fttd with pagination
def getPerVendorFTTD(request):
    try:
        res = requests.get('http://' + config_settings_dns + ':' + config_pod + '/api/config-management/v2/config/per-vendor/all/FTTD', auth=HTTPBasicAuth('fujitsu', 'fujitsu'))
        if res.status_code == 200:
            response = res.json()
            context = {'status':'success','data':response}
        else:
            context ={'status':'fail'}
    except Exception as e :
        print(e)
        context = { 'status' :'fail with exception'}
    finally:
        return JsonResponse(context)

#FTTD savePerVendorFTTD POST
@csrf_exempt
def savePerVendorFTTD(request):
    req_body = request.body.decode('utf-8')
    data = json.loads(req_body)
    access_level =data["access_level"]
    config_data_type=data["config_data_type"]
    vendor=data["vendor"]
    model=data["model"]
    fttd_user=data["fttd_user"]
    fttd_passwd=data["fttd_passwd"]
    print('indie save pervendor fttd passwd')
    # if  fttd_passwd is not None:
    #     fttd_passwd= encrypter.encrypt(bytes(fttd_passwd, "utf-8").decode("utf-8"))
    # else:
    #     fttd_passwd = None
    posts = {
                "access_level": access_level,
                "config_data_type": config_data_type,
                "data": {
                            "fttd_user":fttd_user ,
                            "fttd_passwd":fttd_passwd,
                        },
                        "vendor":vendor,
                        "model":model ,       
        }
    headers = {'content-type': 'application/json'}
    try: 
          req = requests.post('http://'+config_settings_dns+':'+config_pod+'/api/config-management/v1/config/per-vendor',data=json.dumps(posts), headers = headers, auth=HTTPBasicAuth('fujitsu', 'fujitsu'))
    except:
            context = { 'response': 'API Failed to fetch data' ,'status': 'failed'}
            return HttpResponse(json.dumps(context))
    if req.status_code == 200:
            pervendor = json.loads(req.text)
            context = { 'results': pervendor ,'status': 'success'}
    else:
        json_content = json.loads(req.text)
        context = { 'results': json_content["message"],'status':'fail' }
    return HttpResponse(json.dumps(context))

#DeleteFTTD
@csrf_exempt
def fttd_Delete(request):
    req_body = request.body.decode('utf-8')
    results = json.loads(req_body)
    access_level =results["access_level"]
    config_data_type=results["config_data_type"]
    vendor=results["vendor"]
    model=results["model"]
    headers = {'content-type': 'application/json'}
    try: 
          req = requests.delete('http://'+config_settings_dns+':'+config_pod+'/api/config-management/v1/config/per-vendor/FTTD/'+vendor+'/'+model,headers = headers, auth=HTTPBasicAuth('fujitsu', 'fujitsu'))
    except Exception as e:
          context = { 'response': 'API Failed to fetch data' ,'status': 'failed'}
          return HttpResponse(json.dumps(context))
    if req.status_code == 200:
          context = { 'results': "FTTD Deleted Sucessfully",'status': 'success'}
    else:
          json_content = json.loads(req.text)
          context = { 'results': "Failed to Delete",'status':'fail' }
    return HttpResponse(json.dumps(context))

