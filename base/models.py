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

class FinancialAid(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('disbursed', 'Disbursed'),
    )
    
    TERM_CHOICES = (
        ('1', 'Term 1'),
        ('2', 'Term 2'),
        ('3', 'Term 3'),
    )
    
    beneficiary = models.ForeignKey(Beneficiary, on_delete=models.CASCADE, related_name='financial_aids')
    academic_year = models.CharField(max_length=9)  # Format: 2023-2024
    term = models.CharField(max_length=1, choices=TERM_CHOICES)
    amount_requested = models.DecimalField(max_digits=10, decimal_places=2)
    amount_approved = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    request_date = models.DateField(auto_now_add=True)
    approval_date = models.DateField(null=True, blank=True)
    disbursement_date = models.DateField(null=True, blank=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_aids')
    notes = models.TextField(blank=True)
    receipt_number = models.CharField(max_length=50, blank=True)
    payment_method = models.CharField(max_length=50, blank=True)
    
    class Meta:
        ordering = ['-request_date']
        verbose_name_plural = 'Financial Aids'
    
    def __str__(self):
        return f"{self.beneficiary} - {self.get_term_display()} {self.academic_year}"
    
    def save(self, *args, **kwargs):
        # If status is being updated to approved/disbursed, set the appropriate dates
        if self.pk:
            original = FinancialAid.objects.get(pk=self.pk)
            if self.status == 'approved' and original.status != 'approved':
                self.approval_date = timezone.now().date()
            elif self.status == 'disbursed' and original.status != 'disbursed':
                self.disbursement_date = timezone.now().date()
        super().save(*args, **kwargs)

# Add to models.py

class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    level = models.CharField(max_length=20, choices=Beneficiary.LEVEL_CHOICES)
    is_core = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.name} ({self.code})"

class SubjectPerformance(models.Model):
    beneficiary = models.ForeignKey(Beneficiary, on_delete=models.CASCADE, related_name='subject_performances')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    term = models.CharField(max_length=20)
    academic_year = models.CharField(max_length=10)
    score = models.DecimalField(max_digits=5, decimal_places=2)
    grade = models.CharField(max_length=2)
    comments = models.TextField(blank=True)
    date_recorded = models.DateField(auto_now_add=True)
    
    class Meta:
        unique_together = ('beneficiary', 'subject', 'term', 'academic_year')
        ordering = ['academic_year', 'term', 'subject__name']
    
    def __str__(self):
        return f"{self.beneficiary} - {self.subject} ({self.term} {self.academic_year})"

class PerformanceReport(models.Model):
    REPORT_TYPE_CHOICES = (
        ('term', 'Term Report'),
        ('annual', 'Annual Report'),
        ('subject', 'Subject Analysis'),
        ('comparative', 'Comparative Analysis'),
    )
    
    title = models.CharField(max_length=200)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES)
    academic_year = models.CharField(max_length=10)
    term = models.CharField(max_length=20, blank=True, null=True)
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    generated_at = models.DateTimeField(auto_now_add=True)
    report_file = models.FileField(upload_to='performance_reports/', blank=True, null=True)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return self.title