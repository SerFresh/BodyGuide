from django import forms

class UploadFrom(forms.Form):
    file = forms.ImageField(required=True)
