"""
独立的录播课 URL 路由
与直播课路由完全分离
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    VideoCourseViewSet,
    VideoCourseChapterViewSet,
    VideoCourseProgressViewSet
)

# 创建路由器
router = DefaultRouter()

# 注册视图集
router.register(r'video-courses', VideoCourseViewSet, basename='videocourse')

# 嵌套路由：课程下的章节
chapters_router = DefaultRouter()
chapters_router.register(
    r'chapters',
    VideoCourseChapterViewSet,
    basename='videocourse-chapter'
)

# 学习进度路由
router.register(
    r'video-progress',
    VideoCourseProgressViewSet,
    basename='videocourse-progress'
)

app_name = 'oj_videocourse'

urlpatterns = [
    # API 路由
    path('', include(router.urls)),
    
    # 嵌套章节路由
    path(
        'video-courses/<int:videocourse_pk>/',
        include(chapters_router.urls)
    ),
]
