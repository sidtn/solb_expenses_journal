from django.urls import include, path
from rest_framework import routers

from journal_api.views import (
    CategoryAPIViewSet,
    ExpenseAPIViewSet,
    LimitAPIView,
)

router = routers.DefaultRouter()
router.register(r"categories", CategoryAPIViewSet)
router.register(r"expenses", ExpenseAPIViewSet)


urlpatterns = [
    path("", include(router.urls)),
    path("limits/", LimitAPIView.as_view(), name="limits"),
]
