from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('advisor/', views.advisor_dashboard, name='advisor_dashboard'),
    path('advisor/verify/<int:donation_id>/', views.verify_donation, name='verify_donation'),
    path('advisor/moderate/<int:request_id>/', views.moderate_request, name='moderate_request'),
    path('advisor/drive/<int:drive_id>/approve/', views.approve_drive, name='approve_drive'),
    path('advisor/broadcast/<int:broadcast_id>/approve/', views.approve_broadcast, name='approve_broadcast'),
    path('president/', views.president_dashboard, name='president_dashboard'),
    path('president/broadcast/new/', views.create_broadcast, name='create_broadcast'),
    path('manage-roles/', views.manage_roles, name='manage_roles'),
]