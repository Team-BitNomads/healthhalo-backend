from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    phone = models.CharField(max_length=20, default=00000000000)
    language = models.CharField(max_length=20, default='English')

    def __str__(self):
        return self.username

