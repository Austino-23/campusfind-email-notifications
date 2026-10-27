from django.conf import settings
from django.db import models

class Item(models.Model):
    LOST = 'lost'
    FOUND = 'found'
    REPORT_TYPES = [(LOST, 'Lost'), (FOUND, 'Found')]
    CATEGORIES = [
        ('electronics', 'Electronics'), ('documents', 'Documents'),
        ('personal', 'Personal items'), ('bags', 'Bags'),
        ('books', 'Books'), ('clothing', 'Clothing'), ('other', 'Other'),
    ]
    name = models.CharField(max_length=120)
    report_type = models.CharField(max_length=5, choices=REPORT_TYPES)
    category = models.CharField(max_length=20, choices=CATEGORIES)
    location = models.CharField(max_length=180)
    item_date = models.DateField()
    description = models.TextField()
    contact_email = models.EmailField(blank=True)
    photo = models.FileField(upload_to='item_photos/', blank=True, null=True)
    reported_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='item_reports')
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} ({self.get_report_type_display()})'

class Claim(models.Model):
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    STATUSES = [(PENDING, 'Pending'), (APPROVED, 'Approved'), (REJECTED, 'Rejected')]
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='claims')
    claimant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='item_claims')
    message = models.TextField()
    status = models.CharField(max_length=10, choices=STATUSES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [models.UniqueConstraint(fields=['item', 'claimant'], name='unique_claim_per_user_item')]

    def __str__(self):
        return f'Claim: {self.item.name} by {self.claimant.username}'


class MatchNotification(models.Model):
    """Records a potential lost/found match and its email notification status."""
    lost_item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='match_notifications_as_lost')
    found_item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='match_notifications_as_found')
    recipient_email = models.EmailField()
    match_score = models.FloatField(default=0)
    email_sent = models.BooleanField(default=False)
    email_sent_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [models.UniqueConstraint(fields=['lost_item', 'found_item'], name='unique_lost_found_notification')]

    def __str__(self):
        return f'Match notification: {self.lost_item.name} / {self.found_item.name}'
