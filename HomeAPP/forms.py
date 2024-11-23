from django.forms import ModelForm
from .models import *
from django import forms

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'goalAmount', 'collectedAmount', 'startDate', 'endDate', 'status', 'image','owner']
        

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'profile_picture','phn_number']  # List the fields you want to allow users to update

       