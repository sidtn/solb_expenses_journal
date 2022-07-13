from django.urls import include, path
from rest_framework import routers

from journal_api.views import (
    CategoryAPIViewSet,
    ExpenseAPIViewSet,
    LimitAPIViewSet,
)

router = routers.DefaultRouter()
router.register(r"categories", CategoryAPIViewSet)
router.register(r"expenses", ExpenseAPIViewSet)
router.register(r"limits", LimitAPIViewSet)


urlpatterns = [
    path("", include(router.urls)),
]
