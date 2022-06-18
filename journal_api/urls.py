from django.urls import include, path
from rest_framework import routers

from journal_api.views import CategoryAPIViewSet, ExpenseAPIViewSet

router = routers.DefaultRouter()
router.register(r"category", CategoryAPIViewSet)
router.register(r"expense", ExpenseAPIViewSet)


urlpatterns = [
    path("", include(router.urls)),
]
