# example/views.py
from datetime import datetime,time

from django.http import HttpResponse
from django.shortcuts import render
from django.core.files.uploadedfile import InMemoryUploadedFile
from bs4 import BeautifulSoup
import pandas as pd
import re
import io
from .forms import GPayForm

def parse_transactions(transaction_str):

        transaction = {}

        # Extracting amount
        amount_start = transaction_str.find('₹') + 1
        amount_end = transaction_str.find('.', amount_start) + 3
        transaction['amount_simple'] = float(transaction_str[amount_start:amount_end].replace(',', ''))
        transaction['Account/Cat'] = "BULK IMPORT"
        transaction['Memo'] = "BULK IMPORT"
        # Extracting transaction type
        if 'Received' in transaction_str:
            transaction['Type'] = 'Credit'
            transaction['Amount'] = f"+{transaction['amount_simple']}"
            transaction['Credit'] = f"{transaction['amount_simple']}"
        elif 'Sent' in transaction_str:
            transaction['Type'] = 'Debit'
            transaction['Amount'] = f"-{transaction['amount_simple']}"
            transaction['Debit'] = f"{transaction['amount_simple']}"
            
        elif 'Paid' in transaction_str:
            transaction['Type'] = 'Debit'
            transaction['Amount'] = f"-{transaction['amount_simple']}"
            transaction['Debit'] = f"{transaction['amount_simple']}"
            
        else:
            transaction['Amount'] = f"{transaction['amount_simple']}"
            transaction['Type'] = 'Unknown'
            
        # Extracting date using regular expression
        date_match = re.search(r'(\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\b \d{1,2}, \d{4})', transaction_str)
        if date_match:
            
            # Get the start and end positions of the matched date
            
            date_str = date_match.group(0)
            try:
                transaction['Date'] = datetime.strptime(date_str, '%b %d, %Y')
            except ValueError:
                transaction['Date'] = datetime.strptime(date_str, '%b %d, %Y, %I:%M:%S %p %Z')
            

        # Extracting recipient and additional details
        if 'to' in transaction_str:
            recipient_start = transaction_str.find('to') + 3
            recipient_end = transaction_str.find('using') if 'using' in transaction_str else len(transaction_str)
            
            if not 'using' in transaction_str and date_match:
                recipient_end =  date_match.start() if  date_match.start() else len(transaction_str)

            transaction['Payee'] = transaction_str[recipient_start:recipient_end].strip()
        elif 'using' in transaction_str:
            recipient_start = transaction_str.find('using') + 6
            recipient_end = transaction_str.find(' ', recipient_start)
            transaction['Payee'] = transaction_str[recipient_start:recipient_end].strip()
        else:
            transaction['Payee'] = 'Unknown'




        # Extracting status
        status_match = re.search(r'(Pending|Completed|Cancelled|Failed)', transaction_str)
        if status_match:
            transaction['status'] = status_match.group(1)
        else:
            print(transaction_str)
        return transaction


def parse_v1(html,start_date,end_date):
    if start_date:
        start_date = datetime.combine(start_date,datetime.min.time())
    if end_date: 
        end_date = datetime.combine(end_date,datetime.max.time()) 
    soup = BeautifulSoup(html, 'html.parser')
    
    transactions = []

    outer_cells = soup.find_all(class_='outer-cell mdl-cell mdl-cell--12-col mdl-shadow--2dp')
    for outer_cell in outer_cells:
        test_text = outer_cell.get_text(separator=' ').strip().replace('\n', ' ').replace('\u202f', ' ').strip()
        test_text = test_text.replace('           ', ' ')
        test_text = test_text.replace('  ', ' ')
        test_text = test_text.replace('   ', ' ')
        test_text = test_text.replace('  ', ' ')
        try:
            transaction = parse_transactions(test_text)
            if transaction:
                if start_date and end_date:
                    if ( start_date <= transaction.get("Date") <=end_date):
                        transactions.append(transaction)
                else:
                    transactions.append(transaction)
        except Exception as e:
            print(e)
    return transactions

def gpay_to_csv(request):
    form = GPayForm()
    if request.method == 'POST':
        form = GPayForm(request.POST,  request.FILES)
        if form.is_valid():
            # Process the form data if needed
            html_file = form.cleaned_data['html_file']
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            
            if isinstance(html_file, InMemoryUploadedFile):
                content = html_file.read()
                
                content_str = content.decode('utf-8')
                transactions = parse_v1(content_str,start_date,end_date)
                print(transactions)
                df = pd.DataFrame(transactions)

                df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
                
                # Create an in-memory CSV file
                csv_buffer = io.StringIO()
                df.to_csv(csv_buffer, index=False)

                # Set up the response
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="data.csv"'

                # Write the CSV content to the response
                response.write(csv_buffer.getvalue())
                
                return response 
    return render(request, "gpayparser/index.html",{'form': form})


def process_gpay_data(request):
    if request.method == "POST":
        gpay_data = request.POST.get("gpay_data")
        # Process the gpay_data as needed
        # Example: Convert the data to CSV, save to a file, etc.
        return HttpResponse(f"Thank you for submitting! Data received:\n{gpay_data}")

    return HttpResponse("Invalid request")
