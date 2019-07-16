from django.shortcuts import render, redirect
from django.contrib import messages

from AppOne.models import Custom_user, Signature
from AppOne.forms import Custom_user_form, Signature_form

from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from AppOne.newSignVerify import model, getmd5, train, test
from django.views.decorators.csrf import csrf_exempt

from django.core.files.storage import FileSystemStorage

# Create your views here.
from datetime import datetime as dt
import requests
import json
import re
import os

IP = "127.0.0.1"
PORT = "3000"
IMGS_PATH = "./verification/profile"
GENUINE_PATH = "./verification/genuine"
TEST_PATH = "./verification/test"
MODEL_PATH = "./verification/modelsave"

def index(request):
    getmd5('xyz.png')
    return render(request, 'AppOne/index.html')


def home(request):
    return  render(request, 'home.html')

@csrf_exempt
def train_sign(request):
    if request.method == "GET":
        return render(request, "train_me.html")
    else:
        d = dt.now()
        filename = str(d.date().year)+'-'+str(d.date().month)+'-'+str(d.date().day)+'-'+str(d.time().hour)+'-'+str(d.time().minute)+'-'+str(d.time().second)
        train(filename)
        return redirect('uploadsign')

@csrf_exempt
def test_sign(request):
    if request.method == "GET":
        return render(request, "test_me.html",{"result":"0"})
    else:
        filename = request.POST['filename']
        print("******** Test is happening here **********")
        acc = test(filename)
        return render(request, "test_me.html", {"result":acc*100})


def register(request):
    if request.method == 'GET':
        custom_user_form = Custom_user_form()

        return render(request, 'AppOne/signup.html', {'form':custom_user_form})
    else:
        print("###################")
        print(request.POST)
        print(request.FILES)
        print("###################")

        data={
        "$class": "com.pax.signature.CreateUser",
        "emailId": "string",
        "name": "string",
        "password": "string"
        }
        username = request.POST['username']
        data['name'] = username
        data['emailId'] = request.POST['email']
        data['password'] = request.POST['password']
        
        data_json = json.dumps(data)
        output = requests.post('http://'+IP+':'+PORT+'/api/CreateUser', headers={"content-type": "application/json"}, data=data_json)

        if output.status_code == 200:
            myimg = request.FILES['photo']
            fs = FileSystemStorage(location=IMGS_PATH)
            filename = fs.save(username, myimg)
            fileurl = fs.url(filename)
            return redirect('user_login')
        else:
            return HttpResponse("<h1>Something is wrong<h1><br><br>"+output.text)
        # user = Custom_user_form(request.POST, request.FILES)
        # if user.is_valid():
        #     user = user.save()
        #     user.set_password(user.password)
        #     user.save()
        #     user.is_staff =True
        #     user.is_superuser = True
        #     return HttpResponse ('You are registered')
        # else:
        #     return HttpResponse('Error during submission')

@csrf_exempt
def user_login(request):
    if request.method == 'GET':
        custom_user_form = Custom_user_form()
        return render(request, 'AppOne/login.html', {'form':custom_user_form})

    else:
        #if "login" in request.POST:
        print("&&&&&&&&&&&&&&&&&&&&&&&&")
        print(request.POST)
        print("&&&&&&&&&&&&&&&&&&&&&&&&")
        data={
        "$class": "com.pax.signature.UserCheck",
        "email": "",
        "password": ""
        }
        port = request.POST.get('port')
        data['password'] = request.POST.get('password')
        email = request.POST.get('email')
        data['email'] = email
        data_json = json.dumps(data)
        output = requests.post('http://'+IP+':'+PORT+'/api/UserCheck', headers={"content-type": "application/json"}, data=data_json)
        if output.status_code == 200:
            
            response = redirect('uploadsign')
            response.set_cookie('id', port)
            response.set_cookie('email', email)
            return response
        else:
            return redirect('user_login')

        # user = authenticate(username=username, password=password, email=email)
        # if user:
        #     if user.is_active:
        #         login(request, user)
        #         messages.success(request, 'Login Successful')
        #         return redirect('uploadsign')
        #     else:

        #         return redirect('register')
        #         messages.warning(request, 'Sorry, You are not active.')

        # else:
        #     return redirect('register')
        #     messages.error(request, 'Sorry Recheck your username or password')


@login_required(login_url='/AppOne/user_login')
def user_logout(request):
    logout(request)
    return redirect("AppOne:register")



# def upload_sign(request):
#     if request.method == 'GET':HttpResponse("<h1> Wrong </h1>"+output.text)HttpResponse("<h1> Wrong </h1>"+output.text)HttpResponse("<h1> Wrong </h1>"+output.text)
#         return render(request, 'AppOne/upload.html')


@csrf_exempt
# @login_required(login_url='/AppOne/user_login')
def upload(request):
    if request.method == 'GET':
        signature = Signature_form()
        return render(request, 'AppOne/upload_sign.html', context={'form': signature})

    else:
        signature = Signature_form(request.POST, request.FILES)
        print('********')
        # imgs = request.FILES['signature']
        images = request.FILES.getlist('signature')
        print("Type:", type(images))
        print("List Length: ", len(images))
        for img in images:

            # pic = request.FILES['signature']
            # pic.image = img
            #img.save()

            #print(signature)
            print('********')
            print(img, " Type: ", type(img))
            print("$$$$$$$$$$$$$$$$$$$$$$")

        # if signature.is_valid():
        # signature.save()
        return redirect('uploadsign')
        # else:
        #     return HttpResponse('Sorry!')


def homeData(user_email, signee):
    allowed=[]
    data = {"hasSign":"False", "hasAllowed":[], "allowed":[]}
    for i in signee:
        if i['emailId']==user_email:
            allowed = i['allowedList']
            if i.get("sign","notAvailable") == "notAvailable":
                data["hasSign"] = "False"
            else:
                data["hasSign"] = "True"
            break
    for i in signee:
        if user_email in i['allowedList']:
            data['hasAllowed'].append(i)
        if i['emailId'] in allowed:
            data['allowed'].append(i)
    return data, allowed

@csrf_exempt
#@login_required(login_url='/AppOne/user_login')
def uploadsign(request):
    if request.method == "GET":
        signee_json = requests.get("http://"+IP+":"+request.COOKIES.get('id')+"/api/Signee")
        signee = json.loads(signee_json.text)
        data, allowed = homeData(request.COOKIES.get('email'), signee)                
        return render(request, 'uploadsign.html', data)
    elif request.method == "POST":
        print("$$$$$$$$IN POST$$$$$$$$$$$")
        print(request.POST)
        print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
        if request.POST.get("form") == "uploadsign":
            print("**********")
            print("I am upload")
            images = request.FILES.getlist('signatures')
            print(images)
            fs = FileSystemStorage(location=GENUINE_PATH)
            for i,img in enumerate(images):
                fname = fs.save("Gen"+str(i), img)
            
            d = dt.now()
            filename = str(d.date().year)+'-'+str(d.date().month)+'-'+str(d.date().day)+'-'+str(d.time().hour)+'-'+str(d.time().minute)+'-'+str(d.time().second)
            signHash = train(filename)

            data={
            "$class": "com.pax.signature.UploadSignature",
            "sigId": "string",
            "signatureHash": "string"
            }
            data['sigId'] = filename
            data['signatureHash'] = signHash
            data_json = json.dumps(data)
            output = requests.post('http://'+IP+':'+request.COOKIES.get('id')+'/api/UploadSignature', headers={"content-type": "application/json"}, data=data_json)
            
            if output.status_code == 200:
                return redirect('uploadsign') 
            else:
                return HttpResponse("<h1>Sth is wrong</h1><br>"+output.text)
        
        if request.POST.get("search","None") != "None":
            print("$$$$$$$$IN SEARCH$$$$$$$$$$$")
            print(request.POST)
            print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
            searchkey = request.POST['query']
            signee_json = requests.get("http://"+IP+":"+request.COOKIES.get('id')+"/api/Signee")
            signee = json.loads(signee_json.text)
            email = request.COOKIES.get('email')
            data, allowed = homeData(email, signee)
            search_list=[]
            for i in signee:
                if re.search(searchkey, str(i['emailId']), flags=re.IGNORECASE) or re.search(searchkey, str(i['name']), flags=re.IGNORECASE):
                    i['allowed'] = "yes" if i['emailId'] in allowed else "no"
                    i['hasAllowed'] = "yes" if email in i['allowedList'] else "no"
                    search_list.append(i)
            data['searchResult']=search_list
            return render(request, 'search.html', data)

        if request.POST.get("verify","None") != "None":
            signee = request.POST.get("verify")
            image = request.FILES['test']
            fs = FileSystemStorage(location=TEST_PATH)
            filename = fs.save("test", image)
            data ={
            "$class": "com.pax.signature.CheckAllowed",
            "owner": {},
            "signatureHash": "string"
            }
            data['owner']="com.pax.signature.Signee#"+str(signee)
            d = requests.get('http://'+IP+':'+request.COOKIES.get('id')+'/api/Signee?filter={"where":{"emailId":"'+str(signee)+'"}}')
            d = json.loads(d)
            if d[0].get("sign","notAvailable")=="notAvailable":
                return HttpResponse("<h1>User has no sign</h1>")
            signFileName = d[0].get("sign").split('#')[1]
            data['signatureHash'] = getmd5(os.path.join(MODEL_PATH, signFileName+".h5"))
            data_json = json.dumps(data)
            output1 = requests.post('http://'+IP+':'+request.COOKIES.get('id')+'/api/CheckAllowed', headers={"content-type": "application/json"}, data=data_json)
            if output1.status_code == 200:
                accuracy = test(signFileName)
                data2 = {
                "$class": "com.pax.signature.RecordResult",
                "owner": {},
                "result": 0
                }
                data2['owner'] = "com.pax.signature.Signee#"+str(signee)
                data2['result'] = round(accuracy, 2)
                data_json = json.dumps(data2)
                output2 = requests.post('http://'+IP+':'+request.COOKIES.get('id')+'/api/RecordResult', headers={"content-type": "application/json"}, data=data_json)
                if output2.status_code == 200:
                    return redirect('uploadsign')
                else:
                    return HttpResponse("<h1>Error while recording result</h1>")               
            else:
                return HttpResponse("<h1>No authority to validate</h1>")
            
        if request.POST.get("disallow","None") != "None":
            signee = request.POST.get("disallow")
            data = {
            "$class": "com.pax.signature.Disallow",
            "email": "string"
            }
            data['email'] = str(signee)
            data_json = json.dumps(data)
            output = requests.post('http://'+IP+':'+request.COOKIES.get('id')+'/api/Disallow', headers={"content-type": "application/json"}, data=data_json)
            if output.status_code == 200:
                return redirect('uploadsign')
            else:
                return HttpResponse("<h1>Error Disallowing</h1>")
        



    else:
        print(request.POST)
        print(request.FILES)




@csrf_exempt
#@login_required(login_url='/AppOne/user_login')
def welcome(request):
    return render(request, 'welcome.html')



# @login_required(login_url='/AppOne/user_login')
# def user_logout(request):
#     logout(request)
#     return redirect("AppOne:redirect_user")
#



