from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CourseChapterViewSet, CourseViewSet, CourseRedeemCodeViewSet

router = DefaultRouter()
router.register(r'course', CourseViewSet, basename='course')
router.register(r'chapter', CourseChapterViewSet, basename='course-chapter')
router.register(r'redeem-codes', CourseRedeemCodeViewSet, basename='course-redeem-code')

urlpatterns = [
    path('', include(router.urls)),
]
