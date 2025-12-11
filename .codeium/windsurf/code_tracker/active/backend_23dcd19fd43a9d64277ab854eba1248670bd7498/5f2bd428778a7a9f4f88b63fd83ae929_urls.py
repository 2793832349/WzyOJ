Åfrom django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ClassViewSet, ClassProblemViewSet, AssignmentViewSet

router = DefaultRouter()
router.register(r'class', ClassViewSet, basename='class')
router.register(r'class-problem', ClassProblemViewSet, basename='class-problem')
router.register(r'assignment', AssignmentViewSet, basename='assignment')

urlpatterns = [
    path('', include(router.urls)),
]
Å*cascade08"(23dcd19fd43a9d64277ab854eba1248670bd74982%file:///root/backend/oj_class/urls.py:file:///root/backend