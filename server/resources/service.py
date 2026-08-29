import logging

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.http import Http404
from django.utils import timezone
from django.utils.text import slugify

from generators.registry import get_generator
from generators.validators import validate_generator_configuration

from .models import Fields, Resources

logger = logging.getLogger(__name__)


class ResourceService:
    """
    Service layer for resource and field business logic.

    """

    @staticmethod
    def _get_project_resource(project, resource_slug):
        """
        Return an active resource belonging to the given project.

        Args:
            project:
                Project owning the resource.

            resource_slug:
                Slug identifying the resource.

        Returns:
            Resources:
                The matching active resource.

        Raises:
            Http404:
                If the resource does not exist or has been soft-deleted.
        """

        try:
            return Resources.objects.get(
                slug=resource_slug,
                project=project,
                deleted_at__isnull=True,
            )
        except Resources.DoesNotExist as exc:
            raise Http404("Resource not found.") from exc

    @staticmethod
    def _generate_unique_slug(project, name, instance=None):
        """
        Generate a unique resource slug within a project.

        Args:
            project:
                Project owning the resource.

            name:
                Resource name from which the slug is generated.

            instance:
                Optional existing resource being renamed.

        Returns:
            A unique normalized resource slug.

        Raises:
            ValidationError:
                If a valid slug cannot be generated.
        """

        base_slug = slugify(name)

        if not base_slug:
            raise ValidationError(
                {
                    "name": "Resource name must contain valid characters.",
                }
            )

        slug = base_slug
        counter = 2

        queryset = Resources.objects.filter(
            project=project,
        )

        if instance is not None:
            queryset = queryset.exclude(
                pk=instance.pk,
            )

        while queryset.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        return slug

    @staticmethod
    def _generate_unique_field_slug(resource, name, instance=None):
        """
        Generate a unique field slug within a resource.

        Args:
            resource:
                Resource owning the field.

            name:
                Field name from which the slug is generated.

            instance:
                Optional existing field being renamed.

        Returns:
            A unique normalized field slug.

        Raises:
            ValidationError:
                If a valid slug cannot be generated.
        """

        base_slug = slugify(name)

        if not base_slug:
            raise ValidationError(
                {
                    "name": "Field name must contain valid characters.",
                }
            )

        slug = base_slug
        counter = 2

        queryset = Fields.objects.filter(
            resource=resource,
        )

        if instance is not None:
            queryset = queryset.exclude(
                pk=instance.pk,
            )

        while queryset.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        return slug

    @staticmethod
    def _validate_active_resource(resource):
        """
        Ensure that the resource has not been soft-deleted.

        Raises:
            ValidationError:
                If the resource has already been deleted.
        """

        if resource.deleted_at is not None:
            raise ValidationError(
                {
                    "resource": "Resource has been deleted.",
                }
            )

    @staticmethod
    def _get_generator_data_type(generator_key):
        """
        Resolve the data type supported by a generator.

        Args:
            generator_key:
                Registered generator key.

        Returns:
            str:
                The generator's supported data type.

        Raises:
            ValueError:
                If the generator does not exist or supports multiple
                data types and therefore cannot be resolved
                automatically.
        """

        generator = get_generator(generator_key)

        if generator is None:
            raise ValueError(f"Unknown generator: {generator_key}.")

        supported_types = tuple(generator.supported_types)

        if not supported_types:
            raise ValueError(
                f"Generator '{generator_key}' does not declare a supported data type."
            )

        if len(supported_types) > 1:
            raise ValueError(
                f"Generator '{generator_key}' supports multiple data types "
                "and cannot be used without explicit type selection."
            )

        return supported_types[0]

    @staticmethod
    @transaction.atomic
    def create(project, validated_data, user):
        name = validated_data["name"].strip()

        if not name:
            raise ValidationError(
                {
                    "name": "Resource name cannot be empty.",
                }
            )

        slug = ResourceService._generate_unique_slug(
            project=project,
            name=name,
        )

        try:
            resource = Resources.objects.create(
                project=project,
                name=name,
                slug=slug,
                is_published=False,
                created_by=user,
                get_method=validated_data.get("get_method", True),
                post_method=validated_data.get("post_method", False),
                patch_method=validated_data.get("patch_method", False),
                delete_method=validated_data.get("delete_method", False),
            )
        except IntegrityError as exc:
            raise ValidationError(
                {
                    "name": "A resource with this name already exists in this project.",
                }
            ) from exc

        logger.info(
            "Resource created. resource_id=%s project_id=%s user_id=%s slug=%s",
            resource.pk,
            project.pk,
            user.pk,
            resource.slug,
        )

        return resource

    @staticmethod
    @transaction.atomic
    def rename(resource, name, user):
        """
        Rename an active resource and regenerate its slug.

        """

        ResourceService._validate_active_resource(resource)

        name = name.strip()

        if not name:
            raise ValidationError(
                {
                    "name": "Resource name cannot be empty.",
                }
            )

        slug = ResourceService._generate_unique_slug(
            project=resource.project,
            name=name,
            instance=resource,
        )

        if resource.name == name and resource.slug == slug:
            return resource

        resource.name = name
        resource.slug = slug
        resource.updated_by = user

        try:
            resource.save(
                update_fields=[
                    "name",
                    "slug",
                    "updated_by",
                    "updated_at",
                ],
            )
        except IntegrityError as exc:
            raise ValidationError(
                {
                    "name": "A resource with this name already exists in this project.",
                }
            ) from exc

        logger.info(
            "Resource renamed. resource_id=%s user_id=%s slug=%s",
            resource.pk,
            user.pk,
            resource.slug,
        )

        return resource

    @staticmethod
    @transaction.atomic
    def publish(resource, user):
        """
        Publish an active resource.

        """

        ResourceService._validate_active_resource(resource)

        if resource.is_published:
            raise ValidationError(
                {
                    "resource": "Resource is already published.",
                }
            )

        resource.is_published = True
        resource.updated_by = user

        resource.save(
            update_fields=[
                "is_published",
                "updated_by",
                "updated_at",
            ],
        )

        logger.info(
            "Resource published. resource_id=%s user_id=%s",
            resource.pk,
            user.pk,
        )

        return resource

    @staticmethod
    @transaction.atomic
    def unpublish(resource, user):
        """
        Unpublish an active resource.

        """

        ResourceService._validate_active_resource(resource)

        if not resource.is_published:
            raise ValidationError(
                {
                    "resource": "Resource is already unpublished.",
                }
            )

        resource.is_published = False
        resource.updated_by = user

        resource.save(
            update_fields=[
                "is_published",
                "updated_by",
                "updated_at",
            ],
        )

        logger.info(
            "Resource unpublished. resource_id=%s user_id=%s",
            resource.pk,
            user.pk,
        )

        return resource

    @staticmethod
    def get_resource(project, resource_slug):
        """
        Return an active resource identified by project and slug.

        """

        return ResourceService._get_project_resource(
            project=project,
            resource_slug=resource_slug,
        )

    @staticmethod
    def list_resources(project):
        """
        Return all active resources belonging to a project.

        """

        return Resources.objects.filter(
            project=project,
            deleted_at__isnull=True,
        )

    @staticmethod
    @transaction.atomic
    def delete(resource, user):
        """
        Soft-delete a resource and all of its active fields.

        """

        if resource.deleted_at is not None:
            raise ValidationError(
                {
                    "resource": "Resource is already deleted.",
                }
            )

        now = timezone.now()

        resource.deleted_at = now
        resource.deleted_by = user
        resource.is_published = False
        resource.updated_by = user

        resource.save(
            update_fields=[
                "deleted_at",
                "deleted_by",
                "is_published",
                "updated_by",
                "updated_at",
            ],
        )

        resource.fields.filter(
            deleted_at__isnull=True,
        ).update(
            deleted_at=now,
            deleted_by=user,
            updated_by=user,
            updated_at=now,
        )

        logger.warning(
            "Resource soft-deleted. resource_id=%s resource_slug=%s user_id=%s",
            resource.pk,
            resource.slug,
            user.pk,
        )

        return resource

    @staticmethod
    @transaction.atomic
    def create_field(resource, validated_data, user):
        """
        Create a new field under an active resource.

        """

        ResourceService._validate_active_resource(resource)

        name = validated_data["name"].strip()
        generator_key = validated_data["generator_key"].strip()

        generator_options = validated_data.get(
            "generator_options",
            {},
        )

        if not name:
            raise ValidationError(
                {
                    "name": "Field name cannot be empty.",
                }
            )

        try:
            data_type = ResourceService._get_generator_data_type(
                generator_key=generator_key,
            )

            validate_generator_configuration(
                generator_key=generator_key,
                data_type=data_type,
                options=generator_options,
            )

        except ValueError as exc:
            raise ValidationError(
                {
                    "generator_options": str(exc),
                }
            ) from exc

        slug = ResourceService._generate_unique_field_slug(
            resource=resource,
            name=name,
        )

        try:
            field = Fields.objects.create(
                resource=resource,
                name=name,
                slug=slug,
                description=validated_data.get(
                    "description",
                    "",
                ),
                data_type=data_type,
                generator_key=generator_key,
                generator_options=generator_options,
                created_by=user,
            )
        except IntegrityError as exc:
            raise ValidationError(
                {
                    "name": "A field with this name already exists in this resource.",
                }
            ) from exc

        logger.info(
            "Field created. field_id=%s resource_id=%s user_id=%s slug=%s data_type=%s",
            field.pk,
            resource.pk,
            user.pk,
            field.slug,
            field.data_type,
        )

        return field

    @staticmethod
    def get_field(resource, field_slug):
        """
        Return an active field identified by its resource and slug.

        """

        try:
            return resource.fields.get(
                slug=field_slug,
                deleted_at__isnull=True,
            )
        except Fields.DoesNotExist as exc:
            raise Http404("Field not found.") from exc

    @staticmethod
    def list_fields(resource):
        """
        Return all active fields belonging to a resource.

        """

        return resource.fields.filter(
            deleted_at__isnull=True,
        )

    @staticmethod
    @transaction.atomic
    def update_field(field, validated_data, user):
        """
        Update an active field.

        """

        if field.deleted_at is not None:
            raise ValidationError(
                {
                    "field": "Field has been deleted.",
                }
            )

        updated_data = dict(validated_data)

        name = updated_data.get(
            "name",
            field.name,
        ).strip()

        generator_key = updated_data.get(
            "generator_key",
            field.generator_key,
        ).strip()

        generator_options = updated_data.get(
            "generator_options",
            field.generator_options,
        )

        try:
            data_type = ResourceService._get_generator_data_type(
                generator_key=generator_key,
            )

            validate_generator_configuration(
                generator_key=generator_key,
                data_type=data_type,
                options=generator_options,
            )

        except ValueError as exc:
            raise ValidationError(
                {
                    "generator_options": str(exc),
                }
            ) from exc

        if "name" in updated_data:
            if not name:
                raise ValidationError(
                    {
                        "name": "Field name cannot be empty.",
                    }
                )

            updated_data["name"] = name
            updated_data["slug"] = ResourceService._generate_unique_field_slug(
                resource=field.resource,
                name=name,
                instance=field,
            )

        if "generator_key" in updated_data:
            updated_data["generator_key"] = generator_key

        if "generator_options" in updated_data:
            updated_data["generator_options"] = generator_options

        updated_data["data_type"] = data_type

        for attribute, value in updated_data.items():
            setattr(
                field,
                attribute,
                value,
            )

        field.updated_by = user

        try:
            field.save(
                update_fields=[
                    *updated_data.keys(),
                    "updated_by",
                    "updated_at",
                ],
            )
        except IntegrityError as exc:
            raise ValidationError(
                {
                    "name": "A field with this name already exists in this resource.",
                }
            ) from exc

        logger.info(
            "Field updated. field_id=%s resource_id=%s user_id=%s data_type=%s",
            field.pk,
            field.resource_id,
            user.pk,
            field.data_type,
        )

        return field

    @staticmethod
    @transaction.atomic
    def delete_field(field, user):
        """
        Soft-delete an active field.

        """

        if field.deleted_at is not None:
            raise ValidationError(
                {
                    "field": "Field is already deleted.",
                }
            )

        field.deleted_at = timezone.now()
        field.deleted_by = user
        field.updated_by = user

        field.save(
            update_fields=[
                "deleted_at",
                "deleted_by",
                "updated_by",
                "updated_at",
            ],
        )

        logger.warning(
            "Field soft-deleted. field_id=%s resource_id=%s user_id=%s",
            field.pk,
            field.resource_id,
            user.pk,
        )

        return field
