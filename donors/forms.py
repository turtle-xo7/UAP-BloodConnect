from django import forms
from .models import Donor, DonationHistory, BloodGroup, DonationDrive




class DonorRegistrationForm(forms.ModelForm):
   blood_group = forms.ModelChoiceField(
       queryset=BloodGroup.objects.all(),
       widget=forms.Select(attrs={'class': 'form-control'}),
       empty_label="Select Blood Group"
   )


   class Meta:
       model = Donor
       fields = ['blood_group', 'location', 'emergency_response']
       widgets = {
           'location': forms.Select(attrs={'class': 'form-control'}),
           'emergency_response': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
       }




class DonationHistoryForm(forms.ModelForm):
   class Meta:
       model = DonationHistory
       fields = ['donation_date', 'units_donated', 'hospital', 'certificate']
       widgets = {
           'donation_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
           'units_donated': forms.NumberInput(
               attrs={'class': 'form-control', 'step': '0.5', 'min': '0.5', 'max': '2.0'}),
           'hospital': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Hospital name'}),
       }


class DonationDriveForm(forms.ModelForm):
   target_blood_groups = forms.ModelMultipleChoiceField(
       queryset=BloodGroup.objects.all(),
       widget=forms.CheckboxSelectMultiple(),
       required=False,
       label="Target Blood Groups"
   )

   class Meta:
       model = DonationDrive
       fields = [
           'title', 'description', 'date', 'start_time', 'end_time',
           'venue', 'target_units', 'target_blood_groups', 'partner_organization',
       ]
       widgets = {
           'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Drive title'}),
           'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
           'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
           'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
           'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
           'venue': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Location / venue'}),
           'target_units': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
           'partner_organization': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional partner org'}),
       }
