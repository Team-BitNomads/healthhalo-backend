from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum
from decimal import Decimal
from .constants import FREQUENCY_CHOICES, MIN_FREQUENCY

User = get_user_model()

class Circle(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_circles')
    members = models.ManyToManyField(User, through='Membership', related_name='circles')
    contribution_amount = models.DecimalField(max_digits=10, decimal_places=2)
    frequency = models.CharField(
        max_length=20,
        choices=FREQUENCY_CHOICES,
        default=MIN_FREQUENCY,
        help_text="How often members contribute"
    )
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    claim_lock_period = models.PositiveIntegerField(default=30, help_text="Days before new members can file claims")
    min_balance_alert = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.min_balance_alert or self.min_balance_alert == Decimal('0'):
            self.min_balance_alert = self.contribution_amount * 2
        super().save(*args, **kwargs)


class Membership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    circle = models.ForeignKey(Circle, on_delete=models.CASCADE)
    join_date = models.DateTimeField(auto_now_add=True)
    payment_warnings = models.IntegerField(default=0)
    last_contribution_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('user', 'circle')

    def __str__(self):
        return f"Membership({self.user.username} in {self.circle.name})"


class Contribution(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    circle = models.ForeignKey(Circle, on_delete=models.CASCADE, related_name='contributions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_automatic = models.BooleanField(default=False)
    refunded = models.BooleanField(default=False)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"Contribution({self.user.username}, {self.amount}, {self.timestamp})"


class Claim(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='claims')
    circle = models.ForeignKey(Circle, on_delete=models.CASCADE, related_name='claims')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    receipt = models.FileField(upload_to='claim_receipts/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def clean(self):
        super().clean()
        membership = Membership.objects.filter(user=self.user, circle=self.circle).first()
        if membership and (timezone.now() - membership.join_date).days < self.circle.claim_lock_period:
            raise ValidationError(f"Cannot claim within {self.circle.claim_lock_period} days of joining")

        duplicate = Claim.objects.filter(
            user=self.user,
            reason__iexact=self.reason,
            amount=self.amount,
            created_at__gte=timezone.now() - timedelta(days=7)
        )
        if duplicate.exists():
            raise ValidationError("Possible duplicate claim detected")

        total_contributed = Contribution.objects.filter(
            user=self.user,
            circle=self.circle,
            refunded=False
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

        if total_contributed < self.amount * Decimal('0.5'):
            raise ValidationError(
                f"Insufficient contributions. You've contributed {total_contributed} "
                f"but claiming {self.amount}"
            )

    def __str__(self):
        return f"Claim({self.user.username} - {self.amount} - {self.status})"
