#encoding: utf-8
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from futman.forms import *
from django.http import HttpResponse, HttpResponseRedirect, StreamingHttpResponse
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Create your views here.

#@login_required()
def home(request):
    return render_to_response('home.html', context_instance=RequestContext(request))


def welcome(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        account = authenticate(username=username, password=password)
        if account is not None:
            print('account is not none')
            if account.is_active:
                print('account is active')
                login(request, account)
                return HttpResponseRedirect('/home')
            else:  # non active account
                print('account is not active')
                return HttpResponseRedirect('/')
        else:
            # login incorrecto
            print('incorret login')
            return render_to_response('welcome.html', {'error': True}, context_instance=RequestContext(request))

    return render_to_response('welcome.html', {'error': False}, context_instance=RequestContext(request))


def signup(request):
    managerform = ManagerForm()
    djangoform = DjangoForm()
    if request.method == 'POST':
        print(request.POST['username'])
        djangoform = DjangoForm(request.POST)
        managerform = ManagerForm(request.POST)

        if managerform.is_valid() and djangoform.is_valid():
            djan = User.objects.create_user(request.POST['username'], request.POST['email'], request.POST['password'])
            usr = managerform.save(commit=False)
            usr.user = djan
            if 'image' in request.FILES:
                usr.image = request.FILES['image']
            else:
                usr.image = 'static/img/noimage.ppg'
            usr.save()

            return HttpResponseRedirect('/welcome')
        else:
            print(managerform.errors)
            print(djangoform.errors)
            managerform = ManagerForm()
            djangoform = DjangoForm()

    return render_to_response('signup.html', {}, context_instance=RequestContext(request))