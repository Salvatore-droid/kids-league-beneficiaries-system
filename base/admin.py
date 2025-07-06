# admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'user_type', 'is_staff')
    list_filter = ('user_type', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)

class BeneficiaryAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'current_level', 'institution', 'sponsor', 'status')
    list_filter = ('current_level', 'institution', 'sponsor', 'is_active')
    search_fields = ('first_name', 'last_name', 'national_id')
    raw_id_fields = ('user',)
    date_hierarchy = 'enrollment_date'
    ordering = ('last_name', 'first_name')

class SponsorAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_person', 'contact_email', 'is_active')
    search_fields = ('name', 'contact_person', 'contact_email')
    list_filter = ('is_active',)

class InstitutionAdmin(admin.ModelAdmin):
    list_display = ('name', 'institution_type', 'location', 'is_active')
    list_filter = ('institution_type', 'is_active')
    search_fields = ('name', 'location')

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('beneficiary', 'amount', 'payment_date', 'academic_year', 'term')
    list_filter = ('academic_year', 'term')
    search_fields = ('beneficiary__first_name', 'beneficiary__last_name', 'receipt_number')
    date_hierarchy = 'payment_date'

# Unregister the default User admin and register our custom one

admin.site.register(User, CustomUserAdmin)

# Register other models
admin.site.register(UserProfile)
admin.site.register(Institution, InstitutionAdmin)
admin.site.register(Beneficiary, BeneficiaryAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(AcademicPerformance)
admin.site.register(ActivityLog)
admin.site.register(Event)
admin.site.register(Notification)
admin.site.register(Sponsor, SponsorAdmin)
