from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    email = models.EmailField(
        max_length=254,
        unique=True,
        blank=False,
        help_text='Email'
    )
    first_name = models.CharField(
        max_length=150,
        blank=False,
        help_text='Name'
    )
    last_name = models.CharField(
        max_length=150,
        blank=False,
        help_text='Surname'
    )

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
