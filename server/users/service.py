import logging

from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from django.utils.crypto import get_random_string
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)
from rest_framework_simplejwt.tokens import RefreshToken

from shared.tasks import send_feedback_telegram_notification
from users.models import FeedBack, User

logger = logging.getLogger(__name__)


class JWTService:
    """
    Provides JWT session-management operations for Mokvio.
    """

    @staticmethod
    def create_tokens(user):
        """
        Create a JWT access and refresh token pair for a user.
        """
        refresh = RefreshToken.for_user(user)

        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }

    @staticmethod
    def blacklist_refresh_token(refresh_token):
        """
        Blacklist a single refresh token.
        """
        if not refresh_token:
            raise ValidationError(
                {
                    "refresh_token": "Refresh token is required.",
                }
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            raise ValidationError(
                {
                    "refresh_token": "Invalid or expired refresh token.",
                }
            )

        return True

    @staticmethod
    def blacklist_all_user_tokens(user):
        """
        Revoke all outstanding refresh tokens belonging to a user.
        """
        outstanding_tokens = OutstandingToken.objects.filter(
            user=user,
        )

        for outstanding_token in outstanding_tokens:
            BlacklistedToken.objects.get_or_create(
                token=outstanding_token,
            )

        logger.info(
            "All refresh tokens revoked. user_id=%s",
            user.pk,
        )

        return True


class AccountService:
    """
    Contains business logic for Mokvio user accounts.

    """

    @staticmethod
    @transaction.atomic
    def register(
        *,
        username,
        email,
        password,
        first_name="",
        last_name="",
        avatar=None,
    ):
        """
        Register a new Mokvio user account.
        """
        username = username.strip()
        email = email.strip().lower()

        if not username:
            raise ValidationError(
                {
                    "username": "Username cannot be empty.",
                }
            )

        if not email:
            raise ValidationError(
                {
                    "email": "Email cannot be empty.",
                }
            )

        if User.objects.filter(
            username__iexact=username,
        ).exists():
            raise ValidationError(
                {
                    "username": "A user with this username already exists.",
                }
            )

        if User.objects.filter(
            email__iexact=email,
        ).exists():
            raise ValidationError(
                {
                    "email": "A user with this email already exists.",
                }
            )

        temporary_user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
        )

        validate_password(
            password,
            temporary_user,
        )

        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            avatar=avatar,
            is_active=True,
            is_verified=False,
        )

        user.set_password(password)
        user.save()

        logger.info(
            "User registered. user_id=%s",
            user.pk,
        )

        return user

    @staticmethod
    def login(
        *,
        username,
        password,
    ):
        """
        Authenticate a user using username and password.

        """
        username = username.strip()

        user = User.objects.filter(
            username__iexact=username,
        ).first()

        if not user:
            raise ValidationError(
                {
                    "login": "Invalid credentials.",
                }
            )

        if not user.is_active:
            raise ValidationError(
                {
                    "login": "Account is deactivated.",
                }
            )

        authenticated_user = authenticate(
            username=user.username,
            password=password,
        )

        if authenticated_user is None:
            raise ValidationError(
                {
                    "login": "Invalid credentials.",
                }
            )

        authenticated_user.last_login = timezone.now()

        authenticated_user.save(
            update_fields=[
                "last_login",
            ],
        )

        tokens = JWTService.create_tokens(
            authenticated_user,
        )

        logger.info(
            "Successful login. user_id=%s",
            authenticated_user.pk,
        )

        return authenticated_user, tokens

    @staticmethod
    def logout(
        *,
        refresh_token,
    ):
        """
        Revoke the refresh token belonging to the current session.

        """
        JWTService.blacklist_refresh_token(
            refresh_token,
        )

        logger.info(
            "User session logged out.",
        )

        return True

    @staticmethod
    def logout_all(
        *,
        user,
    ):
        """
        Revoke every outstanding refresh token belonging to a user.

        """
        JWTService.blacklist_all_user_tokens(
            user,
        )

        logger.info(
            "All user sessions logged out. user_id=%s",
            user.pk,
        )

        return True

    @staticmethod
    @transaction.atomic
    def update_account(
        *,
        user,
        username=None,
        email=None,
        first_name=None,
        last_name=None,
        avatar=None,
    ):
        """
        Update editable account and profile information.

        """
        update_fields = []

        if username is not None:
            username = username.strip()

            if not username:
                raise ValidationError(
                    {
                        "username": "Username cannot be empty.",
                    }
                )

            if (
                User.objects.filter(
                    username__iexact=username,
                )
                .exclude(
                    pk=user.pk,
                )
                .exists()
            ):
                raise ValidationError(
                    {
                        "username": "A user with this username already exists.",
                    }
                )

            user.username = username
            update_fields.append("username")

        if email is not None:
            email = email.strip().lower()

            if not email:
                raise ValidationError(
                    {
                        "email": "Email cannot be empty.",
                    }
                )

            if (
                User.objects.filter(
                    email__iexact=email,
                )
                .exclude(
                    pk=user.pk,
                )
                .exists()
            ):
                raise ValidationError(
                    {
                        "email": "A user with this email already exists.",
                    }
                )

            if email != user.email:
                user.is_verified = False
                update_fields.append("is_verified")

            user.email = email
            update_fields.append("email")

        if first_name is not None:
            user.first_name = first_name
            update_fields.append("first_name")

        if last_name is not None:
            user.last_name = last_name
            update_fields.append("last_name")

        if avatar is not None:
            user.avatar = avatar
            update_fields.append("avatar")

        if update_fields:
            update_fields.append("updated_at")

            user.save(
                update_fields=update_fields,
            )

        return user

    @staticmethod
    @transaction.atomic
    def change_password(
        *,
        user,
        old_password,
        new_password,
    ):
        """
        Change a user's password after validating the current password.

        """
        if not user.check_password(old_password):
            raise ValidationError(
                {
                    "old_password": "Incorrect current password.",
                }
            )

        if user.check_password(new_password):
            raise ValidationError(
                {
                    "new_password": ("New password must be different from the " "current password."),
                }
            )

        validate_password(
            new_password,
            user,
        )

        user.set_password(new_password)

        user.save(
            update_fields=[
                "password",
                "updated_at",
            ],
        )

        JWTService.blacklist_all_user_tokens(
            user,
        )

        logger.info(
            "Password changed and sessions revoked. user_id=%s",
            user.pk,
        )

        return True

    @staticmethod
    @transaction.atomic
    def verify_email(
        *,
        user,
    ):
        """
        Mark the user's current email address as verified.
        """
        if user.is_verified:
            return user

        user.is_verified = True

        user.save(
            update_fields=[
                "is_verified",
                "updated_at",
            ],
        )

        logger.info(
            "Email verified. user_id=%s",
            user.pk,
        )

        return user

    @staticmethod
    @transaction.atomic
    def deactivate_account(
        *,
        user,
    ):
        """
        Deactivate a user's account without deleting the database record.

        """
        if not user.is_active:
            return user

        user.is_active = False

        user.save(
            update_fields=[
                "is_active",
                "updated_at",
            ],
        )

        JWTService.blacklist_all_user_tokens(
            user,
        )

        logger.info(
            "Account deactivated. user_id=%s",
            user.pk,
        )

        return user


class FeedbackService:

    @staticmethod
    @transaction.atomic
    def create_feedback(
        *,
        created_by,
        title: str,
        description: str,
        steps_to_reproduce: str,
        actual_behavior: str,
        type_of_feedback: str = FeedBack.Types.GENERAL,
    ) -> FeedBack:

        title = title.strip()
        description = description.strip()
        steps_to_reproduce = steps_to_reproduce.strip()
        actual_behavior = actual_behavior.strip()

        if not title:
            raise ValidationError({"title": "Title must not be empty."})

        if not description:
            raise ValidationError({"description": "Description must be provided."})

        ticket = f"MOK-{get_random_string(8).upper()}"

        feedback = FeedBack.objects.create(
            created_by=created_by,
            ticket=ticket,
            title=title,
            description=description,
            steps_to_reproduce=steps_to_reproduce,
            actual_behavior=actual_behavior,
            type_of_feedback=type_of_feedback,
        )

        transaction.on_commit(lambda: send_feedback_telegram_notification.delay(str(feedback.pk)))

        return feedback
