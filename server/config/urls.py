from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from shared.telegram import TelegramWebhookView

from .views import server_status

admin.site.site_header = "Mokvio Administration"
admin.site.index_title = "Admin Services"
admin.site.site_title = "Mokvio"


urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "api/v1/",
        include(
            [
                path("status/", server_status, name="server status"),
                path("users/", include("users.urls"), name="users"),
                path("dashboard/", include("dashboard.urls"), name="dashboard"),
                path("projects/", include("projects.urls"), name="projects"),
                path("generators/", include("generators.urls"), name="generators"),
                path("", include("runtime.urls"), name="runtime"),
            ]
        ),
    ),
    path(
        "telegram/webhook/",
        TelegramWebhookView.as_view(),
        name="telegram-webhook",
    ),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
