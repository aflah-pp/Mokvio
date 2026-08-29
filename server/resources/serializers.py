from rest_framework import serializers

from .models import Fields, Resources


class ResourceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resources
        fields = ("name", "get_method", "post_method", "patch_method", "delete_method")

    def validate_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError("Resource name cannot be empty.")

        return value


class ResourceListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resources
        fields = (
            "id",
            "name",
            "slug",
            "is_published",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class FieldCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fields
        fields = (
            "name",
            "description",
            "generator_key",
            "generator_options",
        )

    def validate_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError("Field name cannot be empty.")

        return value

    def validate_generator_key(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError("Generator key cannot be empty.")

        return value


class FieldUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fields
        fields = (
            "name",
            "description",
            "generator_key",
            "generator_options",
        )

    def validate_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError("Field name cannot be empty.")

        return value

    def validate_generator_key(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError("Generator key cannot be empty.")

        return value


class FieldListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fields
        fields = (
            "id",
            "name",
            "slug",
            "data_type",
            "generator_key",
            "display_order",
        )
        read_only_fields = fields


class FieldDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fields
        fields = (
            "id",
            "name",
            "slug",
            "description",
            "data_type",
            "generator_key",
            "generator_options",
            "display_order",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class ResourceDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Resources
        fields = (
            "id",
            "name",
            "slug",
            "project",
            "is_published",
            "get_method",
            "post_method",
            "patch_method",
            "delete_method",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields
