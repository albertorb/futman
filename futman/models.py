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
    team = models.OneToOneField(Team)
    position = models.CharField(max_length=2, choices=POSITION)
    value = models.FloatField()
    totalPunctuation = models.IntegerField()

    def __unicode__(self):
        return self.name + ',' + self.surname


class Manager(models.Model):
    user = models.OneToOneField(User)
    image = models.ImageField(upload_to='images/profile', blank=True, null=False)

    def __unicode__(self):
        return self.user.get_username()


class Club(models.Model):
    name = models.CharField(max_length=100)
    squad = models.ForeignKey(Player)
    manager = models.OneToOneField(Manager)

    def __unicode__(self):
        return self.name


class Division(models.Model):
    ranking = models.ForeignKey(Club)
    round = models.IntegerField()  # to identify round


class Cup(models.Model):
    compose = models.ForeignKey(Club)
    round = models.IntegerField()  # to identify the round


class League(models.Model):
    name = models.CharField(max_length=300)
    administrator = models.OneToOneField(Manager)
    compose = models.ForeignKey(Division)
    cup = models.ForeignKey(Cup)

    def __unicode__(self):
        return self.name


class RawPunctuation(models.Model):
    player = models.OneToOneField(Player)
    total = models.IntegerField()
