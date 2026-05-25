from django.contrib import admin
from .models import BloodGroup, Donor, DonationHistory, Achievement, DonationDrive, DriveCoordinator, DriveRegistration


@admin.register(BloodGroup)
class BloodGroupAdmin(admin.ModelAdmin):
   list_display = ['blood_type']
   list_display_links = ['blood_type']


@admin.register(Donor)
class DonorAdmin(admin.ModelAdmin):
   list_display = ['user', 'blood_group', 'availability_status', 'location', 'emergency_response', 'total_donations']
   list_filter = ['blood_group', 'availability_status', 'location', 'emergency_response']
   search_fields = ['user__username', 'user__uap_id', 'user__email']
   readonly_fields = ['created_at']


@admin.register(DonationHistory)
class DonationHistoryAdmin(admin.ModelAdmin):
   list_display = ['donor', 'donation_date', 'units_donated', 'status', 'hospital']
   list_filter = ['status', 'donation_date']
   search_fields = ['donor__user__username', 'hospital']
   readonly_fields = ['created_at']


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
   list_display = ['donor', 'badge_type', 'title', 'achieved_at']
   list_filter = ['badge_type']
   search_fields = ['donor__user__username', 'title']
   readonly_fields = ['achieved_at']


@admin.register(DonationDrive)
class DonationDriveAdmin(admin.ModelAdmin):
   list_display = ['title', 'date', 'status', 'is_approved', 'created_by', 'target_units']
   list_filter = ['status', 'is_approved', 'date']
   search_fields = ['title', 'venue', 'created_by__username']
   readonly_fields = ['created_at', 'updated_at']
   filter_horizontal = ['target_blood_groups']


@admin.register(DriveCoordinator)
class DriveCoordinatorAdmin(admin.ModelAdmin):
   list_display = ['drive', 'user', 'assigned_by', 'assigned_at']
   list_filter = ['drive']
   search_fields = ['user__username', 'drive__title']


@admin.register(DriveRegistration)
class DriveRegistrationAdmin(admin.ModelAdmin):
   list_display = ['drive', 'donor', 'registered_at', 'donated']
   list_filter = ['donated', 'drive']
   search_fields = ['donor__user__username', 'drive__title']
