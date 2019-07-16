from django.shortcuts import render, redirect
from django.contrib import messages
import os

from AppOne.models import Custom_user, Signature
from AppOne.forms import Custom_user_form, Signature_form

from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from AppOne.newSignVerify import model, getmd5, train, test
from django.views.decorators.csrf import csrf_exempt
# Create your views here.
from datetime import datetime as dt

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
        # print("###################")
        # print(request.POST)
        # print(request.FILES)
        # print("###################")
        user = Custom_user_form(request.POST, request.FILES)
        if user.is_valid():
            user = user.save()
            user.set_password(user.password)
            user.save()
            user.is_staff =True
            user.is_superuser = True
            return HttpResponse ('You are registered')
        else:
            return HttpResponse('Error during submission')

@csrf_exempt
def user_login(request):
    if request.method == 'GET':
        custom_user_form = Custom_user_form()
        return render(request, 'AppOne/login.html', {'form':custom_user_form})

    else:

        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        user = authenticate(username=username, password=password, email=email)
        if user:
            if user.is_active:
                login(request, user)
                messages.success(request, 'Login Successful')
                return redirect('uploadsign')
            else:

                return redirect('register')
                messages.warning(request, 'Sorry, You are not active.')

        else:
            return redirect('register')
            messages.error(request, 'Sorry Recheck your username or password')


@login_required(login_url='/AppOne/user_login')
def user_logout(request):
    logout(request)
    return redirect("AppOne:register")



# def upload_sign(request):
#     if request.method == 'GET':
#         return render(request, 'AppOne/upload.html')


@csrf_exempt
@login_required(login_url='/AppOne/user_login')
def upload(request):
    if request.method == 'GET':
        signature = Signature_form()
        return render(request, 'AppOne/upload_sign.html', context={'form': signature})

    else:
        signature = Signature_form(request.POST, request.FILES)
        user = Custom_user.objects.all()

        print('********')
        # imgs = request.FILES['signature']
        images = request.FILES.getlist('signature')
        # img_extension = os.path.splitext(images.name)[1]
        user_folder = '/media/user_signature'
        if not os.path.exists(user_folder):
            os.mkdir(user_folder)
        print("Type:", type(images))
        print("List Length: ", len(images))
        for img in images:
            img_save_path = user_folder, 'signature'
            if not os.path.exists(img_save_path):
                os.mkdir(img_save_path)
            with open(str((img_save_path), 'wb+')) as f:
                for chunk in images.chunks():
                    f.write(chunk)

            # pic = request.FILES['signature']
            # pic.image = img
            # images.save()

            #print(signature)
            print('********')
            print(img, " Type: ", type(img))
            print("$$$$$$$$$$$$$$$$$$$$$$")

        # if signature.is_valid():
        # signature.save()
        return redirect('uploadsign')
        # else:
        #     return HttpResponse('Sorry!')


@csrf_exempt
@login_required(login_url='/AppOne/user_login')
def uploadsign(request):
    return render(request, 'uploadsign.html')



@csrf_exempt
@login_required(login_url='/AppOne/user_login')
def welcome(request):
    return render(request, 'welcome.html')



# @login_required(login_url='/AppOne/user_login')
# def user_logout(request):
#     logout(request)
#     return redirect("AppOne:redirect_user")
#



@login_required(login_url='user_login')
def verify_user(request, email):




