from django.urls import path

from . import views

app_name = "users"


urlpatterns = [
    path(
        "register/",
        views.RegisterView.as_view(),
        name="register",
    ),
    path(
        "login/",
        views.LoginView.as_view(),
        name="login",
    ),
    path(
        "refresh/",
        views.RefreshTokenView.as_view(),
        name="token-refresh",
    ),
    path(
        "logout/",
        views.LogoutView.as_view(),
        name="logout",
    ),
    path(
        "logout-all/",
        views.LogoutAllView.as_view(),
        name="logout-all",
    ),
    path(
        "me/",
        views.CurrentUserView.as_view(),
        name="current-user",
    ),
    path(
        "me/update/",
        views.UserUpdateView.as_view(),
        name="update-user",
    ),
    path(
        "me/change-password/",
        views.ChangePasswordView.as_view(),
        name="change-password",
    ),
    path(
        "me/verify-email/",
        views.VerifyEmailView.as_view(),
        name="verify-email",
    ),
    path(
        "me/deactivate/",
        views.DeactivateAccountView.as_view(),
        name="deactivate-account",
    ),
    path(
        "feedback/new/",
        views.FeedBackCreateView.as_view(),
        name="Publish-feedback",
    ),
]
