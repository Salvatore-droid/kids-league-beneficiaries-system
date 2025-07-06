from django.urls import path
from . import views

urlpatterns = [
    
    path('', views.dashboard, name='dashboard'),
    path('api/beneficiary-distribution/', views.get_beneficiary_distribution, name='beneficiary_distribution'),
    path('api/performance-trends/', views.get_performance_trends, name='performance_trends'),
    path('beneficiaries/', views.beneficiaries_list, name='beneficiaries_list'),
    path('beneficiaries/add/', views.add_beneficiary, name='add_beneficiary'),
    path('beneficiaries/<int:pk>/', views.beneficiary_detail, name='beneficiary_detail'),
    path('beneficiaries/<int:pk>/edit/', views.edit_beneficiary, name='edit_beneficiary'),
    path('beneficiaries/<int:pk>/delete/', views.delete_beneficiary, name='delete_beneficiary'),
    path('accounts/login/', views.login_view, name='login_view'),
    path('logout/', views.logout_view, name='logout_view'),
    
    # Add other URLs as needed
]