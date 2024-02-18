# example/urls.py
from django.urls import path

from gpayparser.views import gpay_to_csv,process_gpay_data


urlpatterns = [
    path('gpay-to-csv', gpay_to_csv,name="gpay_to_csv"),
    path('process_gpay_data/', process_gpay_data, name='process_gpay_data'),
]