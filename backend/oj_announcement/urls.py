from rest_framework.routers import SimpleRouter
from django.urls import include, path

from .views import AnnouncementViewSet

router = SimpleRouter()
router.register('', AnnouncementViewSet, basename='announcement')

urlpatterns = [path('', include(router.urls))]
