from django.db import models
from django.contrib.auth.models import User


# Create your models here.





class Team(models.Model):
    name = models.CharField(max_length=600)
    logo = models.ImageField(upload_to='images/logos')

    def __unicode__(self):
        return self.name


class Player(models.Model):
    POSITION = (('g', 'Goalkeeper'), ('d', 'Defense'), ('m', 'Midfielder'), ('s', 'Striker'))

    name = models.CharField(max_length=300)
    surname = models.CharField(max_length=600)
    image = models.ImageField(upload_to='images/players', blank=True, null=False)
    position = models.CharField(max_length=2, choices=POSITION)
    value = models.FloatField()
    totalPunctuation = models.FloatField()

    def __unicode__(self):
        return self.name + ',' + self.surname


class playsOn(models.Model):
    player = models.ForeignKey(Player)
    team = models.ForeignKey(Team)


class Manager(models.Model):
    user = models.OneToOneField(User)
    image = models.ImageField(upload_to='images/profile', blank=True, null=False)


    def __unicode__(self):
        return self.user.get_username()


class Club(models.Model):
    name = models.CharField(max_length=100)
    manager = models.OneToOneField(Manager)

    def __unicode__(self):
        return self.name


class squad_club(models.Model):
    player = models.ForeignKey(Player, related_name='player_squad')
    club = models.ForeignKey(Club, related_name='club_squad')


class League(models.Model):
    name = models.CharField(max_length=300)
    administrator = models.OneToOneField(Manager)
    objects = models.Manager()

    def __unicode__(self):
        return self.name


class Cup(models.Model):
    round = models.IntegerField()  # to identify the round
    league = models.ForeignKey(League, related_name='cup_league')


class cup_match(models.Model):
    home = models.ForeignKey(Club, related_name='cup_home_match')
    away = models.ForeignKey(Club, related_name='cup_away_match')
    home_result = models.FloatField()
    away_result = models.FloatField()


class league_match(models.Model):
    home = models.ForeignKey(Club, related_name='league_home_match')
    away = models.ForeignKey(Club, related_name='league_away_match')
    home_result = models.FloatField()
    away_result = models.FloatField()


class Cup_Compose(models.Model):
    club = models.ForeignKey(Club)
    cup = models.ForeignKey(Cup)


class Division(models.Model):
    round = models.IntegerField()  # to identify round
    league = models.ForeignKey(League)
    objects = models.Manager()


class ranking(models.Model):
    club = models.ForeignKey(Club)
    punctuation = models.FloatField()
    division = models.ForeignKey(Division, related_name='division_ranking')



class Admin(models.Model):
    manager = models.ForeignKey(Manager)
    league = models.ForeignKey(League)


class JoinRequest(models.Model):
    manager = models.ForeignKey(Manager, related_name='requester_for_join')
    admin = models.ForeignKey(Manager, related_name='admin_for_join')


class Offer(models.Model):
    buyer = models.ForeignKey(Manager, related_name='buyer_offer')
    seller = models.ForeignKey(Manager, related_name='seller_offer')
    player = models.ForeignKey(Player, related_name='player_offer')
    amount = models.FloatField()


class RawPunctuation(models.Model):
    player = models.OneToOneField(Player)
    total = models.FloatField()
