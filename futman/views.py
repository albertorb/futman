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
@login_required
def answerbid(request):
    if request.method -- 'POST':
        if request.POST['accept']:
            offer = get_object_or_404(Offer, id=request.POST['accept'])
            ply = offer.player
            amount = offer.amount
            ## seller updates
            squad_buyer = squad_club.objects.all().filter(player=ply)
            squad_buyer.delete()
            offer.buyer.budget += amount
            ## end seller updates
            squad_club.objects.create(player=ply, club=offer.buyer)
            offer.seller.budget -=amount
        elif request.POST['reject']:
            offer = get_object_or_404(Offer, id=request.POST['reject'])
            offer.delete()



@login_required
def dobid(request):
    if request.method == 'POST':
        sellr = get_object_or_404(Manager, id=request.POST['sellerhide'])
        playr = get_object_or_404(Player, id=request.POST['playerhide'])
        Offer.objects.create(buyer=request.user.manager, seller=sellr, player=playr,
                             amount=float(request.POST['amnt']))
    return HttpResponseRedirect('/market/')

@login_required
def market(request):
    # market = Player.objects.all()
    market = squad_club.objects.all()
    alreadybid = Offer.objects.all().filter(buyer=request.user.manager)
    return render_to_response('market.html', {'players': market, 'alreadybid':alreadybid}, context_instance=RequestContext(request))


def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')


@login_required
def create_club(request):
    if request.method == 'POST':
        Club.objects.create(name=request.POST['tname'], manager=request.user.manager, budget = 20000000)
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
        Club.objects.create(name=request.POST['tname'], manager=request.user.manager, budget=20000000)
        cl = get_object_or_404(Club, manager=request.user.manager)
        div = get_object_or_404(Division, league=lg)
        ranking.objects.create(club=cl, punctuation=0.0, division=div)
        return HttpResponseRedirect('/home/')
    return render_to_response('create_league.html', context_instance=RequestContext(request))

@login_required
def check_join(request):
    reqsts = JoinRequest.objects.all().filter(admin=request.user.manager)
    return render_to_response('check_requests.html', {'requests':reqsts}, context_instance=RequestContext(request) )

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
    if len(club) > 0:
        club = club[0]
    else:
        club = False
    rank = ranking.objects.all().filter(club=club)
    if len(rank) > 0:
        rank = rank[0]
    else:
        rank = False

    isAdmin = League.objects.all().filter(administrator=request.user.manager)

    if len(isAdmin) == 0:
        isAdmin = False
    else:
        isAdmin = isAdmin[0]

    join_request = JoinRequest.objects.all().filter(manager=request.user.manager)

    if len(join_request) == 0:
        join = False
    else:
        join = True

    offers = Offer.objects.all().filter(seller=request.user.manager)
    print(offers)

    if len(offers) == 0:
        offers = False

    return render_to_response('home.html', {'club': club, 'hasjoin': join, 'isadmin': isAdmin, 'ranking': rank, 'offers': offers},
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
                usr.image = 'static/img/noimage.png'
            usr.save()

            return HttpResponseRedirect('/')
        else:
            print(managerform.errors)
            print(djangoform.errors)
            managerform = ManagerForm()
            djangoform = DjangoForm()

    return render_to_response('signup.html', {}, context_instance=RequestContext(request))