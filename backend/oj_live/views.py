from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError

from oj_course.models import Course, CourseEnrollment
from oj_class.models import Class, ClassStudent

from .models import LiveParticipant, LiveParticipantRole, LiveSession, LiveSessionStatus
from .serializers import LiveSessionSerializer


def _get_related_object(content_type_name, object_id):
    """获取关联对象（课程或班级）"""
    if content_type_name == 'course':
        return get_object_or_404(Course, id=object_id)
    elif content_type_name == 'class':
        return get_object_or_404(Class, id=object_id)
    else:
        raise ValidationError(f'Invalid content_type: {content_type_name}')


def _is_member(obj, user):
    """检查用户是否是成员"""
    # 检查是否是教师
    teacher_id = obj.teacher_id if hasattr(obj, 'teacher_id') else obj.teacher.id
    if teacher_id == user.id:
        return True
    
    # 检查是否是课程成员
    if isinstance(obj, Course):
        return CourseEnrollment.objects.filter(course=obj, user=user).exists()
    
    # 检查是否是班级成员
    if isinstance(obj, Class):
        return ClassStudent.objects.filter(class_obj=obj, user=user).exists()
    
    return False


def _is_teacher(obj, user):
    """检查用户是否是教师"""
    teacher_id = obj.teacher_id if hasattr(obj, 'teacher_id') else obj.teacher.id
    return teacher_id == user.id


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_session(request, session_id: int):
    session = get_object_or_404(LiveSession, id=int(session_id))
    
    # 检查权限
    if not session.is_member(request.user) and not request.user.is_staff:
        raise PermissionDenied('没有访问权限')
    
    data = LiveSessionSerializer(session).data
    
    # 添加关联对象信息
    obj = session.get_related_object()
    if obj:
        data['related_object'] = {
            'type': 'course' if isinstance(obj, Course) else 'class',
            'id': obj.id,
            'title': obj.title,
            'teacher_id': session.get_teacher_id(),
        }
        # 向后兼容：保留 course 字段
        if isinstance(obj, Course):
            data['course'] = data['related_object']
    
    return Response({'session': data})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def active_session(request):
    content_type = request.query_params.get('content_type')  # 'course' or 'class'
    object_id = request.query_params.get('object_id')
    
    # 向后兼容：支持旧的 course_id 参数
    if not content_type and request.query_params.get('course_id'):
        content_type = 'course'
        object_id = request.query_params.get('course_id')
    
    if not content_type or not object_id:
        raise ValidationError('content_type and object_id required')
    
    obj = _get_related_object(content_type, int(object_id))
    
    if not _is_member(obj, request.user) and not request.user.is_staff:
        raise PermissionDenied('没有访问权限')
    
    # 查找活跃的直播会话
    ct = ContentType.objects.get_for_model(obj)
    session = LiveSession.objects.filter(
        content_type=ct,
        object_id=obj.id,
        status=LiveSessionStatus.ACTIVE
    ).order_by('-start_time').first()
    
    # 向后兼容：也查找旧的 course 字段
    if not session and isinstance(obj, Course):
        session = LiveSession.objects.filter(
            course=obj,
            status=LiveSessionStatus.ACTIVE
        ).order_by('-start_time').first()
    
    if not session:
        return Response({'session': None})
    return Response({'session': LiveSessionSerializer(session).data})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_session(request):
    content_type = request.data.get('content_type')  # 'course' or 'class'
    object_id = request.data.get('object_id')
    
    # 向后兼容：支持旧的 course_id 参数
    if not content_type and request.data.get('course_id'):
        content_type = 'course'
        object_id = request.data.get('course_id')
    
    if not content_type or not object_id:
        raise ValidationError('content_type and object_id required')
    
    obj = _get_related_object(content_type, int(object_id))
    
    if not (request.user.is_staff or _is_teacher(obj, request.user)):
        raise PermissionDenied('只有教师可以开启直播')
    
    # 检查是否已有活跃的直播
    ct = ContentType.objects.get_for_model(obj)
    exist = LiveSession.objects.filter(
        content_type=ct,
        object_id=obj.id,
        status=LiveSessionStatus.ACTIVE
    ).order_by('-start_time').first()
    
    if exist:
        return Response(LiveSessionSerializer(exist).data)
    
    title = request.data.get('title') or ''
    session = LiveSession.objects.create(
        content_type=ct,
        object_id=obj.id,
        title=title,
        started_by=request.user
    )
    
    LiveParticipant.objects.update_or_create(
        session=session,
        user=request.user,
        defaults={'role': LiveParticipantRole.TEACHER, 'left_at': None},
    )
    return Response(LiveSessionSerializer(session).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def end_session(request, session_id: int):
    session = get_object_or_404(LiveSession, id=int(session_id))
    obj = session.get_related_object()
    
    if not obj:
        raise ValidationError('直播会话没有关联对象')
    
    if not (request.user.is_staff or _is_teacher(obj, request.user)):
        raise PermissionDenied('只有教师可以结束直播')
    
    if session.status != LiveSessionStatus.ACTIVE:
        return Response(LiveSessionSerializer(session).data)
    
    session.status = LiveSessionStatus.ENDED
    session.end_time = timezone.now()
    session.save(update_fields=['status', 'end_time'])
    
    LiveParticipant.objects.filter(session=session, left_at__isnull=True).update(left_at=timezone.now())
    
    return Response(LiveSessionSerializer(session).data)
