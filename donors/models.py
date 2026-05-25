from django.db import models
from accounts.models import CustomUser
import os


def donation_certificate_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'certificate_{instance.donor.id}_{instance.id}.{ext}'
    return os.path.join('certificates', f'donor_{instance.donor.id}', filename)


def achievement_badge_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'badge_{instance.id}.{ext}'
    return os.path.join('badges', f'achievement_{instance.id}', filename)


class BloodGroup(models.Model):
    BLOOD_TYPES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('O+', 'O+'), ('O-', 'O-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
    ]

    blood_type = models.CharField(max_length=3, choices=BLOOD_TYPES, unique=True)

    def __str__(self):
        return self.blood_type


class Donor(models.Model):
    STATUS_CHOICES = [
        ('available',   'Available'),
        ('busy',        'Busy'),
        ('unavailable', 'Unavailable'),
    ]

    LOCATION_CHOICES = [
        ('campus',     'UAP Campus'),
        ('uttara',     'Uttara'),
        ('gulshan',    'Gulshan'),
        ('banani',     'Banani'),
        ('dhanmondi',  'Dhanmondi'),
        ('mirpur',     'Mirpur'),
    ]

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    blood_group = models.ForeignKey(BloodGroup, on_delete=models.CASCADE)
    availability_status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='available')
    can_donate_again = models.BooleanField(default=True)
    location = models.CharField(max_length=20, choices=LOCATION_CHOICES, default='campus')
    emergency_response = models.BooleanField(default=False)
    last_donation_date = models.DateField(null=True, blank=True)
    total_donations = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.blood_group}"


class DonationHistory(models.Model):
    STATUS_CHOICES = [
        ('pending',   'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    VERIFICATION_STATUS_CHOICES = [
        ('pending',  'Pending Verification'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ]

    donor = models.ForeignKey(Donor, on_delete=models.CASCADE, related_name='donations')
    donation_date = models.DateField()
    units_donated = models.DecimalField(max_digits=3, decimal_places=1, default=1.0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='completed')
    hospital = models.CharField(max_length=200, blank=True)
    certificate = models.FileField(
        upload_to=donation_certificate_path,
        blank=True, null=True,
        help_text="Upload donation certificate (PDF, JPG, PNG)"
    )
    # Verification fields
    verification_status = models.CharField(
        max_length=10,
        choices=VERIFICATION_STATUS_CHOICES,
        default='pending'
    )
    verified_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='verified_donations'
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.donor.user.username} - {self.donation_date} [{self.verification_status}]"

    def delete(self, *args, **kwargs):
        if self.certificate:
            if os.path.isfile(self.certificate.path):
                os.remove(self.certificate.path)
        super().delete(*args, **kwargs)


class Achievement(models.Model):
    BADGE_TYPES = [
        ('bronze',   'Bronze'),
        ('silver',   'Silver'),
        ('gold',     'Gold'),
        ('platinum', 'Platinum'),
        ('hero',     'Hero'),
    ]

    donor = models.ForeignKey(Donor, on_delete=models.CASCADE, related_name='achievements')
    badge_type = models.CharField(max_length=10, choices=BADGE_TYPES)
    title = models.CharField(max_length=100)
    description = models.TextField()
    badge_icon = models.ImageField(
        upload_to=achievement_badge_path,
        blank=True, null=True,
        help_text="Badge icon image"
    )
    achieved_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.donor.user.username} - {self.badge_type} - {self.title}"

    def delete(self, *args, **kwargs):
        if self.badge_icon:
            if os.path.isfile(self.badge_icon.path):
                os.remove(self.badge_icon.path)
        super().delete(*args, **kwargs)


class DonationDrive(models.Model):
    STATUS_CHOICES = [
        ('upcoming',   'Upcoming'),
        ('active',     'Active'),
        ('completed',  'Completed'),
        ('cancelled',  'Cancelled'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    venue = models.CharField(max_length=300)
    target_units = models.IntegerField(default=10)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='upcoming')

    # Who created and manages this drive
    created_by = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        related_name='created_drives'
    )
    coordinators = models.ManyToManyField(
        CustomUser,
        through='DriveCoordinator',
        through_fields=('drive', 'user'),
        related_name='coordinating_drives',
        blank=True
    )

    # Which blood groups are most needed
    target_blood_groups = models.ManyToManyField(BloodGroup, blank=True)

    # Partner organization (e.g. BDRCS, Sandhani, Quantum)
    partner_organization = models.CharField(max_length=200, blank=True)

    # Approval by faculty advisor
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='approved_drives'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.title} — {self.date}"

    @property
    def registrations_count(self):
        return self.registrations.count()

    @property
    def donations_collected(self):
        return self.registrations.filter(donated=True).count()


class DriveCoordinator(models.Model):
    """Through model linking a user to a specific drive as coordinator."""
    drive = models.ForeignKey(DonationDrive, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)
    assigned_by = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL,
        null=True, related_name='coordinator_assignments'
    )

    class Meta:
        unique_together = ['drive', 'user']

    def __str__(self):
        return f"{self.user.username} → {self.drive.title}"


class DriveRegistration(models.Model):
    """Donor registers to attend a drive."""
    drive = models.ForeignKey(DonationDrive, on_delete=models.CASCADE, related_name='registrations')
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE)
    registered_at = models.DateTimeField(auto_now_add=True)
    donated = models.BooleanField(default=False)  # marked by coordinator on the day
    donation_record = models.OneToOneField(
        DonationHistory, on_delete=models.SET_NULL,
        null=True, blank=True
    )

    class Meta:
        unique_together = ['drive', 'donor']

    def __str__(self):
        return f"{self.donor.user.username} @ {self.drive.title}"
