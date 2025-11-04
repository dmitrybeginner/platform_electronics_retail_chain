from django.contrib.auth.models import AbstractUser
from django.db import models

class Employee(AbstractUser):
    # The is_active field is already inherited from AbstractUser
    # and is used by Django's authentication system by default.
    # No need to add it again.

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'

    def __str__(self):
        return self.username
