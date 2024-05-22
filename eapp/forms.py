from django import forms
from django.core.exceptions import ValidationError
from .models import Address, contact, Seller

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['recepient_name', 'recepient_contact', 'address_line1', 'address_line2', 'city', 'state', 'postal_code']
        widgets = {
            'recepient_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Recipient Name'}),
            'recepient_contact': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Recipient Contact'}),
            'address_line1': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Address Line 1'}),
            'address_line2': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Address Line 2'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Postal Code'}),
        }

    def clean_recepient_contact(self):
        recepient_contact = self.cleaned_data.get('recepient_contact')
        if not recepient_contact.isdigit():
            raise ValidationError('Recipient contact should contain only digits.')
        return recepient_contact
    
    
    


class ContactForm(forms.ModelForm):
    class Meta:
        model = contact
        fields = ['name', 'email', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }


class SellerForm(forms.ModelForm):
    class Meta:
        model = Seller
        fields = ['name', 'email', 'phone_no']

    def clean_phone_no(self):
        phone_no = self.cleaned_data.get('phone_no')
        if not phone_no.isdigit():
            raise ValidationError('Phone number should contain only digits.')
        return phone_no


class SellerChangePasswordForm(forms.Form):
    old_password = forms.CharField(label='Old Password', widget=forms.PasswordInput)
    new_password1 = forms.CharField(label='New Password', widget=forms.PasswordInput)
    new_password2 = forms.CharField(label='Confirm New Password', widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')

        if new_password1 != new_password2:
            raise ValidationError("The new passwords don't match.")
