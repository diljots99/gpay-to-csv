# gpayparser/forms.py

from django import forms

class GPayForm(forms.Form):
    html_file = forms.FileField( required=True)
