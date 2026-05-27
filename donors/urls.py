from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.donor_dashboard, name='donor_dashboard'),
    path('register/', views.donor_register, name='donor_register'),
    path('directory/', views.donor_directory, name='donor_directory'),
    path('add-donation/', views.add_donation_history, name='add_donation_history'),
    path('history/', views.donation_history, name='donation_history'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('availability/', views.update_availability, name='update_availability'),
    path('drives/', views.drive_list, name='drive_list'),
    path('drives/create/', views.create_drive, name='create_drive'),
    path('drives/<int:drive_id>/', views.drive_detail, name='drive_detail'),
    path('drives/<int:drive_id>/register/', views.register_for_drive, name='register_for_drive'),
    path('drives/<int:drive_id>/unregister/', views.unregister_from_drive, name='unregister_from_drive'),
    path('drives/<int:drive_id>/attendance/<int:registration_id>/', views.mark_attendance, name='mark_attendance'),
]
