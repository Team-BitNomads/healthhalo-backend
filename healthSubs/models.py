from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class HealthProfile(models.Model):
    # Choice Definitions
    WEIGHT_CHOICES = [
        ('underweight', 'Underweight'),
        ('healthy', 'Healthy Weight'),
        ('overweight', 'Overweight'),
        ('obese', 'Obese')
    ]
    
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other')
    ]
    
    RISK_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High')
    ]
    
    EXERCISE_CHOICES = [
        ('none', 'None'),
        ('1-2', '1-2 times/week'),
        ('3-5', '3-5 times/week'),
        ('daily', 'Daily')
    ]

    # Personal Info
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='health_profile', db_index=True)
    full_name = models.CharField(max_length=255)
    date_of_birth = models.DateField(
        null=True,
        blank=True,
        help_text="Format: YYYY-MM-DD"
    )
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    marital_status = models.CharField(max_length=50, blank=True)
    occupation = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=100, blank=True)
    income_range = models.CharField(max_length=50, blank=True)
    weight_category = models.CharField(max_length=12, choices=WEIGHT_CHOICES, blank=True)
    height_cm = models.PositiveIntegerField(null=True, blank=True)
    weight_kg = models.PositiveIntegerField(null=True, blank=True)

    # Health Data
    conditions = models.JSONField(default=list)
    medications = models.JSONField(default=list)
    allergies = models.JSONField(default=list)
    surgeries = models.JSONField(default=list)
    family_history = models.JSONField(default=list)

    # Lifestyle
    is_smoker = models.BooleanField(default=False)
    alcohol_use = models.BooleanField(default=False)
    exercise_frequency = models.CharField(max_length=20, choices=EXERCISE_CHOICES, blank=True)
    diet_type = models.CharField(max_length=20, blank=True)
    sleep_hours = models.PositiveIntegerField(null=True, blank=True)
    knows_blood_pressure = models.BooleanField(default=False)
    bp_checked_recently = models.BooleanField(default=False)

    # Healthcare Access
    nearest_facility = models.CharField(max_length=100, blank=True)
    facility_distance = models.CharField(max_length=50, blank=True)
    has_insurance = models.BooleanField(default=False)
    insurance_details = models.TextField(blank=True)

    # Auto-generated
    risk_level = models.CharField(max_length=10, choices=RISK_LEVELS, blank=True)
    last_updated = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        verbose_name = "Health Profile"
        verbose_name_plural = "Health Profiles"
        ordering = ['-last_updated']

    @property
    def bmi(self):
        if not (self.height_cm and self.weight_kg):
            return None
        return round(self.weight_kg / ((self.height_cm/100) ** 2), 1)

    def __str__(self):
        return f"{self.user.email}'s Health Profile"