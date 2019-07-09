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
# Create your views here.
from datetime import datetime as dt

def index(request):
    getmd5('xyz.png')
    return render(request, 'AppOne/index.html')

@csrf_exempt
def train_sign(request):
    if request.method == "GET":
        return render(request, "train_me.html")
    else:
        d = dt.now()
        filename = str(d.date().year)+'-'+str(d.date().month)+'-'+str(d.date().day)+'-'+str(d.time().hour)+'-'+str(d.time().minute)+'-'+str(d.time().second)
        train(filename)
        return redirect('upload_sign')

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
                return redirect('upload_sign')
            else:

                return redirect('register')
                messages.warning(request, 'Sorry, You are not active.')

        else:
            return redirect('register')
            messages.error(request, 'Sorry Recheck your username or password')


@login_required(login_url='/AppOne/register')
def user_logout(request):
    logout(request)
    return redirect("AppOne:redirect_user")



def upload_sign(request):
    if request.method == 'GET':
        return render(request, 'AppOne/upload.html')


def upload(request):
    if request.method == 'GET':
        signature = Signature_form()
        return render(request, 'AppOne/upload_sign.html', context={'form': signature})

    else:
        signature = Signature_form(request.POST, request.FILES)
        print('********')
        # imgs = request.FILES['signature']
        images = request.FILES.getlist('signature');
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
        return redirect('upload_sign')
        # else:
        #     return HttpResponse('Sorry!')





@login_required(login_url='/AppOne/user_login')
def user_logout(request):
    logout(request)
    return redirect("AppOne:redirect_user")




