import logging

from django.conf import settings
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import generics, permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer

from users.models import FeedBack
from users.serializers import (
    ChangePasswordSerializer,
    FeedBackCreateSerializer,
    UserCreateSerializer,
    UserDetailSerializer,
    UserUpdateSerializer,
)
from users.service import AccountService, FeedbackService

logger = logging.getLogger(__name__)


def set_refresh_cookie(response, refresh_token):
    """
    Store a refresh token in an HttpOnly browser cookie.

    Args:
        response: DRF Response instance.
        refresh_token: Serialized JWT refresh token.

    Returns:
        The same response with the refresh-token cookie attached.
    """
    response.set_cookie(
        key=settings.JWT_REFRESH_COOKIE_NAME,
        value=refresh_token,
        max_age=settings.JWT_REFRESH_COOKIE_MAX_AGE,
        httponly=True,
        secure=settings.JWT_REFRESH_COOKIE_SECURE,
        samesite=settings.JWT_REFRESH_COOKIE_SAMESITE,
        domain=settings.JWT_REFRESH_COOKIE_DOMAIN,
        path=settings.JWT_REFRESH_COOKIE_PATH,
    )

    return response


def clear_refresh_cookie(response):
    """
    Remove the refresh-token cookie from the client.

    Args:
        response: DRF Response instance.

    Returns:
        The same response with the refresh-token cookie removed.
    """
    response.delete_cookie(
        key=settings.JWT_REFRESH_COOKIE_NAME,
        domain=settings.JWT_REFRESH_COOKIE_DOMAIN,
        path=settings.JWT_REFRESH_COOKIE_PATH,
        samesite=settings.JWT_REFRESH_COOKIE_SAMESITE,
    )

    return response


def service_validation_error(exc):
    """
    Convert a Django ValidationError raised by the service layer
    into a DRF ValidationError.
    """
    if hasattr(exc, "message_dict"):
        return ValidationError(exc.message_dict)

    if hasattr(exc, "messages"):
        return ValidationError(
            {
                "detail": exc.messages,
            }
        )

    return ValidationError(
        {
            "detail": str(exc),
        }
    )


class RegisterView(APIView):
    """
    endpoint for creating a new user account.
    """

    permission_classes = [permissions.AllowAny]

    parser_classes = [
        JSONParser,
        MultiPartParser,
        FormParser,
    ]

    def post(self, request):
        serializer = UserCreateSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        try:
            user = AccountService.register(
                **serializer.validated_data,
            )
        except DjangoValidationError as exc:
            raise service_validation_error(exc)

        return Response(
            {
                "message": "Account created successfully.",
                "user": UserDetailSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    """
    endpoint for authenticating a user.

    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username:
            raise ValidationError(
                {
                    "username": "Username is required.",
                }
            )

        if not password:
            raise ValidationError(
                {
                    "password": "Password is required.",
                }
            )

        try:
            user, tokens = AccountService.login(
                username=username,
                password=password,
            )
        except DjangoValidationError as exc:
            raise service_validation_error(exc)

        response = Response(
            {
                "access": tokens["access"],
                "user": UserDetailSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )

        return set_refresh_cookie(
            response,
            tokens["refresh"],
        )


class RefreshTokenView(APIView):
    """
    Refresh an access token using the HttpOnly refresh-token cookie.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        refresh_token = request.COOKIES.get(
            settings.JWT_REFRESH_COOKIE_NAME,
        )

        if not refresh_token:
            raise ValidationError(
                {
                    "detail": "Refresh token not provided.",
                }
            )

        serializer = TokenRefreshSerializer(
            data={
                "refresh": refresh_token,
            }
        )

        try:
            serializer.is_valid(raise_exception=True)

        except TokenError:
            raise ValidationError(
                {
                    "detail": "Invalid or expired refresh token.",
                }
            )

        data = serializer.validated_data

        response = Response(
            {
                "access": data["access"],
            },
            status=status.HTTP_200_OK,
        )

        if "refresh" in data:
            return set_refresh_cookie(
                response,
                data["refresh"],
            )

        return response


class LogoutView(APIView):
    """
    Logout the currently authenticated browser session.
    """

    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def post(self, request):
        refresh_token = request.COOKIES.get(
            settings.JWT_REFRESH_COOKIE_NAME,
        )

        if not refresh_token:
            response = Response(
                {
                    "message": "Already logged out.",
                },
                status=status.HTTP_200_OK,
            )

            return clear_refresh_cookie(response)

        try:
            AccountService.logout(
                refresh_token=refresh_token,
            )
        except DjangoValidationError:
            response = Response(
                {
                    "message": "Logout completed.",
                },
                status=status.HTTP_200_OK,
            )

            return clear_refresh_cookie(response)

        response = Response(
            {
                "message": "Logged out successfully.",
            },
            status=status.HTTP_200_OK,
        )

        return clear_refresh_cookie(response)


class LogoutAllView(APIView):
    """
    Revoke every active refresh-token session belonging to
    the authenticated user.
    """

    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def post(self, request):
        try:
            AccountService.logout_all(
                user=request.user,
            )
        except DjangoValidationError as exc:
            raise service_validation_error(exc)

        response = Response(
            {
                "message": "All sessions have been logged out.",
            },
            status=status.HTTP_200_OK,
        )

        return clear_refresh_cookie(response)


class CurrentUserView(generics.RetrieveAPIView):
    """
    Return the authenticated user's public account information.
    """

    permission_classes = [
        permissions.IsAuthenticated,
    ]

    serializer_class = UserDetailSerializer

    def get_object(self):
        return self.request.user


class UserUpdateView(APIView):
    """
    Update the authenticated user's editable profile information.
    """

    permission_classes = [
        permissions.IsAuthenticated,
    ]

    parser_classes = [
        JSONParser,
        MultiPartParser,
        FormParser,
    ]

    def patch(self, request):
        serializer = UserUpdateSerializer(
            instance=request.user,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        try:
            user = AccountService.update_account(
                user=request.user,
                **serializer.validated_data,
            )
        except DjangoValidationError as exc:
            raise service_validation_error(exc)

        return Response(
            UserDetailSerializer(user).data,
            status=status.HTTP_200_OK,
        )


class ChangePasswordView(APIView):
    """
    Change the authenticated user's password.

    """

    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        try:
            AccountService.change_password(
                user=request.user,
                old_password=serializer.validated_data["old_password"],
                new_password=serializer.validated_data["new_password"],
            )
        except DjangoValidationError as exc:
            raise service_validation_error(exc)

        response = Response(
            {
                "message": "Password changed successfully. "
                "All sessions have been logged out.",
            },
            status=status.HTTP_200_OK,
        )

        return clear_refresh_cookie(response)


class VerifyEmailView(APIView):
    """
    Verify the authenticated user's email address.(Currently Not implemented actual verification method.)
    """

    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def post(self, request):
        try:
            user = AccountService.verify_email(
                user=request.user,
            )
        except DjangoValidationError as exc:
            raise service_validation_error(exc)

        return Response(
            {
                "message": "Email verified successfully.",
                "user": UserDetailSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )


class DeactivateAccountView(APIView):
    """
    Deactivate the authenticated user's account.
    """

    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def post(self, request):
        try:
            user = AccountService.deactivate_account(
                user=request.user,
            )

            if user is None:
                return Response(
                    {
                        "detail": "User not found.",
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

        except DjangoValidationError as exc:
            raise service_validation_error(exc)

        response = Response(
            {
                "message": "Account deactivated successfully.",
            },
            status=status.HTTP_200_OK,
        )

        return clear_refresh_cookie(response)


class FeedBackCreateView(generics.CreateAPIView):

    queryset = FeedBack.objects.all()
    serializer_class = FeedBackCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        feedback = FeedbackService.create_feedback(
            created_by=self.request.user,
            **serializer.validated_data,
        )

        serializer.instance = feedback
