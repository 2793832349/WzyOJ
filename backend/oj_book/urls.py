from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import BookViewSet, ChapterViewSet, SectionViewSet, MyBooksViewSet

router = SimpleRouter()
router.register('books', BookViewSet, basename='book')
router.register('chapters', ChapterViewSet, basename='chapter')
router.register('sections', SectionViewSet, basename='section')
router.register('my-books', MyBooksViewSet, basename='my-books')

urlpatterns = router.urls
