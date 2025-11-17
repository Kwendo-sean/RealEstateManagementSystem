from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('client', 'Client'),
        ('agent', 'Real Estate Agent'),
        ('admin', 'Administrator'),
    )
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='client')
    phone_number = models.CharField(max_length=15, blank=True)
    
    def _str_(self):
        return f"{self.username} ({self.role})"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)
    
    # Client specific fields
    budget_min = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    budget_max = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    # Agent specific fields
    license_number = models.CharField(max_length=50, blank=True)
    company_name = models.CharField(max_length=100, blank=True)
    is_approved = models.BooleanField(default=False)
    
    def _str_(self):
        return f"{self.user.username}'s Profile"