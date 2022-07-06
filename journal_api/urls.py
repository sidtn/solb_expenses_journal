from django.urls import include, path, re_path
from rest_framework import routers

from journal_api.views import CategoryAPIViewSet, ExpenseAPIViewSet

router = routers.DefaultRouter()
router.register(r"categories", CategoryAPIViewSet)
router.register(r"expenses", ExpenseAPIViewSet)


urlpatterns = [
    path("", include(router.urls)),
]
