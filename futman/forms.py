#encoding:utf-8
__author__ = 'AlbertoRinconBorreguero'

from django.forms import ModelForm
from django import forms
from futman.models import *

class DjangoForm(ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'password')

class ManagerForm(ModelForm):
    class Meta:
        model = Manager
        fields = {'image'}