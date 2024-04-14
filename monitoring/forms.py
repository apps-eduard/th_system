from django import forms
from .models import EmailSettings

class EmailSettingsForm(forms.ModelForm):
    class Meta:
        model = EmailSettings
        fields = ['sender_email', 'receiver_email', 'password']
