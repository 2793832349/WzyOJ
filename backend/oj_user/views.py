import json
import time
import datetime
from uuid import uuid4
from zoneinfo import ZoneInfo

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.core.cache import cache
from django.db.models import Count, Q
from django.db.models.functions import TruncDate
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from oj_backend.permissions import Granted, IsAuthenticatedAndReadOnly, ReadOnly, Captcha
from oj_problem.models import ProblemSolve
from oj_submission.models import StatusChoices, Submission
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import GenericAPIView, DestroyAPIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet

from .models import User
from .serializers import (ChangePasswordSerializer, CreateUserSerializer,
                          LoginSerializer, UserBriefSerializer,
                          UserDetailSerializer, UserSerializer)


def deep_update(a: dict, b: dict, skip: list = []):
    flag = False
    for i, j in b.items():
        if type(j) == dict:
            if i not in a:
                a[i] = {}
                flag = True
            if i not in skip:
                flag = deep_update(a[i], j) or flag
        elif i not in a:
            a[i] = j
            flag = True
    return flag


# def deep_eq(a: dict, b: dict) -> bool:
#     for i, j in b.items():
#         if type(j) == dict:
#             if i not in a:
#                 return False
#             elif not deep_eq(a[i], j):
#                 return False
#         elif i not in a:
#             return False
#         elif a[i] != j:
#             return False
#     return True



def get_site_settings():
    data = cache.get('site_settings')
    if data is not None:
        return data
    data_example = json.loads(
        settings.SITE_SETTINGS_EXAMPLE.read_text(encoding='utf-8'))
    if not settings.SITE_SETTINGS.exists():
        data = data_example
        data['update_time'] = int(time.time() * 1000)
        settings.SITE_SETTINGS.write_text(json.dumps(data,
                                                     indent=4,
                                                     ensure_ascii=False),
                                          encoding='utf-8')
    else:
        data = json.loads(
            settings.SITE_SETTINGS.read_text(encoding='utf-8'))
        if deep_update(data, data_example, data_example['noDeepUpdate']):
            data['update_time'] = int(time.time() * 1000)
            settings.SITE_SETTINGS.write_text(json.dumps(
                data, indent=4, ensure_ascii=False),
                                              encoding='utf-8')
    cache.set('site_settings', data, 86400)
    return data


class UserPagination(LimitOffsetPagination):
    default_limit = 50
    max_limit = 200


class UserViewSet(ModelViewSet):
    permission_classes = [Granted | IsAuthenticatedAndReadOnly]
    permission = 'user'
    lookup_value_regex = r'\d+'
    pagination_class = UserPagination
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ['id', 'username']
    ordering_fields = ['id', 'username']
    filterset_fields = []
    queryset = User.objects.order_by('id')

    def get_serializer_class(self):
        if self.action == 'list':
            return UserSerializer  # 使用 UserSerializer 以包含权限和状态信息
        elif self.action == 'create':
            return CreateUserSerializer
        elif self.action == 'update':
            return UserSerializer
        return UserDetailSerializer

    def update(self, request, *args, **kwargs):
        """更新用户信息，仅管理员可用"""
        if self.permission not in request.user.permissions:
            return Response(
                {'error': '只有管理员可以修改用户信息'},
                status=HTTP_401_UNAUTHORIZED
            )
        
        user = self.get_object()
        if request.data.get('password'):
            user.set_password(request.data['password'])
        user.save()
        serializer = UserSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], url_path='toggle-active')
    def toggle_active(self, request, pk=None):
        """切换用户封禁状态，仅管理员可用"""
        if self.permission not in request.user.permissions:
            return Response(
                {'error': '只有管理员可以封禁/解封用户'},
                status=HTTP_401_UNAUTHORIZED
            )
        
        user = self.get_object()
        
        # 不能封禁自己
        if user.id == request.user.id:
            return Response(
                {'error': '不能封禁自己'},
                status=HTTP_401_UNAUTHORIZED
            )
        
        # 不能封禁超级管理员
        if user.is_superuser:
            return Response(
                {'error': '不能封禁超级管理员'},
                status=HTTP_401_UNAUTHORIZED
            )
        
        user.is_active = not user.is_active
        user.save()
        
        serializer = UserSerializer(user)
        return Response(serializer.data)

    @action(detail=False,
            methods=['post'],
            permission_classes=[IsAuthenticated],
            url_path='change_password')
    def change_password(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        user = request.user
        user.set_password(serializer.validated_data.get('new_password'))
        user.save()
        return Response(status=HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated], url_path='upload-image')
    def upload_image(self, request):
        uploaded = request.FILES.get('file') or request.FILES.get('image')
        if not uploaded:
            return Response({'error': '请上传图片文件（字段名 file 或 image）'}, status=HTTP_400_BAD_REQUEST)

        content_type = str(getattr(uploaded, 'content_type', '') or '').lower()
        if not content_type.startswith('image/'):
            return Response({'error': '仅支持图片文件'}, status=HTTP_400_BAD_REQUEST)

        max_size = 10 * 1024 * 1024
        if int(getattr(uploaded, 'size', 0) or 0) > max_size:
            return Response({'error': '图片大小不能超过 10MB'}, status=HTTP_400_BAD_REQUEST)

        ext_map = {
            'image/jpeg': '.jpg',
            'image/png': '.png',
            'image/gif': '.gif',
            'image/webp': '.webp',
            'image/bmp': '.bmp',
            'image/svg+xml': '.svg',
        }
        ext = ext_map.get(content_type)
        if not ext:
            raw_name = str(getattr(uploaded, 'name', '') or '').lower()
            if '.' in raw_name:
                ext = '.' + raw_name.rsplit('.', 1)[-1]
            else:
                ext = '.png'

        now = timezone.localtime(timezone.now())
        image_dir = settings.MEDIA_ROOT / 'markdown_images' / str(now.year) / f'{now.month:02d}'
        image_dir.mkdir(parents=True, exist_ok=True)

        filename = f'{now.strftime("%Y%m%d%H%M%S")}_{request.user.id}_{uuid4().hex[:10]}{ext}'
        file_path = image_dir / filename

        with open(file_path, 'wb') as fp:
            for chunk in uploaded.chunks():
                fp.write(chunk)

        url = f'/media/markdown_images/{now.year}/{now.month:02d}/{filename}'
        return Response({'url': url, 'name': filename, 'size': uploaded.size})

    def _activity_daily_counts(self, qs, tz):
        day = TruncDate('create_time', tzinfo=tz)
        rows = (
            qs.annotate(day=day)
            .values('day')
            .annotate(count=Count('id'))
            .order_by('day')
        )
        return {row['day'].isoformat(): row['count'] for row in rows if row.get('day') is not None}

    def _max_streak(self, days):
        if not days:
            return 0
        days_sorted = sorted(set(days))
        best = 1
        cur = 1
        prev = days_sorted[0]
        for d in days_sorted[1:]:
            if (d - prev).days == 1:
                cur += 1
            else:
                best = max(best, cur)
                cur = 1
            prev = d
        best = max(best, cur)
        return best

    @action(detail=True, methods=['get'], url_path='activity', permission_classes=[Granted | IsAuthenticatedAndReadOnly])
    def activity(self, request, pk=None):
        profile_user = self.get_object()
        tz_name = request.query_params.get('tz') or 'Asia/Shanghai'
        try:
            tz = ZoneInfo(tz_name)
        except Exception:
            tz = ZoneInfo('Asia/Shanghai')
            tz_name = 'Asia/Shanghai'

        activity_type = (request.query_params.get('type') or 'solved').lower()
        now = timezone.localtime(timezone.now(), timezone=tz)

        year = request.query_params.get('year')
        if year is None:
            year = now.year
        else:
            try:
                year = int(year)
            except Exception:
                year = now.year

        year_start = datetime.datetime(year, 1, 1, tzinfo=tz)
        year_end = datetime.datetime(year + 1, 1, 1, tzinfo=tz)

        if activity_type == 'accepted':
            base_qs = Submission.objects.filter(user=profile_user, status=StatusChoices.ACCEPTED)
            year_qs = base_qs.filter(create_time__gte=year_start, create_time__lt=year_end)
            days = self._activity_daily_counts(year_qs, tz)
            all_time_count = base_qs.count()
            day_list_all = list(
                base_qs.annotate(day=TruncDate('create_time', tzinfo=tz))
                .values_list('day', flat=True)
                .distinct()
            )
        else:
            base_qs = ProblemSolve.objects.filter(user=profile_user)
            year_qs = base_qs.filter(create_time__gte=year_start, create_time__lt=year_end)
            days = self._activity_daily_counts(year_qs, tz)
            all_time_count = base_qs.count()
            day_list_all = list(
                base_qs.annotate(day=TruncDate('create_time', tzinfo=tz))
                .values_list('day', flat=True)
                .distinct()
            )

        last_year_start = now - datetime.timedelta(days=365)
        last_month_start = now - datetime.timedelta(days=30)

        last_year_count = base_qs.filter(create_time__gte=last_year_start, create_time__lte=now).count()
        last_month_count = base_qs.filter(create_time__gte=last_month_start, create_time__lte=now).count()

        day_list_last_year = list(
            base_qs.filter(create_time__gte=last_year_start, create_time__lte=now)
            .annotate(day=TruncDate('create_time', tzinfo=tz))
            .values_list('day', flat=True)
            .distinct()
        )
        day_list_last_month = list(
            base_qs.filter(create_time__gte=last_month_start, create_time__lte=now)
            .annotate(day=TruncDate('create_time', tzinfo=tz))
            .values_list('day', flat=True)
            .distinct()
        )

        data = {
            'year': year,
            'type': activity_type,
            'tz': tz_name,
            'days': days,
            'stats': {
                'all_time': all_time_count,
                'last_year': last_year_count,
                'last_month': last_month_count,
                'streak_max': self._max_streak([d for d in day_list_all if d is not None]),
                'streak_last_year_max': self._max_streak([d for d in day_list_last_year if d is not None]),
                'streak_last_month_max': self._max_streak([d for d in day_list_last_month if d is not None]),
            },
        }
        return Response(data)

    @action(detail=False, methods=['get'], url_path='ranking', permission_classes=[])
    def get_ranking(self, request):
        limit_param = request.query_params.get('limit', 10)
        try:
            limit = int(limit_param)
        except Exception:
            limit = 10
        limit = max(1, min(limit, 50))

        class_id = request.query_params.get('class_id')
        users = User.objects.filter(
            is_active=True,
            is_staff=False,
            is_superuser=False,
        )

        class_id_value = None
        if class_id not in [None, '']:
            from oj_class.models import Class, ClassStudent

            try:
                class_id_value = int(class_id)
            except Exception:
                return Response({'error': 'class_id 非法'}, status=HTTP_400_BAD_REQUEST)

            class_obj = Class.objects.filter(id=class_id_value, is_disbanded=False).first()
            if not class_obj:
                return Response({'error': '班级不存在'}, status=HTTP_400_BAD_REQUEST)

            if not request.user.is_authenticated:
                return Response({'error': '请先登录'}, status=HTTP_401_UNAUTHORIZED)

            if not request.user.is_staff:
                is_member = ClassStudent.objects.filter(
                    class_obj=class_obj,
                    user=request.user,
                ).exists()
                if not is_member and class_obj.teacher_id != request.user.id:
                    return Response({'error': '无权限查看该班级排行榜'}, status=403)

            student_ids = ClassStudent.objects.filter(
                class_obj=class_obj,
                role='student',
            ).values_list('user_id', flat=True)
            users = users.filter(id__in=student_ids)

        rows = list(
            users
            .annotate(
                solved_count=Count('problem_solve__problem_id', distinct=True),
                accepted_count=Count('submissions__id', filter=Q(submissions__status=StatusChoices.ACCEPTED), distinct=True),
            )
            .filter(solved_count__gt=0)
            .order_by('-solved_count', '-accepted_count', 'id')[:limit]
        )

        ranking = []
        current_rank = 0
        last_key = None
        for index, user in enumerate(rows, start=1):
            key = (user.solved_count, user.accepted_count)
            if key != last_key:
                current_rank = index
                last_key = key

            ranking.append({
                'rank': current_rank,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'real_name': user.real_name,
                    'avatar': user.avatar,
                },
                'solved_count': user.solved_count,
                'accepted_count': user.accepted_count,
            })

        return Response({
            'scope': 'class' if class_id_value else 'global',
            'class_id': class_id_value,
            'total': len(ranking),
            'ranking': ranking,
        })


class LoginView(GenericAPIView):
    authentication_classes = []
    permission_classes = [Captcha]
    serializer_class = LoginSerializer
    scene = 'login'

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        password = serializer.validated_data.get('password')
        user = authenticate(username=username, password=password)
        if not user:
            raise ValidationError(_('Uername or password error.'))
        if not user.is_active:
            raise ValidationError(_('User is disabled.'))
        login(request, user)
        serializer = UserSerializer(instance=user)
        return Response(serializer.data)


class LogoutView(APIView):
    permission_classes = []

    def get(self, *args, **kwargs):
        logout(self.request)
        return Response(status=HTTP_204_NO_CONTENT)


class RegisterView(GenericAPIView):
    authentication_classes = []
    permission_classes = [Captcha]
    serializer_class = LoginSerializer
    scene = 'register'
    permission = 'user'

    def post(self, request, *args, **kwargs):
        if self.request.user.is_anonymous or self.permission not in self.request.user.permissions:
            site_settings = get_site_settings()
            if not site_settings.get('allowRegister'):
                raise PermissionDenied(_('Register is not allowed.'))
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        password = serializer.validated_data.get('password')
        if User.objects.filter(username=username).exists():
            raise ValidationError(_('Username already exists.'))
        user = User.objects.create_user(username=username, password=password)
        if not request.user.is_authenticated:
            login(request, user)
        serializer = UserSerializer(instance=user)
        return Response(serializer.data)


class InfoAPIView(GenericAPIView):
    permission_classes = []
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        if request.user.is_superuser and len(request.user.permissions) != 7:
            request.user.is_staff = True
            request.user.permissions = [
                'site_setting', 'problem', 'submission', 'contest',
                'discussion', 'user', 'class'
            ]
            request.user.save()
        serializer = self.get_serializer(instance=request.user)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(status=HTTP_401_UNAUTHORIZED)
        if request.data.get('permissions'):
            request.data.pop('permissions')
        serializer = self.get_serializer(instance=request.user,
                                         data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class SiteSettingsView(GenericAPIView):
    permission_classes = [ReadOnly | Granted]
    permission = 'site_setting'

    def get(self, request, *args, **kwargs):

        def wash(data):
            not_for_client = data.get('notForClient', [])
            not_for_client = [i.split('.') for i in not_for_client]
            for i in not_for_client:
                t = data
                for j in i[:-1]:
                    t = t[j]
                t.pop(i[-1])
            return data

        data = get_site_settings()
        user = request.user
        if user.is_authenticated and self.permission not in user.permissions:
            data = wash(data)
        return Response(data)

    def put(self, request, *args, **kwargs):
        data = cache.get('site_settings')
        if data is None:
            data = json.loads(
                settings.SITE_SETTINGS.read_text(encoding='utf-8'))
        data.update(request.data)
        data['update_time'] = int(time.time() * 1000)
        settings.SITE_SETTINGS.write_text(json.dumps(data,
                                                     indent=4,
                                                     ensure_ascii=False),
                                          encoding='utf-8')
        cache.set('site_settings', data, 86400)
        return Response(data)

    def patch(self, request, *args, **kwargs):
        cache.delete('site_settings')
        return Response(status=HTTP_204_NO_CONTENT)

    def delete(self, request, *args, **kwargs):
        settings.SITE_SETTINGS.unlink(missing_ok=True)
        cache.delete('site_settings')
        return Response(status=HTTP_204_NO_CONTENT)
