from django.contrib.auth.models import User, AbstractUser
from django.db import models
from datetime import timedelta
from django.utils import timezone
from django.conf import settings



class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    


    def __str__(self):
        return self.user.username
    
from django.utils import timezone
from datetime import timedelta

class PhoneOTP(models.Model):
    phone_number = models.CharField(max_length=15, unique=False)
    otp = models.CharField(max_length=6)
    timestamp = models.DateTimeField(auto_now_add=True)  # This is already the "created_at"
    is_verified = models.BooleanField(default=False)
    

    def is_expired(self):
        return timezone.now() > self.timestamp + timedelta(minutes=5)

    def __str__(self):
        return f"{self.phone_number} - {self.otp}"
    

class EmailOTP(models.Model):
    email = models.EmailField(unique=True)
    otp = models.CharField(max_length=6)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def is_expired(self):
        return timezone.now() > self.timestamp + timedelta(minutes=5)

    def __str__(self):
        return f"{self.email} - {self.otp}"   

    
class ProviderProfile(models.Model):
    SERVICE_CHOICES = [
        ('electrician', 'Electrician'),
        ('plumber', 'Plumber'),
        ('painter', 'Painter'),
        ('carpenter', 'Carpenter'),
        ('solar-electrician', 'Solar Electrician'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('suspended', 'Suspended'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    business_name = models.CharField(max_length=100, blank=True)
    categories = models.CharField(max_length=255)  # CSV of categories
    location = models.CharField(max_length=255)
    services_offered = models.TextField(blank=True)
    experience = models.CharField(max_length=50, blank=True)


    def __str__(self):
        return self.user.username


class Tender(models.Model):
    SERVICE_CATEGORIES = [
        ('electrician', 'Electrician'),
        ('plumber', 'Plumber'),
        ('painter', 'Painter'),
        ('carpenter', 'Carpenter'),
        ('solar', 'Solar Electrician'),
    ]
    URGENCY_CHOICES = [
        ('urgent', 'Urgent (Within 24 hours)'),
        ('soon', 'Soon (Within a week)'),
        ('flexible', 'Flexible (No specific deadline)'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=SERVICE_CATEGORIES)
    budget = models.PositiveIntegerField(blank=True, null=True)
    urgency = models.CharField(max_length=20, choices=URGENCY_CHOICES)
    address = models.CharField(max_length=255)
    postcode = models.CharField(max_length=10)
    start_date = models.DateField(blank=True, null=True)
    deadline = models.DateField()
    notes = models.TextField(blank=True)
    images = models.ImageField(upload_to='tender_images/', blank=True, null=True)
    status = models.CharField(max_length=20, default='open')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# models.py

class ProviderService(models.Model):
    CATEGORY_CHOICES = [
        ('electrician', 'Electrician'),
        ('plumber', 'Plumber'),
        ('painter', 'Painter'),
        ('carpenter', 'Carpenter'),
        ('solar-electrician', 'Solar Electrician'),
    ]

    provider = models.ForeignKey(User, on_delete=models.CASCADE)  # Linked to service provider
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    title = models.CharField(max_length=100)
    description = models.TextField()
    tags = models.CharField(max_length=255, blank=True)  # comma-separated tags

    created_at = models.DateTimeField(auto_now_add=True)

    def get_tags(self):
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]

    def __str__(self):
        return f"{self.title} - {self.provider.username}"
    

class Quotation(models.Model):
    tender = models.ForeignKey(Tender, on_delete=models.CASCADE)
    provider = models.ForeignKey(User, on_delete=models.CASCADE)
    labor_cost = models.DecimalField(max_digits=10, decimal_places=2)
    material_cost = models.DecimalField(max_digits=10, decimal_places=2)
    misc_cost = models.DecimalField(max_digits=10, decimal_places=2)
    gst_amount = models.DecimalField(max_digits=10, decimal_places=2)
    convenience_fee = models.DecimalField(max_digits=10, decimal_places=2)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, default='pending')  # pending, accepted, rejected
    created_at = models.DateTimeField(auto_now_add=True)
    progress = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Quote for {self.tender.title} by {self.provider.username}"
    
class Review(models.Model):
    tender = models.ForeignKey('Tender', on_delete=models.CASCADE)
    provider = models.ForeignKey(User, related_name='reviews_received', on_delete=models.CASCADE)
    customer = models.ForeignKey(User, related_name='reviews_written', on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.provider.username} by {self.customer.username}"    




class PortfolioProject(models.Model):
    provider = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='portfolio_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.provider.username}"

class Earning(models.Model):
    provider = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    project_name = models.CharField(max_length=255)
    client_name = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=[('Paid', 'Paid'), ('Pending', 'Pending'), ('Failed', 'Failed')])
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.project_name} - ₹{self.amount} ({self.status})"

