from django.forms import DateInput, ModelForm
from .models import *
from django import forms

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'goalAmount', 'collectedAmount', 'startDate', 'endDate', 'status', 'image','owner']
         # Adding a DateInput widget to show a calendar for status date selection (if applicable)
         # Ensure the DateInput widget is correctly added for startDate and endDate
    startDate = forms.DateField(
        widget=DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=True
    )
    endDate = forms.DateField(
        widget=DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=True
    )
    
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'profile_picture','phn_number']  # List the fields you want to allow users to update

       