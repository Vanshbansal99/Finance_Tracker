from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import Transaction, Category
from django.db.models import Sum
from django.http import HttpResponse
import csv
from datetime import date
from decimal import Decimal

from django.utils.safestring import mark_safe
import json

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Automatically log the user in after signup
            login(request, user)
            return redirect('dashboard')  # Or wherever you want to take them
    else:
        form = UserCreationForm()
    return render(request, 'tracker/signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'tracker/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

from datetime import date
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Transaction

@login_required
@login_required
def dashboard(request):
    user = request.user
    transactions = Transaction.objects.filter(user=user)

    # Calculate total income across all time
    total_income = transactions.filter(transaction_type='Income').aggregate(Sum('amount'))['amount__sum'] or 0

    # Calculate total expense across all time
    total_expense = transactions.filter(transaction_type='Expense').aggregate(Sum('amount'))['amount__sum'] or 0

    # Total balance = total income - total expense
    total_balance = total_income - total_expense

    # Monthly income
    today = date.today()
    monthly_income = transactions.filter(
        transaction_type='Income',
        date__year=today.year,
        date__month=today.month
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    # Monthly expenses
    monthly_expenses = transactions.filter(
        transaction_type='Expense',
        date__year=today.year,
        date__month=today.month
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    savings = monthly_income - monthly_expenses

    return render(request, 'tracker/dashboard.html', {
        'total_income': total_income,
        'total_expense': total_expense,
        'total_balance': total_balance,
        'monthly_income': monthly_income,
        'monthly_expenses': monthly_expenses,
        'savings': savings
    })

@login_required
@login_required
def add_transaction(request):
    if request.method == 'POST':
        t_type = request.POST['transaction_type']
        description = request.POST['description']
        date = request.POST['date']
        
        try:
            amount = Decimal(request.POST['amount'])
        except:
            return HttpResponse("Invalid amount", status=400)
        
        if t_type not in ['Income', 'Expense']:
            return HttpResponse("Invalid transaction type", status=400)

        Transaction.objects.create(
            user=request.user,
            transaction_type=t_type,
            description=description,
            amount=amount,
            date=date
        )
        return redirect('dashboard')

    return render(request, 'add_transaction.html')

@login_required
def history(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')
    return render(request, 'tracker/history.html', {'transactions': transactions})

@login_required
def export_csv(request):
    transactions = Transaction.objects.filter(user=request.user)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="transactions.csv"'
    writer = csv.writer(response)
    writer.writerow(['Type', 'Category', 'Amount', 'Date', 'Description'])
    for t in transactions:
        writer.writerow([t.type, t.category.name if t.category else '', t.amount, t.date, t.description])
    return response
@login_required
def report(request):
    user = request.user
    transactions = Transaction.objects.filter(user=user)

    total_income = transactions.filter(transaction_type='Income').aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = transactions.filter(transaction_type='Expense').aggregate(Sum('amount'))['amount__sum'] or 0

    # Monthly trend data
    from django.db.models.functions import ExtractMonth
    from calendar import month_name

    monthly_data = transactions.annotate(month=ExtractMonth('date')) \
        .values('month', 'transaction_type') \
        .annotate(total=Sum('amount')) \
        .order_by('month')

    # Build month-wise data
    month_labels = []
    income_data = []
    expense_data = []

    for month_num in range(1, 13):
        month_labels.append(month_name[month_num])
        income = next((item['total'] for item in monthly_data if item['month'] == month_num and item['transaction_type'] == 'Income'), 0)
        expense = next((item['total'] for item in monthly_data if item['month'] == month_num and item['transaction_type'] == 'Expense'), 0)
        income_data.append(float(income))
        expense_data.append(float(expense))

    return render(request, 'tracker/report.html', {
        'total_income': total_income,
        'total_expense': total_expense,
        'month_labels_json': json.dumps(month_labels),
        'income_data_json': json.dumps(income_data),
        'expense_data_json': json.dumps(expense_data),
    })
# def report_view(request):
#     user = request.user
#     transactions = Transaction.objects.filter(user=user)

#     # Example data preparation (you may already have this logic)
#     total_income = float(transactions.filter(transaction_type='Income').aggregate(Sum('amount'))['amount__sum'] or 0)
#     total_expense = float(transactions.filter(transaction_type='Expense').aggregate(Sum('amount'))['amount__sum'] or 0)

#     # Suppose you prepared these lists:
#     month_labels = ['Jan', 'Feb', 'Mar']  # Replace with real month names
#     income_data = [1000, 1500, 1200]      # Replace with real sums
#     expense_data = [500, 800, 600]        # Replace with real sums

#     return render(request, 'tracker/report.html', {
#         'total_income': total_income,
#         'total_expense': total_expense,
#         'month_labels': month_labels,
#         'income_data': income_data,
#         'expense_data': expense_data,
#     })

context = {
    'month_labels_json': json.dumps(['January', 'February', 'March']),  # this will output ["January", "February", "March"]
    'income_data_json': json.dumps([100, 200, 150]),
    'expense_data_json': json.dumps([50, 80, 60]),
    'total_income': 450,
    'total_expense': 190,
}