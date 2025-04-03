from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from user.models import ParkingPlace
class ParkingPlaceForm(forms.ModelForm):
    class Meta:
        model = ParkingPlace
        fields = ['name', 'unique_id', 'address', 'max_slots', 'unavailable_days', 'is_active']

class UserRegisterForm(UserCreationForm):
	email = forms.EmailField()
	phone_no = forms.CharField(max_length = 20)
	first_name = forms.CharField(max_length = 20)
	last_name = forms.CharField(max_length = 20)
	class Meta:
		model = User
		fields = ['username', 'email', 'phone_no', 'password1', 'password2']

class VerificationForm(forms.Form):
    verification_code = forms.CharField(max_length=4, min_length=4, required=True)
    
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("This username is already taken. Please choose another one.")
        return username
