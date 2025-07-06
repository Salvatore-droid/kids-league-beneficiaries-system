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
    
    path('financial/', views.financial_dashboard, name='financial_dashboard'),
    path('financial/aid/', views.financial_aid_list, name='financial_aid_list'),
    path('financial/aid/add/', views.add_financial_aid, name='add_financial_aid'),
    path('financial/aid/<int:pk>/', views.financial_aid_detail, name='financial_aid_detail'),
    path('financial/aid/<int:pk>/update-status/', views.update_financial_aid_status, name='update_financial_aid_status'),
    path('financial/reports/', views.financial_reports, name='financial_reports'),


    path('performance/', views.performance_dashboard, name='performance_dashboard'),
    path('performance/api/', views.performance_data_api, name='performance_data_api'),
    path('performance/export/', views.export_performance_report, name='export_performance_report'),
]