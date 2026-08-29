from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from rest_framework import serializers

from generators.registry import get_generator


class RuntimeQuerySerializer(serializers.Serializer):
    count = serializers.IntegerField(
        required=False,
        default=1,
        min_value=1,
        max_value=10,
    )


class RuntimeResponseSerializer:
    @classmethod
    def serialize(cls, data):
        if isinstance(data, list):
            return [cls._serialize_record(record) for record in data]

        return cls._serialize_record(data)

    @classmethod
    def _serialize_record(cls, record):
        return {key: cls._serialize_value(value) for key, value in record.items()}

    @staticmethod
    def _serialize_value(value):
        if isinstance(value, UUID):
            return str(value)

        if isinstance(value, datetime):
            return value.isoformat()

        if isinstance(value, date):
            return value.isoformat()

        if isinstance(value, Decimal):
            return float(value)

        return value


class RuntimeRequestSerializer(serializers.Serializer):
    DATA_TYPE_FIELDS = {
        "string": serializers.CharField,
        "integer": serializers.IntegerField,
        "decimal": serializers.DecimalField,
        "boolean": serializers.BooleanField,
        "uuid": serializers.UUIDField,
        "date": serializers.DateField,
        "datetime": serializers.DateTimeField,
    }

    def __init__(self, *args, resource, **kwargs):
        super().__init__(*args, **kwargs)

        self.resource = resource

        for field in resource.fields.filter(
            deleted_at__isnull=True,
        ):
            self.fields[field.slug] = self._build_serializer_field(field)

    def _build_serializer_field(self, field):
        serializer_field_class = self.DATA_TYPE_FIELDS.get(
            field.data_type,
        )

        if serializer_field_class is None:
            raise serializers.ValidationError(
                {
                    field.slug: (f"Unsupported data type: {field.data_type}."),
                }
            )

        if field.data_type == "decimal":
            return serializer_field_class(
                max_digits=20,
                decimal_places=6,
                required=True,
            )

        return serializer_field_class(
            required=True,
        )

    def validate(self, attrs):
        defined_fields = {
            field.slug: field
            for field in self.resource.fields.filter(
                deleted_at__isnull=True,
            )
        }

        received_fields = set(self.initial_data.keys())

        unknown_fields = received_fields - set(defined_fields)

        if unknown_fields:
            raise serializers.ValidationError(
                {field: ["Unknown field."] for field in sorted(unknown_fields)}
            )

        for field_slug, field in defined_fields.items():
            generator = get_generator(field.generator_key)

            if generator is None:
                raise serializers.ValidationError(
                    {field_slug: [f"Unknown generator: {field.generator_key}."]}
                )

            generator_options = field.generator_options or {}

            try:
                generator.validate_options(generator_options)
            except ValueError as exc:
                raise serializers.ValidationError(
                    {
                        field_slug: [str(exc)],
                    }
                ) from exc

        return attrs


class RuntimePatchSerializer(serializers.Serializer):
    DATA_TYPE_FIELDS = {
        "string": serializers.CharField,
        "integer": serializers.IntegerField,
        "decimal": serializers.DecimalField,
        "boolean": serializers.BooleanField,
        "uuid": serializers.UUIDField,
        "date": serializers.DateField,
        "datetime": serializers.DateTimeField,
    }

    def __init__(self, *args, resource, **kwargs):
        super().__init__(*args, **kwargs)

        self.resource = resource

        for field in resource.fields.filter(
            deleted_at__isnull=True,
        ):
            self.fields[field.slug] = self._build_serializer_field(field)

    def _build_serializer_field(self, field):
        serializer_field_class = self.DATA_TYPE_FIELDS.get(
            field.data_type,
        )

        if serializer_field_class is None:
            raise serializers.ValidationError(
                {
                    field.slug: (f"Unsupported data type: {field.data_type}."),
                }
            )

        if field.data_type == "decimal":
            return serializer_field_class(
                max_digits=20,
                decimal_places=6,
                required=False,
            )

        return serializer_field_class(
            required=False,
        )

    def validate(self, attrs):
        defined_fields = {
            field.slug: field
            for field in self.resource.fields.filter(
                deleted_at__isnull=True,
            )
        }

        received_fields = set(self.initial_data.keys())

        unknown_fields = received_fields - set(defined_fields)

        if unknown_fields:
            raise serializers.ValidationError(
                {field: ["Unknown field."] for field in sorted(unknown_fields)}
            )

        if not received_fields:
            raise serializers.ValidationError(
                {"request": ["PATCH request cannot be empty."]}
            )

        for field_slug, field in defined_fields.items():
            if field_slug not in received_fields:
                continue

            generator = get_generator(field.generator_key)

            if generator is None:
                raise serializers.ValidationError(
                    {field_slug: [f"Unknown generator: {field.generator_key}."]}
                )

            generator_options = field.generator_options or {}

            try:
                generator.validate_options(generator_options)
            except ValueError as exc:
                raise serializers.ValidationError(
                    {
                        field_slug: [str(exc)],
                    }
                ) from exc

        return attrs
