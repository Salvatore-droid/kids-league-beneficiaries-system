from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Count, Sum, Avg
from .models import *
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.core.paginator import Paginator


@login_required
def dashboard(request):
    # Beneficiary statistics
    total_beneficiaries = Beneficiary.objects.filter(is_active=True).count()
    beneficiaries_by_level = Beneficiary.objects.filter(is_active=True).values('current_level').annotate(count=Count('id'))
    beneficiaries_by_gender = Beneficiary.objects.filter(is_active=True).values('gender').annotate(count=Count('id'))
    
    # Institution statistics
    total_institutions = Institution.objects.filter(is_active=True).count()
    institutions_by_type = Institution.objects.filter(is_active=True).values('institution_type').annotate(count=Count('id'))
    
    # Payment statistics
    total_payments = Payment.objects.filter(
        payment_date__year=datetime.now().year
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Performance statistics
    graduation_rate = 92  # This would be calculated from your data
    
    # Recent activities
    recent_activities = ActivityLog.objects.all().order_by('-date_recorded')[:5]
    
    # Upcoming events
    upcoming_events = Event.objects.filter(
        start_date__gte=datetime.now(),
        is_active=True
    ).order_by('start_date')[:3]
    
    # Unread notifications for the user
    unread_notifications = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).count()
    
    context = {
        'total_beneficiaries': total_beneficiaries,
        'beneficiaries_by_level': list(beneficiaries_by_level),
        'beneficiaries_by_gender': list(beneficiaries_by_gender),
        'total_institutions': total_institutions,
        'institutions_by_type': list(institutions_by_type),
        'total_payments': total_payments,
        'graduation_rate': graduation_rate,
        'recent_activities': recent_activities,
        'upcoming_events': upcoming_events,
        'unread_notifications': unread_notifications,
        'user': request.user,  # Changed from User to request.user
    }
    
    return render(request, 'dashboard.html', context)


def get_beneficiary_distribution(request):
    # This would be called via AJAX for the chart data
    level_data = Beneficiary.objects.filter(is_active=True).values('current_level').annotate(count=Count('id'))
    gender_data = Beneficiary.objects.filter(is_active=True).values('gender').annotate(count=Count('id'))
    
    return JsonResponse({
        'level_data': list(level_data),
        'gender_data': list(gender_data),
    })

def get_performance_trends(request):
    # This would be called via AJAX for the chart data
    term = request.GET.get('term', '1')
    performance_data = AcademicPerformance.objects.filter(term=term).values('academic_year').annotate(
        avg_score=Avg('average_score')
    ).order_by('academic_year')
    
    return JsonResponse({
        'performance_data': list(performance_data),
    })



def login_view(request):
    if request.method == "POST":
        username = request.POST.get('email')  # Using email as username
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)  # Always call login() to set up the session        
            messages.success(request, 'Login successful')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid email or password')

    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been Logged out successfully')
    return redirect('login_view')

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Beneficiary, Institution, Sponsor


@login_required
def beneficiaries_list(request):
    # Get filter parameters
    education_level = request.GET.get('education_level')
    status_filter = request.GET.get('status')
    year = request.GET.get('year')
    sponsor_id = request.GET.get('sponsor')
    search_query = request.GET.get('search', '')

    # Start with all active beneficiaries
    beneficiaries = Beneficiary.objects.filter(is_active=True).select_related('institution', 'sponsor')

    # Apply filters
    if education_level:
        beneficiaries = beneficiaries.filter(current_level=education_level)
    
    if status_filter:
        if status_filter == 'active':
            beneficiaries = beneficiaries.filter(is_active=True, current_level__ne='graduated')
        elif status_filter == 'inactive':
            beneficiaries = beneficiaries.filter(is_active=False)
        elif status_filter == 'pending':
            beneficiaries = beneficiaries.filter(is_active=True, status='pending')
        elif status_filter == 'graduated':
            beneficiaries = beneficiaries.filter(current_level='graduated')

    if year:
        beneficiaries = beneficiaries.filter(enrollment_date__year=year)

    if sponsor_id:
        beneficiaries = beneficiaries.filter(sponsor__id=sponsor_id)

    if search_query:
        beneficiaries = beneficiaries.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(national_id__icontains=search_query)
        )

    # Get distinct enrollment years for filter dropdown
    enrollment_years = Beneficiary.objects.dates('enrollment_date', 'year').order_by('-enrollment_date')

    # Pagination
    paginator = Paginator(beneficiaries, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'beneficiaries': page_obj,
        'education_levels': Beneficiary.LEVEL_CHOICES,
        'enrollment_years': [date.year for date in enrollment_years],
        'sponsors': Sponsor.objects.all(),
        'unread_notifications': Notification.objects.filter(user=request.user, is_read=False).count(),
        'is_paginated': paginator.num_pages > 1,
    }

    return render(request, 'benef.html', context)

# views.py
# views.py
@login_required
def add_beneficiary(request):
    if request.method == 'POST':
        # Get all form data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        gender = request.POST.get('gender')
        date_of_birth = request.POST.get('date_of_birth')
        national_id = request.POST.get('national_id')
        phone_number = request.POST.get('phone_number')
        email = request.POST.get('email')
        current_level = request.POST.get('current_level')
        institution_id = request.POST.get('institution')
        enrollment_date = request.POST.get('enrollment_date')
        sponsor_id = request.POST.get('sponsor')
        photo = request.FILES.get('photo')
        
        # Validate required fields
        errors = {}
        if not first_name:
            errors['first_name'] = 'First name is required'
        if not last_name:
            errors['last_name'] = 'Last name is required'
        if not date_of_birth:
            errors['date_of_birth'] = 'Date of birth is required'
        if not gender:
            errors['gender'] = 'Gender is required'
        if not current_level:
            errors['current_level'] = 'Education level is required'
        if not enrollment_date:
            errors['enrollment_date'] = 'Enrollment date is required'
            
        if errors:
            # Get all institutions and sponsors for the form
            institutions = Institution.objects.all()
            sponsors = Sponsor.objects.all()
            
            context = {
                'errors': errors,
                'institutions': institutions,
                'sponsors': sponsors,
                'education_levels': Beneficiary.LEVEL_CHOICES,
                'genders': Beneficiary.GENDER_CHOICES,
                'unread_notifications': Notification.objects.filter(user=request.user, is_read=False).count(),
                'form_data': request.POST  # To repopulate form
            }
            return render(request, 'beneficiary_add.html', context)
        
        try:
            # Create the beneficiary
            beneficiary = Beneficiary(
                first_name=first_name,
                last_name=last_name,
                gender=gender,
                date_of_birth=date_of_birth,
                national_id=national_id,
                phone_number=phone_number,
                email=email,
                current_level=current_level,
                institution_id=institution_id,
                enrollment_date=enrollment_date,
                sponsor_id=sponsor_id,
                is_active=True
            )
            
            if photo:
                beneficiary.photo = photo
                
            beneficiary.save()
            
            messages.success(request, 'Beneficiary added successfully!')
            return redirect('beneficiary_detail', pk=beneficiary.pk)
            
        except Exception as e:
            messages.error(request, f'Error saving beneficiary: {str(e)}')
            return redirect('add_beneficiary')
    
    else:
        # GET request - show empty form
        institutions = Institution.objects.all()
        sponsors = Sponsor.objects.all()
        
        context = {
            'institutions': institutions,
            'sponsors': sponsors,
            'education_levels': Beneficiary.LEVEL_CHOICES,
            'genders': Beneficiary.GENDER_CHOICES,
            'unread_notifications': Notification.objects.filter(user=request.user, is_read=False).count()
        }
        return render(request, 'beneficiary_add.html', context)

@login_required
def beneficiary_detail(request, pk):
    beneficiary = get_object_or_404(Beneficiary, pk=pk)
    payments = Payment.objects.filter(beneficiary=beneficiary).order_by('-payment_date')
    performances = AcademicPerformance.objects.filter(beneficiary=beneficiary).order_by('-academic_year', 'term')

    context = {
        'beneficiary': beneficiary,
        'payments': payments,
        'performances': performances,
        'unread_notifications': Notification.objects.filter(user=request.user, is_read=False).count(),
    }
    return render(request, 'beneficiary_detail.html', context)

# views.py
@login_required
def edit_beneficiary(request, pk):
    beneficiary = get_object_or_404(Beneficiary, pk=pk)
    
    if request.method == 'POST':
        # Get all form data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        gender = request.POST.get('gender')
        date_of_birth = request.POST.get('date_of_birth')
        national_id = request.POST.get('national_id')
        phone_number = request.POST.get('phone_number')
        email = request.POST.get('email')
        current_level = request.POST.get('current_level')
        institution_id = request.POST.get('institution')
        enrollment_date = request.POST.get('enrollment_date')
        sponsor_id = request.POST.get('sponsor')
        photo = request.FILES.get('photo')
        is_active = request.POST.get('is_active') == 'on'
        
        # Validate required fields
        errors = {}
        if not first_name:
            errors['first_name'] = 'First name is required'
        if not last_name:
            errors['last_name'] = 'Last name is required'
        if not date_of_birth:
            errors['date_of_birth'] = 'Date of birth is required'
        if not gender:
            errors['gender'] = 'Gender is required'
        if not current_level:
            errors['current_level'] = 'Education level is required'
        if not enrollment_date:
            errors['enrollment_date'] = 'Enrollment date is required'
            
        if errors:
            # Get all institutions and sponsors for the form
            institutions = Institution.objects.all()
            sponsors = Sponsor.objects.all()
            
            context = {
                'beneficiary': beneficiary,
                'errors': errors,
                'institutions': institutions,
                'sponsors': sponsors,
                'education_levels': Beneficiary.LEVEL_CHOICES,
                'genders': Beneficiary.GENDER_CHOICES,
                'unread_notifications': Notification.objects.filter(user=request.user, is_read=False).count(),
                'form_data': request.POST  # To repopulate form
            }
            return render(request, 'beneficiary_edit.html', context)
        
        try:
            # Update the beneficiary
            beneficiary.first_name = first_name
            beneficiary.last_name = last_name
            beneficiary.gender = gender
            beneficiary.date_of_birth = date_of_birth
            beneficiary.national_id = national_id
            beneficiary.phone_number = phone_number
            beneficiary.email = email
            beneficiary.current_level = current_level
            beneficiary.institution_id = institution_id
            beneficiary.enrollment_date = enrollment_date
            beneficiary.sponsor_id = sponsor_id
            beneficiary.is_active = is_active
            
            if photo:
                beneficiary.photo = photo
                
            beneficiary.save()
            
            messages.success(request, 'Beneficiary updated successfully!')
            return redirect('beneficiary_detail', pk=beneficiary.pk)
            
        except Exception as e:
            messages.error(request, f'Error updating beneficiary: {str(e)}')
            return redirect('edit_beneficiary', pk=beneficiary.pk)
    
    else:
        # GET request - show form with current data
        institutions = Institution.objects.all()
        sponsors = Sponsor.objects.all()
        
        context = {
            'beneficiary': beneficiary,
            'institutions': institutions,
            'sponsors': sponsors,
            'education_levels': Beneficiary.LEVEL_CHOICES,
            'genders': Beneficiary.GENDER_CHOICES,
            'unread_notifications': Notification.objects.filter(user=request.user, is_read=False).count()
        }
        return render(request, 'beneficiary_edit.html', context)

@login_required
def delete_beneficiary(request, pk):
    beneficiary = get_object_or_404(Beneficiary, pk=pk)
    if request.method == 'POST':
        beneficiary.is_active = False
        beneficiary.save()
        messages.success(request, f'{beneficiary.full_name} has been deactivated.')
        return redirect('beneficiaries_list')
    
    context = {
        'beneficiary': beneficiary,
        'unread_notifications': Notification.objects.filter(user=request.user, is_read=False).count(),
    }
    return render(request, 'beneficiary_confirm_delete.html', context)

# @login_required
# def financial_dashboard(request):
#     # Account balances
#     accounts = FinancialAccount.objects.filter(is_active=True)
#     total_balance = accounts.aggregate(Sum('current_balance'))['current_balance__sum'] or 0
    
#     # Recent transactions
#     recent_transactions = Transaction.objects.all().order_by('-date', '-created_at')[:10]
    
#     # Budget overview
#     current_budgets = Budget.objects.filter(
#         start_date__lte=timezone.now().date(),
#         end_date__gte=timezone.now().date()
#     )
    
#     # Income vs Expense
#     today = timezone.now().date()
#     start_of_month = today.replace(day=1)
#     income_expense = Transaction.objects.filter(
#         date__gte=start_of_month,
#         date__lte=today
#     ).values('transaction_type').annotate(
#         total=Sum('amount')
#     )
    
#     # Invoice status
#     invoice_status = Invoice.objects.values('status').annotate(
#         count=Count('id'),
#         total=Sum('total_amount')
#     )
    
#     context = {
#         'accounts': accounts,
#         'total_balance': total_balance,
#         'recent_transactions': recent_transactions,
#         'current_budgets': current_budgets,
#         'income_expense': income_expense,
#         'invoice_status': invoice_status,
#         'unread_notifications': Notification.objects.filter(user=request.user, is_read=False).count(),
#     }
#     return render(request, 'financial_dashboard.html', context)

# @login_required
# def transaction_list(request):
#     transactions = Transaction.objects.all().order_by('-date', '-created_at')
    
#     # Filtering
#     transaction_type = request.GET.get('type')
#     if transaction_type:
#         transactions = transactions.filter(transaction_type=transaction_type)
    
#     account_id = request.GET.get('account')
#     if account_id:
#         transactions = transactions.filter(account_id=account_id)
    
#     date_from = request.GET.get('date_from')
#     if date_from:
#         transactions = transactions.filter(date__gte=date_from)
    
#     date_to = request.GET.get('date_to')
#     if date_to:
#         transactions = transactions.filter(date__lte=date_to)
    
#     # Pagination
#     paginator = Paginator(transactions, 25)
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(page_number)
    
#     context = {
#         'transactions': page_obj,
#         'accounts': FinancialAccount.objects.filter(is_active=True),
#         'transaction_types': Transaction.TRANSACTION_TYPES,
#         'unread_notifications': Notification.objects.filter(user=request.user, is_read=False).count(),
#     }
#     return render(request, 'transaction_list.html', context)

# @login_required
# def add_transaction(request):
#     if request.method == 'POST':
#         form_data = request.POST
#         try:
#             transaction = Transaction(
#                 account_id=form_data.get('account'),
#                 transaction_type=form_data.get('transaction_type'),
#                 amount=form_data.get('amount'),
#                 date=form_data.get('date'),
#                 payment_method=form_data.get('payment_method'),
#                 reference_number=form_data.get('reference_number'),
#                 description=form_data.get('description'),
#                 beneficiary_id=form_data.get('beneficiary'),
#                 sponsor_id=form_data.get('sponsor'),
#                 institution_id=form_data.get('institution'),
#                 created_by=request.user
#             )
#             transaction.save()
#             messages.success(request, 'Transaction recorded successfully!')
#             return redirect('transaction_list')
#         except Exception as e:
#             messages.error(request, f'Error recording transaction: {str(e)}')
    
#     context = {
#         'accounts': FinancialAccount.objects.filter(is_active=True),
#         'beneficiaries': Beneficiary.objects.filter(is_active=True),
#         'sponsors': Sponsor.objects.filter(is_active=True),
#         'institutions': Institution.objects.filter(is_active=True),
#         'transaction_types': Transaction.TRANSACTION_TYPES,
#         'payment_methods': Transaction.PAYMENT_METHODS,
#         'unread_notifications': Notification.objects.filter(user=request.user, is_read=False).count(),
#     }
#     return render(request, 'add_transaction.html', context)

# @login_required
# def budget_list(request):
#     budgets = Budget.objects.all().order_by('-start_date')
    
#     # Filtering
#     budget_type = request.GET.get('type')
#     if budget_type:
#         budgets = budgets.filter(budget_type=budget_type)
    
#     status = request.GET.get('status')
#     if status == 'active':
#         today = timezone.now().date()
#         budgets = budgets.filter(start_date__lte=today, end_date__gte=today)
#     elif status == 'upcoming':
#         today = timezone.now().date()
#         budgets = budgets.filter(start_date__gt=today)
#     elif status == 'completed':
#         today = timezone.now().date()
#         budgets = budgets.filter(end_date__lt=today)
    
#     context = {
#         'budgets': budgets,
#         'budget_types': Budget.BUDGET_TYPES,
#         'unread_notifications': Notification.objects.filter(user=request.user, is_read=False).count(),
#     }
#     return render(request, 'budget_list.html', context)

# @login_required
# def invoice_list(request):
#     invoices = Invoice.objects.all().order_by('-date')
    
#     # Filtering
#     status = request.GET.get('status')
#     if status:
#         invoices = invoices.filter(status=status)
    
#     sponsor_id = request.GET.get('sponsor')
#     if sponsor_id:
#         invoices = invoices.filter(sponsor_id=sponsor_id)
    
#     date_from = request.GET.get('date_from')
#     if date_from:
#         invoices = invoices.filter(date__gte=date_from)
    
#     date_to = request.GET.get('date_to')
#     if date_to:
#         invoices = invoices.filter(date__lte=date_to)
    
#     context = {
#         'invoices': invoices,
#         'sponsors': Sponsor.objects.filter(is_active=True),
#         'status_choices': Invoice.STATUS_CHOICES,
#         'unread_notifications': Notification.objects.filter(user=request.user, is_read=False).count(),
#     }
#     return render(request, 'invoice_list.html', context)

# @login_required
# def view_invoice(request, pk):
#     invoice = get_object_or_404(Invoice, pk=pk)
#     context = {
#         'invoice': invoice,
#         'unread_notifications': Notification.objects.filter(user=request.user, is_read=False).count(),
#     }
#     return render(request, 'view_invoice.html', context)

# @login_required
# def financial_reports(request):
#     report_type = request.GET.get('report', 'income_expense')
    
#     # Default date range - current year
#     today = timezone.now().date()
#     start_date = request.GET.get('start_date', today.replace(month=1, day=1).isoformat())
#     end_date = request.GET.get('end_date', today.isoformat())
    
#     # Convert to date objects
#     start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
#     end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
    
#     # Generate report data based on type
#     report_data = None
#     chart_data = None
    
#     if report_type == 'income_expense':
#         transactions = Transaction.objects.filter(
#             date__gte=start_date_obj,
#             date__lte=end_date_obj
#         ).values('transaction_type').annotate(
#             total=Sum('amount')
#         )
        
#         report_data = {
#             'income': transactions.filter(transaction_type='income').first()['total'] if transactions.filter(transaction_type='income').exists() else 0,
#             'expense': transactions.filter(transaction_type='expense').first()['total'] if transactions.filter(transaction_type='expense').exists() else 0,
#             'net': (transactions.filter(transaction_type='income').first()['total'] if transactions.filter(transaction_type='income').exists() else 0) - 
#                   (transactions.filter(transaction_type='expense').first()['total'] if transactions.filter(transaction_type='expense').exists() else 0)
#         }
        
#         # Monthly breakdown for chart
#         monthly_data = Transaction.objects.filter(
#             date__gte=start_date_obj,
#             date__lte=end_date_obj
#         ).annotate(
#             month=TruncMonth('date')
#         ).values('month', 'transaction_type').annotate(
#             total=Sum('amount')
#         ).order_by('month')
        
#         chart_data = {
#             'labels': [],
#             'income': [],
#             'expense': []
#         }
        
#         current_month = start_date_obj
#         while current_month <= end_date_obj:
#             month_label = current_month.strftime('%b %Y')
#             chart_data['labels'].append(month_label)
            
#             income = next((item['total'] for item in monthly_data 
#                          if item['month'].month == current_month.month 
#                          and item['month'].year == current_month.year
#                          and item['transaction_type'] == 'income'), 0)
#             chart_data['income'].append(float(income))
            
#             expense = next((item['total'] for item in monthly_data 
#                           if item['month'].month == current_month.month 
#                           and item['month'].year == current_month.year
#                           and item['transaction_type'] == 'expense'), 0)
#             chart_data['expense'].append(float(expense))
            
#             # Move to next month
#             if current_month.month == 12:
#                 current_month = current_month.replace(year=current_month.year + 1, month=1)
#             else:
#                 current_month = current_month.replace(month=current_month.month + 1)
    
#     elif report_type == 'budget_vs_actual':
#         budgets = Budget.objects.filter(
#             start_date__lte=end_date_obj,
#             end_date__gte=start_date_obj
#         )
        
#         report_data = []
#         for budget in budgets:
#             actual = Transaction.objects.filter(
#                 transaction_type='expense',
#                 date__gte=budget.start_date,
#                 date__lte=budget.end_date,
#                 description__icontains=budget.name
#             ).aggregate(Sum('amount'))['amount__sum'] or 0
            
#             report_data.append({
#                 'budget': budget,
#                 'actual': actual,
#                 'variance': budget.amount - actual
#             })
    
#     context = {
#         'report_type': report_type,
#         'start_date': start_date,
#         'end_date': end_date,
#         'report_data': report_data,
#         'chart_data': chart_data,
#         'unread_notifications': Notification.objects.filter(user=request.user, is_read=False).count(),
#     }
#     return render(request, 'financial_reports.html', context)


@login_required
def financial_dashboard(request):
    # Financial summary
    current_year = timezone.now().year
    current_month = timezone.now().month
    
    # Transaction summary
    transactions = FinancialTransaction.objects.filter(
        status='completed'
    ).select_related('beneficiary', 'sponsor', 'institution')
    
    # Monthly summary
    monthly_summary = transactions.filter(
        transaction_date__year=current_year
    ).annotate(
        month=ExtractMonth('transaction_date')
    ).values('month').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('month')
    
    # Transaction types summary
    transaction_types = transactions.values('transaction_type').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')
    
    # Recent transactions
    recent_transactions = transactions.order_by('-transaction_date')[:5]
    
    # Budget overview
    active_budgets = Budget.objects.filter(
        is_active=True,
        end_date__gte=timezone.now().date()
    ).annotate(
        spent_amount=Sum('financialtransaction__amount', filter=Q(financialtransaction__status='completed'))
    
    # Sponsorship summary
    sponsorship_summary = transactions.filter(
        transaction_type='sponsorship'
    ).values('sponsor__name').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')[:5]
    
    context = {
        'monthly_summary': list(monthly_summary),
        'transaction_types': list(transaction_types),
        'recent_transactions': recent_transactions,
        'active_budgets': active_budgets,
        'sponsorship_summary': sponsorship_summary,
        'unread_notifications': Notification.objects.filter(user=request.user, is_read=False).count(),
    }
    
    return render(request, 'financial_dashboard.html', context)

@login_required
def transaction_list(request):
    # Filter parameters
    transaction_type = request.GET.get('type')
    status = request.GET.get('status')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    search = request.GET.get('search')
    
    transactions = FinancialTransaction.objects.all().select_related(
        'beneficiary', 'sponsor', 'institution', 'recorded_by'
    ).order_by('-transaction_date')
    
    # Apply filters
    if transaction_type:
        transactions = transactions.filter(transaction_type=transaction_type)
    if status:
        transactions = transactions.filter(status=status)
    if start_date:
        transactions = transactions.filter(transaction_date__gte=start_date)
    if end_date:
        transactions = transactions.filter(transaction_date__lte=end_date)
    if search:
        transactions = transactions.filter(
            Q(reference_number__icontains=search) |
            Q(description__icontains=search) |
            Q(beneficiary__first_name__icontains=search) |
            Q(beneficiary__last_name__icontains=search) |
            Q(sponsor__name__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(transactions, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'transactions': page_obj,
        'transaction_types': FinancialTransaction.TRANSACTION_TYPES,
        'status_choices': FinancialTransaction.STATUS_CHOICES,
        'unread_notifications': Notification.objects.filter(user=request.user, is_read=False).count(),
        'is_paginated': paginator.num_pages > 1,
    }
    
    return render(request, 'financial_transactions.html', context)

@login_required
def add_transaction(request):
    if request.method == 'POST':
        form = FinancialTransactionForm(request.POST, request.FILES)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.recorded_by = request.user
            transaction.save()
            messages.success(request, 'Transaction added successfully!')
            return redirect('transaction_detail', pk=transaction.pk)
    else:
        form = FinancialTransactionForm()
    
    context = {
        'form': form,
        'unread_notifications': Notification.objects.filter(user=request.user, is_read=False).count(),
    }
    return render(request, 'financial_transaction_add.html', context)

@login_required
def transaction_detail(request, pk):
    transaction = get_object_or_404(FinancialTransaction, pk=pk)
    context = {
        'transaction': transaction,
        'unread_notifications': Notification.objects.filter(user=request.user, is_read=False).count(),
    }
    return render(request, 'financial_transaction_detail.html', context)

@login_required
def budget_list(request):
    budgets = Budget.objects.all().order_by('-start_date')
    context = {
        'budgets': budgets,
        'unread_notifications': Notification.objects.filter(user=request.user, is_read=False).count(),
    }
    return render(request, 'financial_budgets.html', context)

@login_required
def generate_report(request):
    if request.method == 'POST':
        form = FinancialReportForm(request.POST)
        if form.is_valid():
            # Generate report logic here
            # This would typically create a PDF or Excel file
            # For now, we'll just simulate it
            
            report = form.save(commit=False)
            report.generated_by = request.user
            report.report_file.name = f"reports/report_{timezone.now().timestamp()}.pdf"
            report.save()
            
            messages.success(request, 'Report generated successfully!')
            return redirect('report_detail', pk=report.pk)
    else:
        form = FinancialReportForm()
    
    context = {
        'form': form,
        'unread_notifications': Notification.objects.filter(user=request.user, is_read=False).count(),
    }
    return render(request, 'financial_report_generate.html', context)