from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Extends the default Django user. I only add 'role' on top of
    the standard username/email/password that AbstractUser already gives us.
    """

    class Role(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        ANALYST = 'analyst', 'Analyst'
        VIEWER = 'viewer', 'Viewer'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.VIEWER,
    )

    def is_admin(self):
        return self.role == self.Role.ADMIN

    def is_analyst(self):
        return self.role in (self.Role.ADMIN, self.Role.ANALYST)

    def __str__(self):
        return f"{self.username} ({self.role})"