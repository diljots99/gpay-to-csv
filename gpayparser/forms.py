# gpayparser/forms.py

from django import forms
from django.core.exceptions import ValidationError

class GPayForm(forms.Form):
    html_file = forms.FileField( required=True)
    start_date = forms.DateField(label='Start Date', required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(label='End Date', required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    def clean_html_file(self):
        html_file = self.cleaned_data.get('html_file')

        # Add your file validation rules here if needed
        # Example: Limit allowed file types
        allowed_types = ['text/html']
        if html_file.content_type not in allowed_types:
            raise ValidationError("Invalid file type. Please upload a valid HTML file.")

        # Add other file validation rules as needed

        # Example: Limit file size to 5MB
        max_size = 5 * 1024 * 1024  # 5MB
        if html_file.size > max_size:
            raise ValidationError("File size exceeds the maximum allowed limit (5MB).")

        return html_file