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

ne_management_dns = '167.254.204.73'  #'db-backup-ne-mgmt-svc.list-manager'
ne_pod = '30195'
list_manager_dns = 'list-manager-svc.jx-ms-list-manager-pr-6' #'db-backup-list-manager-svc.list-manager'
list_pod = '8080'
schedule_dns = "scheduler-svc.jx-ms-scheduler-pr-6"
schedule_pod = "8002"
file_management_dns='65.49.80.216'
file_management_pod='8004'
report_dns = '65.49.80.216'
report_pod = '8005'
dashboard_dns = '167.254.204.73'
dashboard_pod = '8007'
tes_management_dns = '167.254.204.73'
tes_management_pod = '8003'
all_list_ids = []
allRegions = ['All', 'Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado', 'Connecticut',
              'District of Columbia', 'Delaware', 'Florida', 'Georgia', 'Hawaii', 'Idaho', 'Illinois', 'Indiana',
              'Iowa', 'Kansas', 'Kentucky', 'Louisiana', 'Maine', 'Maryland', 'Massachusetts', 'Michigan', 'Minnesota',
              'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire', 'New Jersey', 'New Mexico',
              'New York', 'North Carolina', 'North Dakota', 'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania',
              'Rhode Island', 'South Carolina', 'South Dakota', 'Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia',
              'Washington', 'West Virginia', 'Wisconsin', 'Wyoming', 'Other']
headers = {'content-type': 'application/json'}
keyString = os.environ.get('CRYPTO_KEY')
if keyString is not None:
    key = bytes(os.environ.get('CRYPTO_KEY').strip(), 'utf-8')
    encrypter = Fernet(key)

class HomePageView(TemplateView):
    def get(self, request, **kwargs):
        return render(request, 'container/index.html', context=None)

def getNes(request):
    try:
        res = requests.get('http://' + ne_management_dns + ':' + ne_pod + '/api/ne-management/v2/allnes',
                           auth=HTTPBasicAuth('fujitsu', 'fujitsu'))
        if res.status_code == 200:
            response = res.json()
            context = {'status':'success','data':response}
        else:
            context ={'status':'fail'}
    except:
        context = { 'status' :'fail'}
    finally:
        return JsonResponse(context)

@csrf_exempt
def OndemandBackup(request):
  try:
    if request.method == 'POST':
      buf = request.body.decode('utf-8')
      res = json.loads(buf)
      data = res["data"]
      inprogress =[]
      queued = []
      completed = []
      nodata = []
      final_data = []
      headers = {'content-type': 'application/json'}
      posts = {
        "tids":data,
        "operation_type": "NE_RESTORE" 
      }
      res = requests.post('http://'+tes_management_dns+':'+tes_management_pod+'/api/tes-management/v1/collection/get/getNEStatus',
                          data=json.dumps(posts), headers=headers, auth=HTTPBasicAuth('fujitsu', 'fujitsu'))
      if res.status_code == 200:
        response = res.json()
        inprogress =response["INPROGRESS"]
        queued = response["QUEUED"]
        completed = response["COMPLETED"]
        nodata = response["NODATA"]
        final_data = queued + completed + nodata
        if len(final_data) > 0:
            posts_sch={
                "backup_type": "DO_NEBACKUP",
                "data": [{
                "type":"NEs",
                "ids":final_data
                }],
                "job_status": "ACTIVE",
                "recur_on": "INSTANTLY",
                "schedule_day": "",
                "schedule_from": "",
                "schedule_name": "Instant OnDemand Backup",
                "schedule_status": "TRIGGERED",
                "schedule_to": ""
            }
            
            resp = requests.post('http://'+schedule_dns+':'+schedule_pod+'/api/scheduler/v1/schedule',
                                data=json.dumps(posts_sch), headers=headers, auth=HTTPBasicAuth('fujitsu', 'fujitsu'))
            if resp.status_code == 200:
                response = resp.json()
                context = {'status':'success','data':response,'inprogress':inprogress}
            else:
                context ={'status':'fail','data':'Internal Server Error'}
        else:
            context ={'status':'success','data':'No NEs left','inprogress':inprogress}
      else:
         context ={'status':'fail','data':'Internal Server Error'}   
  except Exception as e:
    print(e)
    context = { 'status' :'fail'}
  finally:
    return JsonResponse(context)

@csrf_exempt
def deleteNE(request):
  # delete_data = request.POST.get('data', "")
  buf = request.body.decode('utf-8')
  res = json.loads(buf)
  print("--------------delete ne response is-----------------------")
  print(res)
  delete_data = res["data"]
  data = ','.join(delete_data)

  print("--------------delete ne -----------------------")
  print(delete_data)
  print(data)
  headers = {'content-type': 'application/json'}
  print('http://'+ne_management_dns+':'+ne_pod+'/api/ne-management/v1/ne?tid='+data)
  
  try:
    res = requests.delete('http://'+ne_management_dns+':'+ne_pod+'/api/ne-management/v1/ne?tid='+data, headers = headers, auth=HTTPBasicAuth('fujitsu', 'fujitsu'))
    print(res)
    if res.status_code == 200:
      
      context = {'status':'success','data':"Successfully deleted NEs"}
    else:
      context ={'status':'fail','data':'Internal Server Error'}
  except Exception as e:
    print(e)
    context = { 'status' :'fail'}
  finally:
    return JsonResponse(context)

@csrf_exempt
def filterNE(request):
  
  buf = request.body.decode('utf-8')
  res = json.loads(buf)
  data = res["data"]
  print(type(data))
  print(data)
  headers = {'content-type': 'application/json'}  
  print('http://' + ne_management_dns + ':' + ne_pod + '/api/ne-management/v2/ne/filterby-nes?filterBy='+data+'&searchString='+"")
  

  try:
    res = requests.get('http://' + ne_management_dns + ':' + ne_pod + '/api/ne-management/v2/ne/filterby-nes?filterBy='+data+'&searchString='+"", headers = headers,auth=HTTPBasicAuth('fujitsu', 'fujitsu'))
    print(res)
    print(res.status_code)
    if res.status_code == 200:
      response = res.json()
      context = {'status':'success','data':response}
    else:
      context ={'status':'fail','data':'Internal Server Error'}
  except Exception as e:
    print(e)
    context = { 'status' :'fail'}
  finally:
    return JsonResponse(context)

@csrf_exempt
def addNE(request):
  try:
    if request.method == 'POST':
      buf = request.body.decode('utf-8')
      res = json.loads(buf)
      data = res["data"]
      passwd = ""
      if data != None:
        data= ast.literal_eval(data)
        passwd = data["passwd"]
        password = encrypter.encrypt(bytes(passwd,'utf-8')).decode("utf-8") 
      posts ={
          "target_id": data["tid"],
          "vendor": data["vendor"],
          "model": data["model"],
          "user_id": data["userid"],
          "passwd": password,
          "gne_tid": data["gnetid"],
          "gne_ip": data["gneip"],
          "gne_port": data["gneport"],
          "region": data["region"]
          }
      headers = {'content-type': 'application/json'}
      res = requests.post('http://' + ne_management_dns + ':' + ne_pod + '/api/ne-management/v1/ne', data=json.dumps(posts), headers = headers,
                           auth=HTTPBasicAuth('fujitsu', 'fujitsu'))
      if res.status_code == 200:
        response = res.json()
        context = {'status':'success','data':response}
      else:
        context ={'status':'fail','data':'Internal Server Error'}
  except Exception as e:
    context = { 'status' :'fail'}
  finally:
    return JsonResponse(context)

@csrf_exempt
def logNE(request):
  try:
    if request.method == 'POST':
      buf = request.body.decode('utf-8')
      res = json.loads(buf)
      data = res["data"]
      headers = {'content-type': 'application/json'}
      res =  requests.get('http://'+file_management_dns+':'+file_management_pod+'/api/file-management/v1/backup/pod-name/'+data,auth=HTTPBasicAuth('fujitsu', 'fujitsu'))
      if res.status_code == 200:
        json_content = json.loads(res.text)
        podName = json_content["podName"]
        if not request.GET._mutable:
            request.GET._mutable = True
        request.GET['podName'] = podName
        request.GET['targetId'] = data

        res_dwnldapi = causeofFailure(request)
        return res_dwnldapi
      else:
        context ={'status':'fail','data':'Internal Server Error'}
  except Exception as e:
    print(e)
    context = { 'status' :'fail'}
  finally:
    return JsonResponse(context)


def causeofFailure(request):    
  deleteFiles()
  if request.method == 'GET':
      podName = request.GET.get('podName', '')
      targetId = request.GET.get('targetId', '')
      try:
          url = 'http://'+report_dns+':'+report_pod+'/api/report/v1/backup/download-bkup-log/'+podName+'/'+targetId+''
          r = requests.get(url, auth=HTTPBasicAuth('fujitsu', 'fujitsu'))
          content_disposition = r.headers.get('Content-Disposition')
          if r.status_code == 500:
              context = { 'file_data': 'API Failed to fetch data' ,'count': '0', 'status': 500}
              return JsonResponse(context)

          if not content_disposition:
              print("Not Content disposition")
              context = { 'file_data': 'API Failed to fetch data' ,'count': '0', 'status': 500}
              return JsonResponse(context)
          fname = re.findall('filename=(.+)', content_disposition)
          if len(fname) == 0:
              print("Failed")
          filename = fname[0]
          filename = filename.split('"')[1]
          file_path = os.path.join(settings.STATIC_ROOT, "db_backup/to_download", filename)
          open(file_path, 'wb').write(r.content)           
          path = '/static/db_backup/to_download/'+ filename
          context = {'url':path, 'status':200, 'filename':filename}
          return JsonResponse(context)

      except Exception as exc:
          context = { 'file_data': 'API Failed to fetch data' ,'count': '0', 'status': 500}
          return JsonResponse(context)
      context = {'status':500,'file_data':"Database service currently unavailable",'count':'0'}
      return JsonResponse(context)


@csrf_exempt
def csv_validation(request):
    chunk_data = ""
    headers = {'content-type': 'application/json'}
    csv_data = request.POST.get('chunk')
    
    print('http://'+ne_management_dns+':'+ne_pod+'/api/ne-management/v1/ne/validate-chunk-nes')
    try:
        req = requests.post('http://'+ne_management_dns+':'+ne_pod+'/api/ne-management/v1/ne/validate-chunk-nes', data=csv_data, headers = headers, auth=HTTPBasicAuth('fujitsu', 'fujitsu'))
    except:
        context = { 'schedule': 'API Failed to fetch data' ,'count': '0'}
        return HttpResponse(json.dumps(context))
    if req.status_code == 200:
        
        chunk_data = json.loads(req.text)
        context = { 'chunk_data': chunk_data ,'status': 'success'}
    else:
        chunk_data = json.loads(req.text)
        context = { 'chunk_data': chunk_data["message"],'status':'fail' }
    return HttpResponse(json.dumps(context))

@csrf_exempt
def csv_commit(request):
    chunk_data = ""
    headers = {'content-type': 'application/json'}
    csv_data = request.POST.get('chunk')
    
    print('http://'+ne_management_dns+':'+ne_pod+'/api/ne-management/v1/ne/import-chunk-ne')
    try:
        req = requests.post('http://'+ne_management_dns+':'+ne_pod+'/api/ne-management/v1/ne/import-chunk-ne', data=csv_data, headers = headers, auth=HTTPBasicAuth('fujitsu', 'fujitsu'))
    except:
        context = { 'schedule': 'API Failed to fetch data' ,'count': '0'}
        return HttpResponse(json.dumps(context))
    if req.status_code == 200:
        
        chunk_data = json.loads(req.text)
        context = { 'chunk_data': chunk_data ,'status': 'success'}
    else:
        chunk_data = json.loads(req.text)
        context = { 'chunk_data': chunk_data["message"],'status':'fail' }
    return HttpResponse(json.dumps(context))


def export_NE(request):
    deleteFiles()
    if request.method == 'GET':       
        column_data = request.GET.get('column_data', '')
        actionType = request.GET.get('actionType', '')
        search_String = request.GET.get('search_String', '')
        sort_String = request.GET.get('sort_String', '')
        sort_type = request.GET.get('sort_type', '')
        size = request.GET.get('size', '')
        if column_data is not None:
            column_data = ast.literal_eval(column_data)
        column_data=",".join(column_data)
        print('http://'+ne_management_dns+':'+ne_pod+'/api/ne-management/v1/ne/export-nes?columnNames='+column_data+'&actionType='+actionType+'&searchString='+search_String+'&page=0&size='+size+'&sortString='+sort_String+'&sortOrder='+sort_type)
        try:
            url = 'http://'+ne_management_dns+':'+ne_pod+'/api/ne-management/v1/ne/export-nes?columnNames='+column_data+'&actionType='+actionType+'&searchString='+search_String+'&page=0&size='+size+'&sortString='+sort_String+'&sortOrder='+sort_type
            r = requests.get(url, auth=HTTPBasicAuth('fujitsu', 'fujitsu'))
            content_disposition = r.headers.get('Content-Disposition')
            print(r.headers)
            if not content_disposition:
                print("Not Content disposition")
            fname = re.findall('filename=(.+)', content_disposition)
            if len(fname) == 0:
                print("Failed")
            filename = fname[0]
            filename = filename.split('"')[1]
            file_path = os.path.join(settings.STATIC_ROOT, "to_download", filename)
            open(file_path, 'wb').write(r.content)
            path = '/static/to_download/'+ filename
            context = {'url':path, 'status':'success', 'filename':filename}
            return JsonResponse(context)
        except Exception as exc:
            context = { 'file_data': 'API Failed with exception' ,'count': '0', 'status': 500}
            return JsonResponse(context)
        context = {'status':500,'file_data':"Database service currently unavailable",'count':'0'}
        return JsonResponse(context)

def deleteFiles():
    # Deletion of previous older files in static directory
    db_files_path = "/warriorframework_py3/static/to_download/"
    for file in os.listdir(db_files_path):
        file = os.path.join(db_files_path, file)
        # Deleting all files older than 15 minutes
        fifteen_mins = 15*60
        old_time = int(time.time()) - fifteen_mins

        try:
            file_time = int(os.path.getmtime(file))
            if file_time < old_time:
                if os.path.isfile(file):
                    print("Deleting old file - %s"%file)
                    os.remove(file)
        except Exception as e:
            print("There was an error while deletion of file - {0}".format(e))

@csrf_exempt
def editNE(request):
    try:
        if request.method == 'POST':
            buf = request.body.decode('utf-8')
            res = json.loads(buf)
            passwd = res["passwd"]
            if res["encryptPasswd"] == True:
                password = encrypter.encrypt(bytes(passwd, 'utf-8')).decode("utf-8")
            else:
                password = passwd
            netype = res["netype"]
            if netype == "sne":
                updated_data = {
                    "target_id": res["tid"],
                    "vendor": res["vendor"],
                    "model": res["model"],
                    "user_id": res["userid"],
                    "passwd": password,
                    "gne_tid": res["gnetid"],
                    "region": res["region"],
                }
            else:
                updated_data = {
                    "target_id": res["tid"],
                    "vendor": res["vendor"],
                    "model": res["model"],
                    "gne_ip": res["gneip"],
                    "gne_port": res["gneport"],
                    "user_id": res["userid"],
                    "passwd": password,
                    "region": res["region"],
                }
            r = requests.put('http://' + ne_management_dns + ':' + ne_pod + '/api/ne-management/v1/ne',
                             data=json.dumps(updated_data), headers=headers, auth=HTTPBasicAuth('fujitsu', 'fujitsu'))
            if r.status_code == 200:
                context = {'status': "success", 'resp': r.text}
            else:
                context = {'status': "Fail"}


        else:
            context = {'status':'fail'}
    except Exception as e:
        print("EXception as eeee")
        print(e)
        context = {'status':'fail'}

    finally:
        return JsonResponse(context)

# get tids in add NEs
@csrf_exempt
def getTid(request):
    if request.method == 'POST':
        buf = request.body.decode('utf-8')
        res = json.loads(buf)
        search_value = res["search_value"]
        print("----------------load tid param is ")
        print(res)
        tid_details = []
        print('http://'+ne_management_dns+':'+ne_pod+'/api/ne-management/v1/ne/gne/'+search_value)
        try:
            req = requests.get('http://'+ne_management_dns+':'+ne_pod+'/api/ne-management/v1/ne/gne/'+search_value, auth=HTTPBasicAuth('fujitsu', 'fujitsu'))
        except:
            context = { 'tid_details': 'API Failed' , "status":"error"}
            return JsonResponse(context)
        
        if req.status_code == 200:
            tid_details = req.json()
            context = {'tid_details': tid_details,'status':'success'}
        else:
            json_content = json.loads(req.text)
            context = {'nes': json_content["message"], "status":"error"}

        return JsonResponse(context)

def getNesQuickFilterCount(request):
    try:
        r = requests.get('http://' + dashboard_dns + ':' + dashboard_pod + '/api/dash-board/v1/ne-summary?days=30',auth=HTTPBasicAuth('fujitsu', 'fujitsu'))
        if r.status_code == 200:
            response = json.loads(r.text)

            context = {'status':'success','data':response}
        else:
            context = {'status':'fail'}

    except Exception as e:
        print("Exception ...")
        print(e)
        context = {'status':'fail'}
    finally:
        return JsonResponse(context)
