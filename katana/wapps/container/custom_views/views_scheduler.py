from django.shortcuts import render
import requests
from requests.auth import HTTPBasicAuth
from django.http import HttpResponse,JsonResponse
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
import json
import ast

scheduler_dns = 'scheduler-mgmt-svc.scheduler-mgmt'#'scheduler-svc.jx-ms-scheduler-pr-6'
scheduler_port = '8002'
headers = {'content-type': 'application/json'}
class HomePageView(TemplateView):
    def get(self, request, **kwargs):
        return render(request, 'container/index.html', context=None)

def getSchedules(request):
    try:
        res = requests.get('http://' + scheduler_dns + ':' + scheduler_port + '/api/scheduler/v1/allschedules',
                           auth=HTTPBasicAuth('fujitsu', 'fujitsu'))
        if res.status_code == 200:
            response = res.json()
            #schedulesDetails = response["content"]
            context = {'status':'success','data':response}
        else:
            context ={'status':'fail'}
    except:
        context = { 'status' :'fail'}
    finally:
        return JsonResponse(context)
@csrf_exempt
def deleteSchedule(request):
	try:
		if request.method == 'POST':
			buf = request.body.decode('utf-8')
			res = json.loads(buf)
			print(res)
			data = res["id"]
			if data != None:
				data = ast.literal_eval(data)
			headers = {'content-type': 'application/json'}
			res = requests.post('http://' + scheduler_dns + ':' + scheduler_port + '/api/scheduler/v1/schedule/actions/DELETE',json=data, headers = headers,
                               auth=HTTPBasicAuth('fujitsu', 'fujitsu'))
			if res.status_code == 200:
				context = {'status':'success','data':'Deleted successfully'}
			else:
				context ={'status':'fail','data':'Internal Server Error'}
	except Exception as e:
		print(e)
		context = { 'status' :'fail'}
	finally:
		return JsonResponse(context)
@csrf_exempt
def suspendSchedule(request):
    try:
        if request.method == 'POST':
            buf = request.body.decode('utf-8')
            res = json.loads(buf)
            data = res["id"]
            if data != None:
                data = ast.literal_eval(data)
            headers = {'content-type': 'application/json'}
            res = requests.post('http://' + scheduler_dns + ':' + scheduler_port + '/api/scheduler/v1/schedule/actions/SUSPENDED',json=data, headers = headers,
                               auth=HTTPBasicAuth('fujitsu', 'fujitsu'))
            if res.status_code == 200:
                context = {'status':'success','data':'Suspended successfully'}
            else:
                context ={'status':'fail','data':'Internal Server Error'}
    except Exception as e:
        print(e)
        context = { 'status' :'fail'}
    finally:
        return JsonResponse(context)
@csrf_exempt
def activeSchedule(request):
    try:
        if request.method == 'POST':
            buf = request.body.decode('utf-8')
            res = json.loads(buf)
            data = res["id"]
            if data != None:
               data = ast.literal_eval(data)
            headers = {'content-type': 'application/json'}
            res = requests.post('http://' + scheduler_dns + ':' + scheduler_port + '/api/scheduler/v1/schedule/actions/ACTIVE',json=data, headers = headers,
                               auth=HTTPBasicAuth('fujitsu', 'fujitsu'))
            if res.status_code == 200:
                context = {'status':'success','data':'Activated successfully'}
            else:
                context ={'status':'fail','data':'Internal Server Error'}
    except Exception as e:
        print(e)
        context = { 'status' :'fail'}
    finally:
        return JsonResponse(context)
@csrf_exempt
def runSchedule(request):
    try:
        if request.method == 'POST':
            buf = request.body.decode('utf-8')
            res = json.loads(buf)
            data = res["id"]
            if data != None:
                data = ast.literal_eval(data)
            headers = {'content-type': 'application/json'}
            res = requests.post('http://' + scheduler_dns + ':' + scheduler_port + '/api/scheduler/v1/schedule/actions/RUN',json=data, headers = headers,
                               auth=HTTPBasicAuth('fujitsu', 'fujitsu'))
            if res.status_code == 200:
                context = {'status':'success','data':'Started successfully'}
            else:
                context ={'status':'fail','data':'Internal Server Error'}
    except Exception as e:
        print(e)
        context = { 'status' :'fail'}
    finally:
        return JsonResponse(context)


def getCalendarData(request):
    
    headers = {'content-type': 'application/json'}
    context = {}
    try:
        response = requests.get('http://'+scheduler_dns+':'+scheduler_port+'/api/scheduler/v1/allschedules', auth=HTTPBasicAuth('fujitsu', 'fujitsu'),  headers=headers)
        if response.status_code == 200:
            json_content = response.json()
            json_content = json_content
            context = {"data":json_content, "status":"success"}
        else:
            json_content = json.loads(response.text)
            context = {'data':json_content,'status':'fail'}
            print("called ", response.text)
    except:
        context = {'data':'API FAILED', 'error':'exception'}
    return JsonResponse(context)

@csrf_exempt
def createSchedule(request):
    schedule_name = request.POST.get("schedule_name")
    recuron = request.POST.get("recuron")
    recur_day = request.POST.get("recur_day")
    start_date = request.POST.get("start_date")
    end_date = request.POST.get("end_date")
    status = "ACTIVE"
    creation_type_data = request.POST.get("creation_type_data")
    backup_type = request.POST.get("schedule_type")
    ms_type = request.POST.get("from_ms")

    print("Passing through create schedule in warrior", schedule_name, recuron, recur_day, start_date, end_date, creation_type_data, backup_type, ms_type)

    headers = {'content-type': 'application/json'}
    # ast.literal_eval(POST )

    if(end_date != ''):
        posts = {
            "schedule_name":schedule_name,
            "recur_on": recuron,
            "schedule_day": recur_day,
            "job_status": "ACTIVE",
            "schedule_from": start_date,
            "schedule_to": end_date,
            "data":[{"ids":ast.literal_eval(creation_type_data), "type":ms_type}],
            "backup_type": backup_type
        }
        print("posts in if", posts)
    else:
        posts = {
           "schedule_name":schedule_name,
            "recur_on": recuron,
            "schedule_day": recur_day,
            "job_status": "ACTIVE",
            "schedule_from": start_date,
            "schedule_to": "",
            "data":[{"ids":ast.literal_eval(creation_type_data), "type":ms_type}],
            "backup_type": backup_type
        }
        print("posts in else", posts)
    try:
        r = requests.post('http://'+scheduler_dns+':'+scheduler_port+'/api/scheduler/v1/schedule',
                          data=json.dumps(posts), headers=headers, auth=HTTPBasicAuth('fujitsu', 'fujitsu'))
        print("in try", r)
    except:
        context = {'data': 'API Failed to fetch data', 'status': 'failed'}
        print("in except", context)
        return JsonResponse(context)
    json_content = json.loads(r.text)
    if r.status_code == 200:
        print("in r.status_code", r.status_code)
        context = {'status': "success", 'data': json_content}
    else:

        context = {'status': "failed", 'data': json_content}
    return JsonResponse(context)

@csrf_exempt
def update_schedule(request):

    ID = request.POST.get("schedule_id")
    schedule_name = request.POST.get("schedule_name")
    recuron = request.POST.get("recuron")
    every = request.POST.get("recur_day")
    start_date = request.POST.get("start_date")
    end_date = request.POST.get("end_date")
    jobStatus = request.POST.get("jobStatus")
    backup_type = request.POST.get("schedule_type")
    list_data = request.POST.get("list")
    from_ms = request.POST.get("from_ms")

    headers = {'content-type': 'application/json'}

    if(end_date != ""):
        posts = {   
                    "id":ID,
                    "recuron":recuron,
                    "job_status" : jobStatus,
                    "scheduleFrom":start_date,
                    "scheduleTo":end_date,
                    "scheduleName":schedule_name,
                    "scheduleDay":every,
                    "data":[{"ids":ast.literal_eval(list_data), "type":from_ms}],
                    "backup_type":backup_type
                }
                
    else:
        posts = {
                    "id":ID,
                    "recuron":recuron,
                    "job_status" : jobStatus,
                    "scheduleFrom":start_date,
                    "scheduleTo":"",
                    "scheduleName":schedule_name,
                    "scheduleDay":every,
                    "data":[{"ids":ast.literal_eval(list_data), "type":from_ms}],
                    "backup_type":backup_type
                }
    

    try:
        r = requests.put('http://'+schedule_dns+':'+schedule_pod+'/api/scheduler/v1/schedule', data=json.dumps(posts), headers = headers, auth=HTTPBasicAuth('fujitsu', 'fujitsu'))
    except:
        context = {'data': 'API Failed to fetch data', 'status': 'failed'}
        return JsonResponse(context)
    json_content = json.loads(r.text)
    if r.status_code == 200:
        context = {'status': "success", 'data':json_content}
    else:
        context = {'status': "failed",'data':json_content}
    return JsonResponse(context)


