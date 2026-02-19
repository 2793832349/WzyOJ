from django.db.models import Q
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.viewsets import ModelViewSet

from oj_backend.permissions import Granted, ReadOnly

from .models import Announcement
from .serializers import AnnouncementSerializer


class AnnouncementPagination(LimitOffsetPagination):
    default_limit = 20
    max_limit = 100


class AnnouncementViewSet(ModelViewSet):
    permission_classes = [Granted | ReadOnly]
    permission = 'site_setting'
    lookup_value_regex = r'\d+'
    serializer_class = AnnouncementSerializer
    pagination_class = AnnouncementPagination
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ['id', 'title', 'content']
    ordering_fields = ['id', 'order', 'start_time', 'end_time', 'created_at', 'updated_at']
    filterset_fields = ['is_published', 'is_pinned']

    def _is_manager(self):
        user = self.request.user
        perms = getattr(user, 'permissions', []) if user and user.is_authenticated else []
        return bool(user and user.is_authenticated and (user.is_staff or user.is_superuser or self.permission in perms))

    def get_queryset(self):
        queryset = Announcement.objects.all()
        if self._is_manager():
            return queryset

        now = timezone.now()
        return queryset.filter(
            is_published=True,
        ).filter(
            Q(start_time__isnull=True) | Q(start_time__lte=now),
            Q(end_time__isnull=True) | Q(end_time__gte=now),
        )

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
