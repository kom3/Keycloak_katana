from django.shortcuts import render
import requests
from requests.auth import HTTPBasicAuth
from django.http import HttpResponse,JsonResponse
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
import json
import ast

ne_management_dns ='167.254.204.73'
ne_pod ='30195'
list_manager_dns='list-manager-svc.jx-staging'
list_pod='8080'
file_management_dns = '167.254.204.73'
file_management_pod = '30191'
allRegions = ['All','Alabama','Alaska','Arizona','Arkansas','California','Colorado','Connecticut','District of Columbia','Delaware','Florida','Georgia','Hawaii','Idaho','Illinois','Indiana','Iowa','Kansas','Kentucky','Louisiana','Maine','Maryland','Massachusetts','Michigan','Minnesota','Mississippi','Missouri','Montana','Nebraska','Nevada','New Hampshire','New Jersey','New Mexico','New York','North Carolina','North Dakota','Ohio','Oklahoma','Oregon','Pennsylvania','Rhode Island','South Carolina','South Dakota','Tennessee','Texas','Utah','Vermont','Virginia','Washington','West Virginia','Wisconsin','Wyoming','Other']
headers = {'content-type': 'application/json'}
class HomePageView(TemplateView):
    def get(self, request, **kwargs):
        return render(request, 'container/index.html', usertype="admin")
def getAPIdata(request):
    try:
        pass
        print('http://' + ne_management_dns + ':' + ne_pod + '/api/ne-management/v2/allnes')
        res = requests.get('http://' + ne_management_dns + ':' + ne_pod + '/api/ne-management/v2/allnes',
                           auth=HTTPBasicAuth('fujitsu', 'fujitsu'))
        if res.status_code == 200:
            response = res.json()
            #data = response["nes"]      
            context = {'status':'success','data':response,'allRegions':allRegions}
        else:
            data = []
            context = {'status':'fail','data':data,'allRegions':allRegions}
    except Exception as e:
        pass      
        context = {'status':'fail','results':'API failed to fetch data'}
    finally:
        return  JsonResponse(context)

@csrf_exempt
def deleteListAPI(request):
    try:
        pass
        if request.method == 'POST':
            buf = request.body.decode('utf-8')
            res = json.loads(buf)
            list_id = res["id"]
            list_id = list_id.replace("[","")
            list_id = list_id.replace("]","")
            list_id = list_id.replace("\"","")
            res = requests.delete('http://'+list_manager_dns+':'+list_pod+'/api/element-list/v1/lists/'+list_id,
                               auth=HTTPBasicAuth('fujitsu', 'fujitsu'))
            if res.status_code == 200:
                response = res.json();
                context = {'results':'success','data':response}
            else:
                context = {'results':'fail'}
    except Exception as e:
        pass
        context = {'results':'API Failed to fetch data'}
    finally:
        return  JsonResponse(context)

@csrf_exempt
def createListAPI(request):
    try:
        pass
        if request.method == 'POST':
            buf = request.body.decode('utf-8')
            res = json.loads(buf)
            data = res["data"]
            headers = {'content-type': 'application/json'}
            res = requests.post('http://'+list_manager_dns+':'+list_pod+'/api/element-list/v1/lists/',data=json.dumps(data), headers = headers,
                               auth=HTTPBasicAuth('fujitsu', 'fujitsu'))
            if res.status_code == 200:
                response = res.json();
                context = {'status':'success','data':response}
            else:
                context = {'status':'fail'}
    except Exception as e:
        print("Exception....")
        context = {'status':'fail','results':'API Failed to fetch data'}
    finally:
        return  JsonResponse(context)

def getListAllLists(request):
    try:
        res = requests.get('http://' + list_manager_dns + ':' + list_pod + '/api/element-list/v1/lists/list-detail')
        if res.status_code == 200:
            response = res.json()
            context = {'status':'success','data':response}

        else:
            context = {'status':'fail'}

    except  Exception as e:
        context = { 'status' :'fail'  }
    finally:
        return JsonResponse(context)


@csrf_exempt
def addNEToListAPI(request):
    try:
        pass
        if request.method == 'POST':
            buf = request.body.decode('utf-8')
            res = json.loads(buf)
            data = res["data"]
            list_id = res["id"]
            headers = {'content-type': 'application/json'}
            res = requests.put('http://'+list_manager_dns+':'+list_pod+'/api/element-list/v1/lists/'+list_id,data=json.dumps(data), headers = headers,
                               auth=HTTPBasicAuth('fujitsu', 'fujitsu'))
            if res.status_code == 200:
                response = res.json();
                context = {'results':'success','data':response}
            else:
                context = {'status':'fail'}
    except Exception as e:
        pass
        context = {'results':'API Failed to fetch data'}
    finally:
        return  JsonResponse(context)
def dummy_data(ele,index):
    
    static_data = {"id": "5de8ac5358234c55db2e951b", "target_id": "tid-11", "vendor": "lucent", "model": "ddm2000",
                         "version": "null", "gne_ip": "173.32.150.15", "gne_port": "13332", "user_id": "", "passwd": "",
                         "gne_tid": "null", "gne_vendor": "", "gne_model": "null", "region": "pennsylvania",
                         "new_ne": "YES", "last_sync": "null", "last_backup": "null", "failed_backups": "null",
                         "avg_backup_time": "null", "is_error": "NO", "ne_status": "ASSIGNED", "last_attempt": "null",
                         "last_status": "null", "last_success": "null", "missing_from": "null",
                         "list_id": "5de8ac5358234c57a3e2d3aa", "schedule_id": ["5de8a73f58234c560fc4e585"],
                         "last_user_id": "null", "last_passwd": "null", "created_ts": 1575529555827,
                         "last_exec_days": "null", "list_name": "pennsylvania-9", "schedule_name": ["AUTO_FRI@00:00"]}
    static_data["target_id"] = ele
    if index%2 == 0:
        static_data["vendor"] ="fujitsu"
        static_data["model"] = "flashwave4500"
    elif index%3 == 0:
        static_data["vendor"] ="coriant"
        static_data["model"] = "coriant2500"
    elif index%5 == 0:
        static_data["vendor"] ="lucent"
        static_data["model"] = "lucent4500"
    elif index%7 == 0:
        static_data["vendor"] ="fujitsu"
        static_data["model"] = "flashwave2500"
    else :
        static_data["vendor"] ="nokia"
        static_data["model"] = "nokia4500"
    return static_data

@csrf_exempt
def getNesForSelectedList(request):
    try:

        if request.method == 'POST':
            buf = request.body.decode('utf-8')
            res = json.loads(buf)
            #http://167.254.204.88:8080/api/element-list/v1/lists/5e6a7328b08d715d4fe998d8
            list_id = res["id"]
            res = requests.get('http://' + list_manager_dns + ':' + list_pod + '/api/element-list/v1/lists/'+list_id)
            if res.status_code == 200:
                response = res.json()
                tids = response["element_ids"]
                last_run = response["lastRunStatus"]
                indeces = [index for index, value in enumerate(tids)]
                #print(indeces)
                nes_info = list(map(lambda x,y: dummy_data(x,y),tids,indeces))
                #last_run = {"tid-11":"failure", "tid-12":"success","fujitsu_2100":"success","fujitsu_2200":"success"}
                context = {'status': 'success', 'data': nes_info,'last_run':last_run}
                return JsonResponse(context)
                '''try:
                    nes_response = requests.get(
                        'http://' + ne_management_dns + ':' + ne_pod + '/api/ne-management/v1/getnes',
                        auth=HTTPBasicAuth('fujitsu', 'fujitsu')) #replace this api with reusable micro service api
                    if nes_response.status_code == 200 :
                        nes_res = nes_response.json()
                        context = {'status':'success','data':nes_res, 'last_run': last_run}
                    else:
                        data =[{"id":"5de8ac5358234c55db2e951b","target_id":"Ne1","vendor":"lucent","model":"ddm2000","version":"null","gne_ip":"173.32.150.15","gne_port":"13332","user_id":"","passwd":"","gne_tid":"null","gne_vendor":"","gne_model":"null","region":"pennsylvania","new_ne":"YES","last_sync":"null","last_backup":"null","failed_backups":"null","avg_backup_time":"null","is_error":"NO","ne_status":"ASSIGNED","last_attempt":"null","last_status":"null","last_success":"null","missing_from":"null","list_id":"5de8ac5358234c57a3e2d3aa","schedule_id":["5de8a73f58234c560fc4e585"],"last_user_id":"null","last_passwd":"null","created_ts":1575529555827,"last_exec_days":"null","list_name":"pennsylvania-9","schedule_name":["AUTO_FRI@00:00"]}]
                        context = {'status': 'success', 'data': data}
                        #context = {'status':'fail'} #uncomment this line upon replacing abv api
                except:
                    context = {'status': 'fail'}
                finally:
                    return JsonResponse(context)'''
            else:
                #uncomment below code to load application with static data
                #context = {'status': 'success', 'data': data,'last_run':last_run}
                context = {'status' :'fail'}
                return JsonResponse(context)
        else:
            context = {'status':'fail'}
            return JsonResponse(context)

    except Exception as e:
        context = {'status' :'fail'}
        return JsonResponse(context)

def retrieveAllLists(request):
    try:
        res = requests.get('http://' + list_manager_dns + ':' + list_pod + '/api/element-list/v1/lists/all',
                           auth=HTTPBasicAuth('fujitsu', 'fujitsu'))
        if res.status_code == 200:
            response = res.json();
            context = {'status':'success','data':response}
        else:
            #uncomment below lines to test with static data
            data = [];
            context = {'status': 'fail', 'data': data}

    except:
        context = {'status': 'fail'}
    finally:
        return JsonResponse(context)

@csrf_exempt
def modifyList(request):
    try:
        if request.method == 'POST':
            buf = request.body.decode('utf-8')
            result = json.loads(buf)
            list_id = result["id"]
            response = requests.put('http://'+list_manager_dns+':'+list_pod+'/api/element-list/v1/lists/'+list_id, data=json.dumps(result), headers=headers)
            if response.status_code == 200:
                context = {'status':'success','message':'updated successfully'}
            else:
                context = {'status':'fail'}

        else:
            context = { 'status':'fail'}

    except:
        context = {'status':'fail'}
    finally:
        return  JsonResponse(context)

@csrf_exempt
def retrieveList(request):
    try:
        if request.method == "POST":

            buf = request.body.decode('utf-8')
            result = json.loads(buf)
            list_id = result["id"]
            res = requests.get('http://'+list_manager_dns+':'+list_pod+'/api/element-list/v1/lists/'+list_id)
            if res.status_code == 200:
                data = res.json()
                context = {'status':'success','data':data}
            else:
                context = { 'status':'fail'}
        else:
            context = { 'status':'fail'}

    except Exception as e:
        context = { 'status':'fail'}
    finally:
        return JsonResponse(context)


@csrf_exempt
def lastRunInfo(request):
    try:
        if request.method == "POST":
            buf = request.body.decode('utf-8')
            result = json.loads(buf)
            tid = result["data"]
            tid = str(tid)
            tid = tid.replace('[','').replace(']','').replace('"','').split(",")
            tid = " ".join(tid)
            print(tid)
            res = requests.get('http://'+file_management_dns+':'+file_management_pod+'/api/file-management/v2/backupsummary?tids='+tid,auth=HTTPBasicAuth('fujitsu', 'fujitsu'))
            if res.status_code == 200:
                data = res.json()
                context = {'status':'success','data':data}
            else:
              context = { 'status':'fail','response':'Internal server Error'}
        else:
          context = { 'status':'fail','response':'fail'}

    except Exception as e:
        context = { 'status':'fail'}
    finally:
        return JsonResponse(context)
