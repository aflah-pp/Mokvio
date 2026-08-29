from django.db import models
from django.utils.text import slugify

from projects.models import Projects
from shared.models import AuditMixin, UUIDPrimaryKeyMixin

DATA_TYPE_CHOICES = [
    ("string", "String"),
    ("integer", "Integer"),
    ("decimal", "Decimal"),
    ("boolean", "Boolean"),
    ("uuid", "UUID"),
    ("date", "Date"),
    ("datetime", "DateTime"),
]


class HTTPMethods(models.Model):
    get_method = models.BooleanField(default=True)
    post_method = models.BooleanField(default=False)
    patch_method = models.BooleanField(default=False)
    delete_method = models.BooleanField(default=False)

    class Meta:
        abstract = True


class Resources(UUIDPrimaryKeyMixin, AuditMixin, HTTPMethods):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=100, db_index=True)
    project = models.ForeignKey(
        Projects, on_delete=models.CASCADE, related_name="resources"
    )
    is_published = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["project", "slug"], name="unique_project_resource_slug"
            )
        ]
        indexes = [
            models.Index(fields=["slug", "is_published"]),
            models.Index(fields=["project", "slug"]),
        ]
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if self.slug:
            self.slug = slugify(self.slug)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} under {self.project.name}"


class Fields(UUIDPrimaryKeyMixin, AuditMixin):
    """
    Model for a single Field/Column inside a Resource.
    """

    resource = models.ForeignKey(
        Resources, on_delete=models.CASCADE, related_name="fields"
    )

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, db_index=True)
    description = models.TextField(max_length=1000, blank=True)

    data_type = models.CharField(max_length=30, choices=DATA_TYPE_CHOICES)

    generator_key = models.CharField(max_length=80)
    generator_options = models.JSONField(
        default=dict,
        blank=True,
    )
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["resource", "slug"], name="unique_resource_field_slug"
            ),
        ]
        indexes = [
            models.Index(fields=["resource", "display_order"]),
            models.Index(fields=["resource", "slug"]),
        ]
        ordering = ["display_order"]

    @classmethod
    def get_next_display_order(cls, resource_id):
        """Return the next available display_order for a resource."""
        last = (
            cls.objects.filter(resource_id=resource_id)
            .order_by("-display_order")
            .first()
        )
        return (last.display_order + 1) if last else 1

    def save(self, *args, **kwargs):
        if len(self.name) > 100:
            raise ValueError("Field name cannot exceed 100 characters")
        if len(self.slug) > 100:
            raise ValueError("Field slug cannot exceed 100 characters")

        if not self.slug:
            self.slug = slugify(self.name)
        else:
            self.slug = slugify(self.slug)

        if self.display_order == 0 and self.pk is None:
            self.display_order = self.get_next_display_order(self.resource_id)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.generator_key})"
