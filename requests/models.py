from django.db import models
from accounts.models import CustomUser
from donors.models import BloodGroup, Donor




class BloodRequest(models.Model):
   URGENCY_CHOICES = [
       ('low', 'Low'),
       ('medium', 'Medium'),
       ('high', 'High'),
       ('critical', 'Critical'),
   ]

   STATUS_CHOICES = [
       ('open', 'Open'),
       ('in_progress', 'In Progress'),
       ('fulfilled', 'Fulfilled'),
       ('closed', 'Closed'),
   ]

   MODERATION_CHOICES = [
       ('pending',  'Pending Review'),
       ('approved', 'Approved'),
       ('rejected', 'Rejected'),
   ]

   LOCATION_CHOICES = [
       ('campus',    'UAP Campus'),
       ('uttara',    'Uttara'),
       ('gulshan',   'Gulshan'),
       ('banani',    'Banani'),
       ('dhanmondi', 'Dhanmondi'),
       ('mirpur',    'Mirpur'),
   ]

   requester = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='blood_requests')
   blood_group = models.ForeignKey(BloodGroup, on_delete=models.CASCADE)
   urgency = models.CharField(max_length=10, choices=URGENCY_CHOICES, default='medium')
   status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='open')
   is_emergency = models.BooleanField(default=False)
   location = models.CharField(max_length=20, choices=LOCATION_CHOICES)
   needed_by_date = models.DateTimeField()
   units_required = models.DecimalField(max_digits=3, decimal_places=1, default=1.0)
   patient_name = models.CharField(max_length=100)
   patient_age = models.IntegerField(null=True, blank=True)
   description = models.TextField(blank=True)
   supporting_document = models.FileField(upload_to='request_documents/', blank=True, null=True)
   # Moderation fields
   moderation_status = models.CharField(
       max_length=10, choices=MODERATION_CHOICES, default='pending'
   )
   moderated_by = models.ForeignKey(
       CustomUser, on_delete=models.SET_NULL,
       null=True, blank=True, related_name='moderated_requests'
   )
   moderated_at = models.DateTimeField(null=True, blank=True)
   moderation_note = models.TextField(blank=True)
   created_at = models.DateTimeField(auto_now_add=True)
   updated_at = models.DateTimeField(auto_now=True)


   def __str__(self):
       return f"Request {self.id} - {self.blood_group} - {self.requester.username}"


   def save(self, *args, **kwargs):
       if self.urgency in ['high', 'critical']:
           self.is_emergency = True
       super().save(*args, **kwargs)




class RequestResponse(models.Model):
   STATUS_CHOICES = [
       ('pending', 'Pending'),
       ('accepted', 'Accepted'),
       ('declined', 'Declined'),
       ('completed', 'Completed'),
   ]


   blood_request = models.ForeignKey(BloodRequest, on_delete=models.CASCADE, related_name='responses')
   donor = models.ForeignKey(Donor, on_delete=models.CASCADE)
   status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
   message = models.TextField(blank=True)
   responded_at = models.DateTimeField(auto_now_add=True)


   class Meta:
       unique_together = ['blood_request', 'donor']


   def __str__(self):
       return f"Response {self.id} - {self.donor.user.username} to Request {self.blood_request.id}"




class Notification(models.Model):
   NOTIFICATION_TYPES = [
       ('new_request', 'New Blood Request'),
       ('matched', 'Request Matched'),
       ('fulfilled', 'Request Fulfilled'),
       ('achievement', 'New Achievement'),
       ('response', 'Response to Your Request'),
   ]


   user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
   notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
   title = models.CharField(max_length=200)
   message = models.TextField()
   is_read = models.BooleanField(default=False)
   action_url = models.CharField(max_length=200, blank=True)
   created_at = models.DateTimeField(auto_now_add=True)


   def __str__(self):
       return f"Notification for {self.user.username} - {self.notification_type}"




class EmergencyBroadcast(models.Model):
   """Emergency message sent to all eligible donors. Requires advisor co-approval."""
   STATUS_CHOICES = [
       ('pending',  'Pending Advisor Approval'),
       ('approved', 'Approved & Sent'),
       ('rejected', 'Rejected'),
   ]

   title = models.CharField(max_length=200)
   message = models.TextField()
   target_blood_groups = models.CharField(max_length=100, blank=True, help_text="Comma-separated, blank = all")
   created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='broadcasts_created')
   approved_by = models.ForeignKey(
       CustomUser, on_delete=models.SET_NULL,
       null=True, blank=True, related_name='broadcasts_approved'
   )
   status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
   sent_at = models.DateTimeField(null=True, blank=True)
   created_at = models.DateTimeField(auto_now_add=True)

   def __str__(self):
       return f"Broadcast: {self.title} [{self.status}]"


# ✅ Move Feedback outside (top-level class)
class Feedback(models.Model):
   RATING_CHOICES = [
       (1, '⭐ Poor'),
       (2, '⭐⭐ Fair'),
       (3, '⭐⭐⭐ Good'),
       (4, '⭐⭐⭐⭐ Very Good'),
       (5, '⭐⭐⭐⭐⭐ Excellent'),
   ]


   name = models.CharField(max_length=100)
   email = models.EmailField()
   rating = models.IntegerField(choices=RATING_CHOICES)
   message = models.TextField()
   created_at = models.DateTimeField(auto_now_add=True)
   is_resolved = models.BooleanField(default=False)


   def __str__(self):
       return f"Feedback from {self.name} - {self.get_rating_display()}"
