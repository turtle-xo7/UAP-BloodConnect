from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('student', 'Student'),
        ('faculty', 'Faculty'),
        ('admin', 'Administrator'),
    )

    ROLE_CHOICES = (
        ('super_admin',       'Super Admin'),
        ('faculty_advisor',   'Faculty Advisor'),
        ('medical_verifier',  'Medical Verifier'),
        ('club_president',    'Club President'),
        ('club_secretary',    'Club Secretary'),
        ('club_moderator',    'Club Moderator'),
        ('camp_coordinator',  'Camp Coordinator'),
        ('donor',             'Donor'),
        ('student',           'Student'),
    )

    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='student')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    uap_id = models.CharField(max_length=20, unique=True)
    is_verified = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=15, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} ({self.uap_id})"

    # ─── Role helper properties ───

    @property
    def is_super_admin(self):
        return self.role == 'super_admin' or self.is_superuser

    @property
    def is_faculty_advisor(self):
        return self.role in ('super_admin', 'faculty_advisor') or self.is_superuser

    @property
    def is_medical_verifier(self):
        return self.role in ('super_admin', 'faculty_advisor', 'medical_verifier') or self.is_superuser

    @property
    def is_club_president(self):
        return self.role in ('super_admin', 'faculty_advisor', 'club_president') or self.is_superuser

    @property
    def is_club_secretary(self):
        return self.role in ('super_admin', 'faculty_advisor', 'club_president', 'club_secretary') or self.is_superuser

    @property
    def is_club_moderator(self):
        return self.role in ('super_admin', 'faculty_advisor', 'club_president', 'club_moderator') or self.is_superuser

    @property
    def is_management(self):
        """True for anyone with elevated permissions (tier 1–3)."""
        return self.role in (
            'super_admin', 'faculty_advisor', 'medical_verifier',
            'club_president', 'club_secretary', 'club_moderator', 'camp_coordinator'
        ) or self.is_superuser

    def get_role_display_badge(self):
        """Returns CSS class for the role badge."""
        badges = {
            'super_admin':      'badge-role-superadmin',
            'faculty_advisor':  'badge-role-advisor',
            'medical_verifier': 'badge-role-medical',
            'club_president':   'badge-role-president',
            'club_secretary':   'badge-role-secretary',
            'club_moderator':   'badge-role-moderator',
            'camp_coordinator': 'badge-role-coordinator',
            'donor':            'badge-role-donor',
            'student':          'badge-role-student',
        }
        return badges.get(self.role, 'badge-role-student')


class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    total_donations = models.IntegerField(default=0)
    points = models.IntegerField(default=0)
    date_of_birth = models.DateField(null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    blood_group = models.CharField(max_length=5, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"
