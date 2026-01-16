from django.urls import path
from rest_framework.routers import SimpleRouter
from .views import SubmissionViewSet, debug_run

router = SimpleRouter()
router.register('', SubmissionViewSet, basename='submission')

urlpatterns = [
    path('debug/', debug_run, name='debug_run'),
] + router.urls
