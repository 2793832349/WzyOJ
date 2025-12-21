import json
import time

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.core.cache import cache
from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from oj_backend.permissions import Granted, IsAuthenticatedAndReadOnly, ReadOnly, Captcha
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import GenericAPIView, DestroyAPIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT, HTTP_401_UNAUTHORIZED
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet

from .models import User
from .serializers import (ChangePasswordSerializer, LoginSerializer,
                          UserBriefSerializer, UserDetailSerializer,
                          UserSerializer)


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

    @action(detail=False, methods=['get'], url_path='ranking')
    def get_ranking(self, request):
        ...


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
        if request.user.is_superuser and len(request.user.permissions) != 6:
            request.user.is_staff = True
            request.user.permissions = [
                'site_setting', 'problem', 'submission', 'contest',
                'discussion', 'user'
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
    permission_classes = [ReadOnly | IsAdminUser]
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
