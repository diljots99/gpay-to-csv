# example/views.py
from datetime import datetime

from django.http import HttpResponse
from django.shortcuts import render

from .forms import GPayForm


def gpay_to_csv(request):
    form = GPayForm()
    return render(request, "gpayparser/index.html",{'form': form})


def process_gpay_data(request):
    if request.method == "POST":
        gpay_data = request.POST.get("gpay_data")
        # Process the gpay_data as needed
        # Example: Convert the data to CSV, save to a file, etc.
        return HttpResponse(f"Thank you for submitting! Data received:\n{gpay_data}")

    return HttpResponse("Invalid request")
