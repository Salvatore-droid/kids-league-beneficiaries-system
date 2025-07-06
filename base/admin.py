from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(User)
admin.site.register(UserProfile)
admin.site.register(Institution)
admin.site.register(Beneficiary)
admin.site.register(Payment)
admin.site.register(AcademicPerformance)
admin.site.register(ActivityLog)
admin.site.register(Event)
admin.site.register(Notification)
