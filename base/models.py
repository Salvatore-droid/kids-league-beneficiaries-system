from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.validators import RegexValidator

class User(AbstractUser):
    """
    Custom User model with extended fields and proper authentication handling.
    """
    
    # User type choices
    USER_TYPE_CHOICES = (
        ('admin', 'Administrator'),
        ('staff', 'Staff Member'),
        ('sponsor', 'Sponsor'),
        ('beneficiary', 'Beneficiary'),
    )
    
    # Make email unique and required
    email = models.EmailField(
        _('email address'),
        unique=True,
        error_messages={
            'unique': _("A user with that email already exists."),
        }
    )
    
    # User type field with default
    user_type = models.CharField(
        max_length=12,
        choices=USER_TYPE_CHOICES,
        default='staff',
        verbose_name=_('user type')
    )
    
    # Phone number with validation
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(
        validators=[phone_regex],
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_('phone number')
    )
    
    # Profile picture handling
    profile_picture = models.ImageField(
        upload_to='profile_pics/',
        blank=True,
        null=True,
        verbose_name=_('profile picture')
    )
    
    # Email verification fields
    email_verified = models.BooleanField(
        default=False,
        verbose_name=_('email verified')
    )
    verification_token = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('verification token')
    )
    
    # Security-related fields
    last_password_reset = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('last password reset')
    )
    
    # Override groups and permissions to avoid clashes
    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        help_text=_('The groups this user belongs to.'),
        related_name='custom_user_set',
        related_query_name='custom_user',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name='custom_user_set',
        related_query_name='custom_user',
    )
    
    # Use email as the username field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
    
    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.email})"
    
    def save(self, *args, **kwargs):
        # Ensure username is set if not provided
        if not self.username:
            self.username = self.email
        super().save(*args, **kwargs)
    
    @property
    def is_admin(self):
        return self.user_type == 'admin' or self.is_superuser
    
    @property
    def is_staff_member(self):
        return self.user_type == 'staff' or self.is_staff
    
    @property
    def is_sponsor(self):
        return self.user_type == 'sponsor'
    
    @property
    def is_beneficiary(self):
        return self.user_type == 'beneficiary'

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    nationality = models.CharField(max_length=100, blank=True, null=True)
    id_number = models.CharField(max_length=20, blank=True, null=True)
    
    def __str__(self):
        return f"Profile for {self.user.username}"



class Institution(models.Model):
    INSTITUTION_TYPES = (
        ('primary', 'Primary School'),
        ('secondary', 'Secondary School'),
        ('college', 'College'),
        ('university', 'University'),
        ('vocational', 'Vocational Training'),
    )
    
    name = models.CharField(max_length=200)
    institution_type = models.CharField(max_length=20, choices=INSTITUTION_TYPES)
    location = models.CharField(max_length=100)
    contact_person = models.CharField(max_length=100)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20)
    partnership_date = models.DateField()
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

class Beneficiary(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )
    
    LEVEL_CHOICES = (
        ('primary', 'Primary'),
        ('secondary', 'Secondary'),
        ('college', 'College'),
        ('university', 'University'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    sponsor = models.ForeignKey('Sponsor', on_delete=models.SET_NULL, null=True, blank=True)
    date_of_birth = models.DateField()
    national_id = models.CharField(max_length=20, blank=True, null=True)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    current_level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    institution = models.ForeignKey(Institution, on_delete=models.SET_NULL, null=True)
    enrollment_date = models.DateField()
    is_active = models.BooleanField(default=True)
    photo = models.ImageField(upload_to='beneficiaries/', blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    expected_graduation = models.DateField(blank=True, null=True)
    sponsorship_start_date = models.DateField(blank=True, null=True)
    sponsorship_end_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('pending', 'Pending'),
        ('graduated', 'Graduated'),
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def status(self):
        if not self.is_active:
            return "Inactive"
        if self.current_level == 'graduated':
            return "Graduated"
        return "Active"
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('beneficiary_detail', kwargs={'pk': self.pk})
    
    class Meta:
        verbose_name_plural = "Beneficiaries"
        ordering = ['last_name', 'first_name']

class Payment(models.Model):
    beneficiary = models.ForeignKey(Beneficiary, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    term = models.CharField(max_length=20)
    academic_year = models.CharField(max_length=10)
    description = models.TextField(blank=True)
    receipt_number = models.CharField(max_length=50)
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    def __str__(self):
        return f"Payment of {self.amount} for {self.beneficiary}"

class AcademicPerformance(models.Model):
    beneficiary = models.ForeignKey(Beneficiary, on_delete=models.CASCADE)
    term = models.CharField(max_length=20)
    academic_year = models.CharField(max_length=10)
    average_score = models.DecimalField(max_digits=5, decimal_places=2)
    rank = models.IntegerField()
    comments = models.TextField(blank=True)
    date_recorded = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return f"Performance for {self.beneficiary} - Term {self.term} {self.academic_year}"

class ActivityLog(models.Model):
    ACTIVITY_TYPES = (
        ('enrollment', 'New Enrollment'),
        ('payment', 'Payment Processed'),
        ('performance', 'Performance Update'),
        ('meeting', 'Meeting'),
        ('training', 'Training Conducted'),
        ('other', 'Other Activity'),
    )
    
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    description = models.TextField()
    date_recorded = models.DateTimeField(auto_now_add=True)
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    related_beneficiary = models.ForeignKey(Beneficiary, on_delete=models.SET_NULL, null=True, blank=True)
    related_institution = models.ForeignKey(Institution, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    def __str__(self):
        return f"{self.get_activity_type_display()} - {self.description[:50]}"

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    location = models.CharField(max_length=200)
    organizer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    link = models.URLField(blank=True, null=True)
    
    def __str__(self):
        return f"Notification for {self.user.username}"

class Sponsor(models.Model):
    name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20)
    address = models.TextField()
    sponsorship_start_date = models.DateField()
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

class FinancialAccount(models.Model):
    ACCOUNT_TYPES = (
        ('bank', 'Bank Account'),
        ('mobile_money', 'Mobile Money'),
        ('cash', 'Cash Account'),
    )
    
    name = models.CharField(max_length=100)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)
    account_number = models.CharField(max_length=50)
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    branch = models.CharField(max_length=100, blank=True, null=True)
    current_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.get_account_type_display()})"

# class Transaction(models.Model):
#     TRANSACTION_TYPES = (
#         ('income', 'Income'),
#         ('expense', 'Expense'),
#         ('transfer', 'Transfer'),
#     )
    
#     PAYMENT_METHODS = (
#         ('cash', 'Cash'),
#         ('check', 'Check'),
#         ('bank_transfer', 'Bank Transfer'),
#         ('mobile_money', 'Mobile Money'),
#         ('credit_card', 'Credit Card'),
#     )
    
#     account = models.ForeignKey(FinancialAccount, on_delete=models.PROTECT)
#     transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
#     amount = models.DecimalField(max_digits=15, decimal_places=2)
#     date = models.DateField()
#     payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
#     reference_number = models.CharField(max_length=100, blank=True, null=True)
#     description = models.TextField()
#     beneficiary = models.ForeignKey(Beneficiary, on_delete=models.SET_NULL, null=True, blank=True)
#     sponsor = models.ForeignKey(Sponsor, on_delete=models.SET_NULL, null=True, blank=True)
#     institution = models.ForeignKey(Institution, on_delete=models.SET_NULL, null=True, blank=True)
#     created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)
    
#     def __str__(self):
#         return f"{self.get_transaction_type_display()} - {self.amount} on {self.date}"
    
#     def save(self, *args, **kwargs):
#         # Update account balance when transaction is saved
#         if not self.pk:  # New transaction
#             if self.transaction_type == 'income':
#                 self.account.current_balance += self.amount
#             elif self.transaction_type == 'expense':
#                 self.account.current_balance -= self.amount
#             self.account.save()
#         super().save(*args, **kwargs)

# class Budget(models.Model):
#     BUDGET_TYPES = (
#         ('sponsorship', 'Sponsorship'),
#         ('operations', 'Operations'),
#         ('programs', 'Programs'),
#         ('fundraising', 'Fundraising'),
#     )
    
#     name = models.CharField(max_length=100)
#     budget_type = models.CharField(max_length=20, choices=BUDGET_TYPES)
#     amount = models.DecimalField(max_digits=15, decimal_places=2)
#     start_date = models.DateField()
#     end_date = models.DateField()
#     description = models.TextField(blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
    
#     def __str__(self):
#         return f"{self.name} ({self.get_budget_type_display()})"
    
#     @property
#     def spent_amount(self):
#         return Transaction.objects.filter(
#             transaction_type='expense',
#             date__gte=self.start_date,
#             date__lte=self.end_date,
#             description__icontains=self.name
#         ).aggregate(Sum('amount'))['amount__sum'] or 0
    
#     @property
#     def remaining_amount(self):
#         return self.amount - self.spent_amount

# class Invoice(models.Model):
#     STATUS_CHOICES = (
#         ('draft', 'Draft'),
#         ('sent', 'Sent'),
#         ('paid', 'Paid'),
#         ('overdue', 'Overdue'),
#         ('cancelled', 'Cancelled'),
#     )
    
#     invoice_number = models.CharField(max_length=50, unique=True)
#     sponsor = models.ForeignKey(Sponsor, on_delete=models.PROTECT)
#     date = models.DateField()
#     due_date = models.DateField()
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
#     amount = models.DecimalField(max_digits=15, decimal_places=2)
#     tax_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
#     discount_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
#     total_amount = models.DecimalField(max_digits=15, decimal_places=2)
#     notes = models.TextField(blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
    
#     def __str__(self):
#         return f"Invoice #{self.invoice_number} - {self.sponsor}"
    
#     def save(self, *args, **kwargs):
#         if not self.invoice_number:
#             # Generate invoice number
#             last_invoice = Invoice.objects.order_by('-id').first()
#             last_number = int(last_invoice.invoice_number.split('-')[1]) if last_invoice else 0
#             self.invoice_number = f"INV-{last_number + 1:05d}"
        
#         self.total_amount = self.amount + self.tax_amount - self.discount_amount
#         super().save(*args, **kwargs)

# class InvoiceItem(models.Model):
#     invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
#     description = models.CharField(max_length=200)
#     quantity = models.DecimalField(max_digits=10, decimal_places=2)
#     unit_price = models.DecimalField(max_digits=15, decimal_places=2)
#     tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
#     amount = models.DecimalField(max_digits=15, decimal_places=2)
    
#     def __str__(self):
#         return f"{self.description} - {self.amount}"
    
#     def save(self, *args, **kwargs):
#         self.amount = self.quantity * self.unit_price * (1 + self.tax_rate / 100)
#         super().save(*args, **kwargs)


class FinancialTransaction(models.Model):
    TRANSACTION_TYPES = (
        ('sponsorship', 'Sponsorship Payment'),
        ('donation', 'Donation'),
        ('expense', 'Expense'),
        ('refund', 'Refund'),
        ('other', 'Other'),
    )
    
    PAYMENT_METHODS = (
        ('bank', 'Bank Transfer'),
        ('mobile', 'Mobile Money'),
        ('cash', 'Cash'),
        ('check', 'Check'),
        ('card', 'Credit/Debit Card'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('reversed', 'Reversed'),
    )
    
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    transaction_date = models.DateField()
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    beneficiary = models.ForeignKey(Beneficiary, on_delete=models.SET_NULL, null=True, blank=True)
    sponsor = models.ForeignKey(Sponsor, on_delete=models.SET_NULL, null=True, blank=True)
    institution = models.ForeignKey(Institution, on_delete=models.SET_NULL, null=True, blank=True)
    reference_number = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    receipt = models.FileField(upload_to='receipts/', blank=True, null=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-transaction_date']
        verbose_name = 'Financial Transaction'
        verbose_name_plural = 'Financial Transactions'
    
    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.amount} {self.currency} ({self.reference_number})"

class Budget(models.Model):
    BUDGET_TYPES = (
        ('annual', 'Annual Budget'),
        ('project', 'Project Budget'),
        ('sponsorship', 'Sponsorship Budget'),
        ('operational', 'Operational Budget'),
    )
    
    name = models.CharField(max_length=200)
    budget_type = models.CharField(max_length=20, choices=BUDGET_TYPES)
    start_date = models.DateField()
    end_date = models.DateField()
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.name} ({self.get_budget_type_display()})"
    
    @property
    def spent_amount(self):
        return FinancialTransaction.objects.filter(
            transaction_date__gte=self.start_date,
            transaction_date__lte=self.end_date,
            status='completed'
        ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    @property
    def remaining_amount(self):
        return self.total_amount - self.spent_amount

class FinancialReport(models.Model):
    REPORT_TYPES = (
        ('monthly', 'Monthly Report'),
        ('quarterly', 'Quarterly Report'),
        ('annual', 'Annual Report'),
        ('sponsorship', 'Sponsorship Report'),
        ('custom', 'Custom Report'),
    )
    
    name = models.CharField(max_length=200)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    start_date = models.DateField()
    end_date = models.DateField()
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    generated_at = models.DateTimeField(auto_now_add=True)
    report_file = models.FileField(upload_to='reports/')
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-generated_at']
    
    def __str__(self):
        return f"{self.name} ({self.get_report_type_display()})"