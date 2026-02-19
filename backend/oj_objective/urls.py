from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import ObjectivePaperViewSet, ObjectiveQuestionViewSet

router = SimpleRouter()
router.register('paper', ObjectivePaperViewSet, basename='objective-paper')
router.register('', ObjectiveQuestionViewSet, basename='objective')

urlpatterns = [path('', include(router.urls))]
