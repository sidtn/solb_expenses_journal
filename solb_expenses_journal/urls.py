from django.contrib import admin
from django.urls import include, path

from journal_api.views import CreateUserView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("auth/", include("rest_framework.urls")),
    path("register/", CreateUserView.as_view()),
    path("api/v1/", include("journal_api.urls")),
]