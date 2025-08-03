from django import forms
from django.contrib.auth.models import User
from .models import CustomerProfile, ProviderProfile, ProviderService, PortfolioProject, Review
from django.contrib.auth.forms import UserCreationForm

class CustomerRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=15)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class ProviderRegisterForm(UserCreationForm):
    username = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    phone = forms.CharField(required=True)
    business_name = forms.CharField(required=False)
    categories = forms.MultipleChoiceField(
        choices=[
            ('electrician', 'Electrician'),
            ('plumber', 'Plumber'),
            ('painter', 'Painter'),
            ('carpenter', 'Carpenter'),
            ('solar-electrician', 'Solar Electrician'),
        ],
        widget=forms.CheckboxSelectMultiple,
        required=True
    )
    location = forms.CharField(required=True)

    class Meta:
        model = User
        fields = ['username','first_name', 'last_name', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['username']
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        if commit:
            user.save()
        return user



class ProviderServiceForm(forms.ModelForm):
    class Meta:
        model = ProviderService
        fields = ['category', 'title', 'description', 'tags']
        widgets = {
            'tags': forms.TextInput(attrs={'placeholder': 'Comma separated tags'}),
        }


class BasicInfoForm(forms.ModelForm):
    class Meta:
        model = ProviderProfile
        fields = ['phone', 'location']


class BusinessDetailsForm(forms.ModelForm):
    class Meta:
        model = ProviderProfile
        fields = ['business_name', 'services_offered', 'experience']



class AccountSettingsForm(forms.ModelForm):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput(), required=False)

    class Meta:
        model = User
        fields = ['email', 'password']

from .models import Quotation

from django import forms
from .models import Quotation

class QuotationForm(forms.ModelForm):
    class Meta:
        model = Quotation
        fields = ['labor_cost', 'material_cost', 'misc_cost']
        widgets = {
            'labor_cost': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter labor cost'
            }),
            'material_cost': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter material cost'
            }),
            'misc_cost': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter miscellaneous cost'
            }),
        }

class PortfolioProjectForm(forms.ModelForm):
    class Meta:
        model = PortfolioProject
        fields = ['title', 'description', 'image']

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.HiddenInput(),
            'comment': forms.Textarea(attrs={'placeholder': 'Write your review...', 'class': 'form-control', 'rows': 4}),
        }

                