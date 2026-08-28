from rest_framework import serializers

from users.models import FeedBack, User


class UserDetailSerializer(serializers.ModelSerializer):
    """
    Serializes the authenticated user's public account information.

    """

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "avatar",
            "is_verified",
            "last_login",
        ]
        read_only_fields = [
            "id",
            "is_verified",
            "last_login",
        ]


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Validates and serializes new user registration data.
    """

    password = serializers.CharField(
        write_only=True,
        required=True,
    )

    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "avatar",
            "password",
            "password_confirm",
        ]

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {
                    "password_confirm": "Passwords do not match.",
                }
            )

        attrs.pop("password_confirm")

        return attrs


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Validates editable profile information for an existing user.
    """

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "avatar",
        ]


class ChangePasswordSerializer(serializers.Serializer):
    """
    Validates password-change requests.

    """

    old_password = serializers.CharField(
        write_only=True,
        required=True,
    )

    new_password = serializers.CharField(
        write_only=True,
        min_length=8,
        required=True,
    )

    new_password_confirm = serializers.CharField(
        write_only=True,
        required=True,
    )

    def validate(self, attrs):
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError(
                {
                    "new_password_confirm": "Passwords do not match.",
                }
            )

        attrs.pop("new_password_confirm")

        return attrs


class FeedBackCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedBack
        fields = ["title", "description", "steps_to_reproduce", "actual_behavior", "type_of_feedback"]
