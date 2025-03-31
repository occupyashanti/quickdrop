from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    USER_TYPE_CHOICES = [
        ('customer', 'Customer'),
        ('worker', 'Worker'),
    ]

    VEHICLE_TYPE_CHOICES = [
        ('bike', 'Motorbike'),
        ('car', 'Car'),
        ('van', 'Van'),
        ('truck', 'Truck'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    phone_regex = RegexValidator(
        regex=r'^[+]?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17)
    address = models.CharField(max_length=255)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    vehicle_type = models.CharField(max_length=5, choices=VEHICLE_TYPE_CHOICES, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    class Meta:
        db_table = 'user_profiles'

class JobPosting(models.Model):
    JOB_TYPE_CHOICES = [
        ('FULL_TIME', 'Full Time'),
        ('PART_TIME', 'Part Time'),
        ('CONTRACT', 'Contract'),
        ('INTERNSHIP', 'Internship')
    ]

    title = models.CharField(max_length=100)
    department = models.CharField(max_length=50)
    location = models.CharField(max_length=100)
    description = models.TextField()
    requirements = models.TextField()
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES, default='FULL_TIME')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'job_postings'
        ordering = ['-created_at']

class JobApplication(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending Review'),
        ('REVIEWING', 'Under Review'),
        ('SHORTLISTED', 'Shortlisted'),
        ('REJECTED', 'Rejected'),
        ('ACCEPTED', 'Accepted'),
    ]

    job = models.ForeignKey(JobPosting, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_applications')
    resume = models.FileField(upload_to='resumes/')
    cover_letter = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.applicant.username}'s application for {self.job.title}"

    class Meta:
        db_table = 'job_applications'
        ordering = ['-created_at']

class Earnings(models.Model):
    EARNING_TYPE_CHOICES = [
        ('DELIVERY', 'Delivery Completion'),
        ('BONUS', 'Performance Bonus'),
        ('TIP', 'Customer Tip'),
        ('OTHER', 'Other')
    ]
    
    worker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='earnings')
    delivery = models.ForeignKey('deliveries.Delivery', on_delete=models.SET_NULL, null=True, blank=True, related_name='earnings')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    earning_type = models.CharField(max_length=20, choices=EARNING_TYPE_CHOICES, default='DELIVERY')
    description = models.CharField(max_length=255, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.worker.username}'s earning of ${self.amount} on {self.timestamp.strftime('%Y-%m-%d')}"
    
    class Meta:
        db_table = 'worker_earnings'
        ordering = ['-timestamp']
        verbose_name_plural = 'Earnings'

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a UserProfile when a new User is created"""
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save the UserProfile when the User is saved"""
    instance.userprofile.save()
