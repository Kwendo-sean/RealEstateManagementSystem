from django.db import models
from django.conf import settings

class Transaction(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    )
    
    property = models.ForeignKey('properties.Property', on_delete=models.CASCADE, related_name='transactions')
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'role': 'client'})
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    mpesa_receipt_number = models.CharField(max_length=50, blank=True)
    phone_number = models.CharField(max_length=15)
    transaction_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    
    # MPESA STK Push fields
    merchant_request_id = models.CharField(max_length=100, blank=True)
    checkout_request_id = models.CharField(max_length=100, blank=True)
    result_code = models.IntegerField(null=True, blank=True)
    result_desc = models.CharField(max_length=255, blank=True)
    description = models.CharField(max_length=255, blank=True)
    transaction_type = models.CharField(max_length=50, default='property_payment')
    account_reference = models.CharField(max_length=50, blank=True)
    transaction_desc = models.CharField(max_length=255, default='Property Payment')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Transaction {self.mpesa_receipt_number or self.id} - KSh {self.amount}"
    
    class Meta:
        ordering = ['-transaction_date']
        
    def save(self, *args, **kwargs):
        if not self.account_reference:
            self.account_reference = f"PROP{self.property.id}"
        if not self.description:
            self.description = f"Payment for {self.property.title}"
        super().save(*args, **kwargs)