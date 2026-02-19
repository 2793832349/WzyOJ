from django.conf import settings
from django.core.cache import cache
from django.db.models import Q
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from oj_backend.permissions import (Granted, IsAuthenticatedAndReadCreate,
                                    Captcha)
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import Discussion, Reply
from .serializers import DiscussionSerializer, ReplySerializer, ReplyBriefSerializer
from oj_contest.models import Contest


def _can_publish_discussion(user):
    if not (user and user.is_authenticated):
        return False
    if user.is_superuser or user.is_staff:
        return True
    perms = set(getattr(user, 'permissions', []) or [])
    return bool(perms.intersection({'problem', 'class'}))


def _can_edit_discussion(user, discussion):
    if not _can_publish_discussion(user):
        return False
    if user.is_superuser or user.is_staff:
        return True
    return discussion.author_id == getattr(user, 'id', None)


class DiscussionPagination(LimitOffsetPagination):
    default_limit = 20
    max_limit = 100


class ReplyPagination(PageNumberPagination):
    page_size = 20
    max_page_size = 100


class DiscussionViewSet(ReadOnlyModelViewSet):
    permission_classes = [Granted | IsAuthenticatedAndReadCreate, Captcha]
    permission = scene = 'discussion'
    pagination_class = DiscussionPagination
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    search_fields = ['id', 'title']
    filterset_fields = [
        'title', 'related_problem__id', 'related_contest__id',
        'author__username'
    ]
    ordering_fields = ['create_time', 'update_time']

    def get_queryset(self):
        site_settings = cache.get('site_settings')
        if not site_settings.get('enableDiscussion'):
            queryset = Discussion.objects.none()
        elif self.permission in self.request.user.permissions:
            queryset = Discussion.objects
        else:
            processing_contest = Contest.objects.filter(
                start_time__lt=timezone.now(), end_time__gt=timezone.now())
            queryset = Discussion.objects
            # queryset = queryset.exclude(Q(_is_hidden=True))
            queryset = queryset.exclude(
                Q(related_problem___is_hidden=True)
                | Q(related_problem___hide_discussions=True)
                | Q(related_problem__contests__contest__in=processing_contest))
            queryset = queryset.exclude(
                Q(related_contest__is_hidden=True)
                | Q(related_contest__in=processing_contest))
            # queryset = queryset | Discussion.objects.filter(
            #     Q(author=self.request.user))
            queryset = queryset.distinct()
        return queryset.order_by('-id')

    def get_serializer_class(self):
        return DiscussionSerializer

    def create(self, request, *args, **kwargs):
        site_settings = cache.get('site_settings')
        if not site_settings.get('enableDiscussion'):
            return Response({'detail': '讨论功能已关闭'}, status=403)
        if not _can_publish_discussion(request.user):
            return Response({'detail': '仅教师可发布讨论'}, status=403)
        data = request.data
        discussion = Discussion(title=data['title'], author=request.user)
        if data.get('related_content_type') == 'problem':
            discussion.related_problem_id = data['related_content_id']
        elif data.get('related_content_type') == 'contest':
            discussion.related_contest_id = data['related_content_id']
        discussion.save()
        reply = Reply(content=data['content'],
                      author=request.user,
                      discussion=discussion)
        reply.save()
        return Response({'id': discussion.id}, status=201)

    @action(detail=True, methods=['get', 'post'], url_path='edit')
    def edit_discussion(self, request, pk=None):
        site_settings = cache.get('site_settings')
        if not site_settings.get('enableDiscussion'):
            return Response({'detail': '讨论功能已关闭'}, status=403)

        discussion = self.get_object()
        if not _can_edit_discussion(request.user, discussion):
            return Response({'detail': '无权限修改该讨论'}, status=403)

        first_reply = discussion.replies.order_by('id').first()

        if request.method == 'GET':
            related_content_type = 'none'
            related_content_id = None
            if discussion.related_problem_id:
                related_content_type = 'problem'
                related_content_id = discussion.related_problem_id
            elif discussion.related_contest_id:
                related_content_type = 'contest'
                related_content_id = discussion.related_contest_id

            return Response({
                'id': discussion.id,
                'title': discussion.title,
                'related_content_type': related_content_type,
                'related_content_id': related_content_id,
                'content': (first_reply.content if first_reply else ''),
            })

        data = request.data
        title = str(data.get('title', '') or '').strip()
        if not title:
            return Response({'detail': '讨论标题不能为空'}, status=400)

        related_content_type = data.get('related_content_type', 'none')
        related_content_id = data.get('related_content_id')

        discussion.title = title
        discussion.related_problem_id = None
        discussion.related_contest_id = None
        if related_content_type == 'problem':
            discussion.related_problem_id = related_content_id
        elif related_content_type == 'contest':
            discussion.related_contest_id = related_content_id
        discussion.save()

        content = str(data.get('content', '') or '')
        if first_reply:
            first_reply.content = content
            first_reply.save()
        else:
            Reply.objects.create(content=content,
                                 author=request.user,
                                 discussion=discussion)

        return Response({'id': discussion.id}, status=200)

    @action(detail=True, methods=['get', 'post'], url_path='reply')
    def get_reply(self, request, pk=None):
        site_settings = cache.get('site_settings')
        if not site_settings.get('enableDiscussion'):
            return Response({'detail': '讨论功能已关闭'}, status=403)
        if request.method == 'POST':
            if not _can_publish_discussion(request.user):
                return Response({'detail': '仅教师可发布回复'}, status=403)
            data = request.data
            discussion = self.get_object()
            reply = Reply(content=data['content'],
                          author=request.user,
                          discussion=discussion)
            if data.get('reply_to'):
                reply_to = Reply.objects.filter(id=data['reply_to'])
                if reply_to.exists():
                    reply_to = reply_to.first()
                    if reply_to.discussion == discussion:
                        reply.reply_to = reply_to
            reply.save()
            return Response(status=201)
        paginator = ReplyPagination()
        discussion = self.get_object()
        queryset = discussion.replies.order_by('id')
        results = paginator.paginate_queryset(queryset, request)
        serializer = ReplySerializer(results, many=True)
        return Response(serializer.data)
