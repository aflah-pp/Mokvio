from django.contrib.auth.models import AbstractUser
from django.db import models

from shared.models import AuditMixin, UUIDPrimaryKeyMixin


class User(UUIDPrimaryKeyMixin, AbstractUser):
    """
    Application user model.
    """

    username = models.CharField(
        max_length=30,
        unique=True,
        db_index=True,
    )

    email = models.EmailField(
        unique=True,
        db_index=True,
    )

    is_verified = models.BooleanField(
        default=False,
        db_index=True,
    )

    avatar = models.ImageField(
        upload_to="users/avatars/",
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return self.username


class FeedBack(UUIDPrimaryKeyMixin, AuditMixin):
    class Types(models.TextChoices):
        BUG_REPORT = "BUG REPORT", "Bug Report"
        FEATURE_REQUEST = "FEATURE REQUEST", "Feature Request"
        DOCUMENTATION = "DOCUMENTATION", "Documentation"
        USER_EXPERIENCE = "USER EXPERIENCE", "User Experience"
        GENERAL = "GENERAL", "General"

    ticket = models.CharField(max_length=20,unique=True,db_index=True)
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=150)
    steps_to_reproduce = models.CharField(max_length=150)
    actual_behavior = models.CharField(max_length=150)
    type_of_feedback = models.CharField(max_length=50, choices=Types, default=Types.GENERAL)

    def __str__(self):
        return f"{self.title} by {self.created_by}"
