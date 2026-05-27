from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, UserProfile
from requests.models import EmergencyBroadcast


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your UAP email'
    }))
    uap_id = forms.CharField(max_length=20, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your UAP ID'
    }))
    user_type = forms.ChoiceField(choices=CustomUser.USER_TYPE_CHOICES, widget=forms.Select(attrs={
        'class': 'form-control'
    }))
    phone_number = forms.CharField(max_length=15, required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Phone number (optional)'
    }))

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'uap_id', 'user_type', 'phone_number', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Choose a username'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm password'})


class EmergencyBroadcastForm(forms.ModelForm):
    class Meta:
        model = EmergencyBroadcast
        fields = ('title', 'message', 'target_blood_groups')
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. URGENT: O- needed for emergency surgery',
                'maxlength': 200,
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Patient, location, contact, time-sensitivity…',
            }),
            'target_blood_groups': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. O-, AB-   (leave blank for all donors)',
            }),
        }


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('profile_picture', 'date_of_birth', 'bio', 'blood_group')
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'bio': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Tell us about yourself...'}),
            'blood_group': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('', 'Select Blood Group'),
                ('A+', 'A+'), ('A-', 'A-'),
                ('B+', 'B+'), ('B-', 'B-'),
                ('O+', 'O+'), ('O-', 'O-'),
                ('AB+', 'AB+'), ('AB-', 'AB-'),
            ]),
        }