# encoding: utf-8
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from futman.forms import *
from django.http import HttpResponse, HttpResponseRedirect, StreamingHttpResponse
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import datetime
import random

# Create your views here.


def set_onsale(request):
    if request.method == 'POST':
        ply = get_object_or_404(Player, id=request.POST['player'])
        rankng = get_object_or_404(ranking, club=request.user.manager.club)
        lg = rankng.division.league
        mkt = get_object_or_404(Market, league=lg)
        player_market.objects.create(player=ply, amount=request.POST['amount'],
                                     date_joined=datetime.datetime.now(), market=mkt, agent=request.user.manager)
        return HttpResponseRedirect('/lineup')
    return HttpResponseRedirect('/panic')


def feed_buy(offer):
    if not offer.seller.user.username == 'libre':
        bdy = offer.buyer.user.username + " compro por " + str(
            offer.amount) + " a " + offer.player.name + " que jugaba en  " + offer.seller.club.name
        leag = get_object_or_404(ranking, club=offer.seller.club)
    elif offer.buyer.user.username == 'libre':
        bdy = offer.seller.user.username + " vendio por " + str(
            offer.amount) + " al " + offer.player.name + " a mercado libre"
        leag = get_object_or_404(ranking, club=offer.seller.club)

    else:
        bdy = offer.buyer.user.username + " compro por " + str(
            offer.amount) + " a " + offer.player.name + " que estaba libre"
        leag = get_object_or_404(ranking, club=offer.buyer.club)

    f = feed.objects.create(time=datetime.datetime.now(), body=bdy)

    l = league_feed.objects.create(feed=f, league=leag.division.league)
    f.save()
    l.save()


@login_required
def accept_offer(request):
    if request.method == 'POST':
        offer = get_object_or_404(Offer, id=request.POST['accept'])
        ply = offer.player
        amount = offer.amount
        # # buyer updates
        if offer.buyer.user.username == 'libre':
            pass
        else:
            squad_buyer = squad_club.objects.all().filter(player=ply)
            squad_buyer.delete()
            offer.buyer.club.budget -= amount
            offer.buyer.club.save()
        # # end buyer updates
        if offer.buyer.user.username == 'libre':
            pass
        else:
            squad_club.objects.create(player=ply, club=offer.buyer.club)
        offer.seller.club.budget += amount
        offer.seller.club.save()
        feed_buy(offer)
        offer.delete()
        rank = get_object_or_404(ranking, club=request.user.manager.club)
        markt = get_object_or_404(Market, league=rank.division.league)

        player_market.objects.get(player=ply, market=markt).delete()
    return HttpResponseRedirect('/home/')


@login_required
def reject_offer(request):
    if request.method == 'POST':
        offer = get_object_or_404(Offer, id=request.POST['reject'])
        offer.delete()
    return HttpResponseRedirect('/home/')


@login_required
def dobid(request):
    if request.method == 'POST':
        sellr = get_object_or_404(Manager, id=request.POST['sellerhide'])
        playr = get_object_or_404(Player, id=request.POST['playerhide'])
        Offer.objects.create(buyer=request.user.manager, seller=sellr, player=playr,
                             amount=float(request.POST['amnt']), date=datetime.datetime.now())
    return HttpResponseRedirect('/market/')


@login_required
def market(request):
    # market = Player.objects.all()
    update_markets()
    clb = request.user.manager.club
    rank = get_object_or_404(ranking, club=clb)
    markt = Market.objects.filter(league=rank.division.league)
    players = list(player_market.objects.filter(market=markt))
    alreadybid = Offer.objects.filter(buyer=request.user.manager)

    for elem in players:
        if elem in alreadybid.all():
            print(elem.name, ' esta')

    return render_to_response('market.html', {'players': players, 'alreadybid': alreadybid},
                              context_instance=RequestContext(request))


def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')


@login_required
def create_club(request):
    if request.method == 'POST':
        Club.objects.create(name=request.POST['tname'], manager=request.user.manager, budget=20000000)
        return HttpResponseRedirect('/home/')


@login_required
def league_settings(request):
    return render_to_response('league_settings.html', context_instance=RequestContext(request))


@login_required
def lineup(request):
    # lineup
    aux = squad_titular.objects.all().filter(club=request.user.manager.club)
    lineup = []
    for elem in aux:
        lineup.append(elem.player)

    # sorted players
    whole = squad_club.objects.all().filter(club=request.user.manager.club)
    strik = []
    mid = []
    defn = []
    goalk = []
    all = []
    for elem in whole:
        all.append(elem.player)
        if elem.player.position == 's':
            strik.append(elem.player)
        if elem.player.position == 'm':
            mid.append(elem.player)
        if elem.player.position == 'd':
            defn.append(elem.player)
        if elem.player.position == 'g':
            goalk.append(elem.player)
    print(all)
    return render_to_response('lineup.html',
                              {'lineup': lineup, 'Strikers': strik, 'Midfielders': mid, 'Defenses': defn,
                               'Goalkeepers': goalk, 'whole': all},
                              context_instance=RequestContext(request))


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
        initialize_market(Market.objects.create(league=lg))
        return HttpResponseRedirect('/home/')
    return render_to_response('create_league.html', context_instance=RequestContext(request))


@login_required
def check_join(request):
    reqsts = JoinRequest.objects.all().filter(admin=request.user.manager)
    return render_to_response('check_requests.html', {'requests': reqsts}, context_instance=RequestContext(request))


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
    fd = None
    feeds = []
    if rank:
        fd = league_feed.objects.filter(league=rank.division.league)

        for elem in fd:
            feeds.append(elem.feed)

    return render_to_response('home.html',
                              {'feed': feeds, 'club': club, 'hasjoin': join, 'isadmin': isAdmin, 'ranking': rank,
                               'offers': offers},
                              context_instance=RequestContext(request))


@login_required
def league(request):
    return render_to_response('league.html', context_instance=RequestContext(request))


@login_required
def settings(request):
    if request.method == 'POST':
        managerform = ManagerForm
        print(request.POST['username'])
        djan = User.objects.all().filter(username=request.POST['username'])
        djan.update(username=request.POST['username'], email=request.POST['email'])
        if request.POST['password']:
            djan.update(password=request.POST['password'])
        usr = managerform.save(commit=False)
        usr.user = djan
        if 'image' in request.FILES:
            usr.image = request.FILES['image']
        elif usr.image is not None:
            pass
        elif usr.image is None:
            usr.image = 'static/img/noimage.ppg'
        djan.save()
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


def computer_offers():
    players_onsale = player_market.objects.all()
    usr = get_object_or_404(User, username='libre')
    free_agent = get_object_or_404(Manager, user=usr)
    for elem in players_onsale:
        if not elem.agent.user.username == 'libre':
            rcv_offers = Offer.objects.filter(player=elem, buyer=free_agent).order_by('date')
            if len(rcv_offers) > 0:
                if (datetime.datetime.now().day - rcv_offers[0].date.day) > 0:
                    seller = squad_club.objects.filter(player=elem.player)[0]
                    amnt = elem.player.value - elem.player.value * 0.05
                    Offer.objects.create(buyer=free_agent, seller=seller.club.manager, player=elem.player, amount=amnt,
                                         date=datetime.datetime.now())
            else:
                seller = squad_club.objects.filter(player=elem.player).__getitem__(0)
                amnt = elem.player.value - elem.player.value * 0.05
                Offer.objects.create(buyer=free_agent, seller=seller.club.manager, player=elem.player, amount=amnt,
                                     date=datetime.datetime.now())


def update_markets():
    updates_counter = 0  # players to be added on market
    usr = get_object_or_404(User, username='libre')
    free_agent = get_object_or_404(Manager, user=usr)
    for markt in Market.objects.all():
        onmarket = player_market.objects.filter(market=markt)
        for player in onmarket:
            diff = datetime.date.today() - player.date_joined
            print('diff vale: ', diff)
            if diff.days >= 2:
                offers = Offer.objects.filter(player=player.player).order_by('-amount')
                print(len(offers))
                print(offers[0].buyer.user.username)

                if len(offers) > 0:

                    acceptoffer(offers[0])
                    removeoffers(offers)
                    player.delete()
                    updates_counter += 1
                else:

                    player.delete()
                    updates_counter += 1
        if updates_counter > 0:
            working_list = []
            onmarket = player_market.objects.filter(market=markt)
            for elem in onmarket:
                working_list.append(elem.player)
            for count in range(updates_counter):
                new_player = Player.objects.order_by('?')[0]
                while new_player in working_list:
                    new_player = Player.objects.order_by('?')[0]
                working_list.append(new_player)
                player_market.objects.create(player=new_player, amount=new_player.value, market=markt,
                                             date_joined=datetime.datetime.now(), agent=free_agent)
    computer_offers()


def initialize_market(markt):
    working_list = []
    usr = get_object_or_404(User, username='libre')
    free_agent = get_object_or_404(Manager, user=usr)
    for count in range(5):
        new_player = Player.objects.order_by('?')[0]
        while new_player in working_list:
            new_player = Player.objects.order_by('?')[0]
        working_list.append(new_player)

        player_market.objects.create(player=new_player, amount=new_player.value, market=markt,
                                     date_joined=datetime.datetime.now(), agent=free_agent)


def acceptoffer(offer):
    ply = offer.player
    amount = offer.amount  # # buyer updates
    squad_buyer = squad_club.objects.all().filter(player=ply)
    squad_buyer.delete()
    offer.buyer.club.budget -= amount
    offer.buyer.club.save()
    # # end buyer updates
    squad_club.objects.create(player=ply, club=offer.buyer.club)
    if not offer.seller.user.username == 'libre':
        offer.seller.club.budget += amount
        offer.seller.club.save()
    feed_buy(offer)


def removeoffers(offers):
    for elem in offers:
        print(elem.player.name)
        print(elem.buyer.user)
        of = Offer.objects.filter(player=elem.player, buyer=elem.buyer)
        of.delete()
    print('offers deleted')
