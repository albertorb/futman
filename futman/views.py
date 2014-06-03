# encoding: utf-8
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from futman.forms import *
from django.http import HttpResponse, HttpResponseRedirect, StreamingHttpResponse
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Create your views here.
def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')


@login_required
def create_club(request):
    if request.method == 'POST':
        Team.objects.create(name=request.POST['tname'], manager=request.user.manager)
        return HttpResponseRedirect('/home/')


@login_required
def league_settings(request):
    return render_to_response('league_settings.html', context_instance=RequestContext(request))


@login_required
def lineup(request):
    return render_to_response('lineup.html', context_instance=RequestContext(request))


@login_required
def send_request_join(request):
    if request.method == 'POST':
        dusr = get_object_or_404(User, username=request.POST['join'])
        man = get_object_or_404(Manager, user=dusr)
        JoinRequest.objects.create(manager=request.user.manager, admin=man)
        return HttpResponseRedirect('/home/')


@login_required
def create_league(request):
    if request.method == 'POST':
        League.objects.create(name=request.POST['name'], administrator=request.user.manager)
        lg = get_object_or_404(League, name=request.POST['name'])
        Division.objects.create(round=0, league=lg)
        Club.objects.create(name=request.POST['tname'], manager=request.user.manager)
        cl = get_object_or_404(Club, manager=request.user.manager)
        div = get_object_or_404(Division, league=lg)
        ranking.objects.create(club=cl, punctuation=0.0, division=div)
        return HttpResponseRedirect('/home/')
    return render_to_response('create_league.html', context_instance=RequestContext(request))


@login_required
def join(request):
    join_request = JoinRequest.objects.all().filter(manager=request.user.manager)
    if len(join_request) == 0:
        join = False
    else:
        join = True
    if request.method == 'POST':
        lgname = request.POST['lgname']
        if User.objects.all().filter(username=lgname):
            admins = User.objects.get(username=lgname)
            print(admins)
            res = League.objects.all().filter(administrator=admins.manager)
            if len(res) == 0:
                return render_to_response('join.html', {'league': False},
                                          context_instance=RequestContext(request))
        else:
            return render_to_response('join.html', {'league': False},
                                      context_instance=RequestContext(request))
        print(res)
        return render_to_response('join.html', {'league': res[0], 'isjoin': join},
                                  context_instance=RequestContext(request))


@login_required
def home(request):
    club = Club.objects.all().filter(manager=request.user.manager)
    rank = ranking.objects.all().filter(club=club)
    isAdmin = League.objects.all().filter(administrator=request.user.manager)

    if len(isAdmin) == 0:
        isAdmin = False

    join_request = JoinRequest.objects.all().filter(manager=request.user.manager)

    if len(join_request) == 0:
        join = False
    else:
        join = True

    return render_to_response('home.html', {'club': club[0], 'hasjoin': join, 'isadmin': isAdmin[0], 'ranking':rank[0]},
                              context_instance=RequestContext(request))


@login_required
def league(request):
    return render_to_response('league.html', context_instance=RequestContext(request))


@login_required
def settings(request):
    if request.method == 'POST':
        print(request.POST['username'])
        djan = User.objects.update(username=request.POST['username'], email=request.POST['email'])
        if request.POST['password']:
            djan = User.objects.update(password=request.POST['password'])
        usr = managerform.save(commit=False)
        usr.user = djan
        if 'image' in request.FILES:
            usr.image = request.FILES['image']
        elif usr.image is not None:
            pass
        elif usr.image is None:
            usr.image = 'static/img/noimage.ppg'
        usr.save()

        return HttpResponseRedirect('/')

    return render_to_response('settings.html', context_instance=RequestContext(request))


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

            return HttpResponseRedirect('/')
        else:
            print(managerform.errors)
            print(djangoform.errors)
            managerform = ManagerForm()
            djangoform = DjangoForm()

    return render_to_response('signup.html', {}, context_instance=RequestContext(request))