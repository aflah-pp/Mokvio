from django.contrib import admin

from .models import FeedBack, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """
    Administrative interface for the Mokvio user model.

    """

    list_display = (
        "username",
        "email",
        "is_verified",
        "is_active",
        "is_staff",
        "created_at",
        "last_login",
    )

    list_filter = (
        "is_verified",
        "is_active",
        "is_staff",
        "is_superuser",
    )

    search_fields = (
        "username",
        "email",
        "first_name",
        "last_name",
    )

    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
        "last_login",
        "date_joined",
    )

    ordering = ("-created_at",)

    fieldsets = (
        (
            "Account",
            {
                "fields": (
                    "id",
                    "username",
                    "email",
                    "password",
                ),
            },
        ),
        (
            "Profile",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "avatar",
                ),
            },
        ),
        (
            "Account Status",
            {
                "fields": (
                    "is_active",
                    "is_verified",
                ),
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_staff",
                    "is_superuser",
                    # "groups",
                    # "user_permissions",
                ),
            },
        ),
        (
            "Activity",
            {
                "fields": (
                    "last_login",
                    "date_joined",
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )


admin.site.register(FeedBack)
