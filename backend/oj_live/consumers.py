import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.utils import timezone

from oj_course.models import Course, CourseEnrollment
from oj_class.models import Class, ClassStudent

from .models import LiveParticipant, LiveParticipantRole, LiveSession, LiveSessionStatus


class LiveSessionConsumer(AsyncJsonWebsocketConsumer):
    session_id = None
    group_name = None

    @database_sync_to_async
    def _get_session(self, session_id):
        return LiveSession.objects.filter(id=session_id, status=LiveSessionStatus.ACTIVE).first()

    @database_sync_to_async
    def _has_access(self, session: LiveSession, user_id: int):
        obj = session.get_related_object()
        if not obj:
            return False
        
        # 检查是否是教师
        teacher_id = session.get_teacher_id()
        if teacher_id == user_id:
            return True
        
        # 检查是否是课程成员
        if isinstance(obj, Course):
            return CourseEnrollment.objects.filter(course=obj, user_id=user_id).exists()
        
        # 检查是否是班级成员
        if isinstance(obj, Class):
            return ClassStudent.objects.filter(class_obj=obj, user_id=user_id).exists()
        
        return False

    @database_sync_to_async
    def _upsert_participant(self, session: LiveSession, user_id: int):
        teacher_id = session.get_teacher_id()
        role = LiveParticipantRole.TEACHER if teacher_id == user_id else LiveParticipantRole.STUDENT
        obj, _ = LiveParticipant.objects.update_or_create(
            session=session,
            user_id=user_id,
            defaults={
                'role': role,
                'left_at': None,
            }
        )
        return obj

    @database_sync_to_async
    def _is_active_participant(self, session_id, user_id):
        return LiveParticipant.objects.filter(session_id=session_id, user_id=user_id, left_at__isnull=True).exists()

    @database_sync_to_async
    def _active_participant_count(self, session_id):
        return LiveParticipant.objects.filter(session_id=session_id, left_at__isnull=True).count()

    @database_sync_to_async
    def _mark_left(self, session_id, user_id):
        LiveParticipant.objects.filter(session_id=session_id, user_id=user_id, left_at__isnull=True).update(left_at=timezone.now())

    @database_sync_to_async
    def _participants_payload(self, session_id):
        qs = (
            LiveParticipant.objects
            .select_related('user')
            .filter(session_id=session_id, left_at__isnull=True)
            .order_by('joined_at')
        )
        return [
            {
                'user_id': p.user_id,
                'username': p.user.username,
                'role': p.role,
                'muted': p.muted,
                'hand_raised': p.hand_raised,
            }
            for p in qs
        ]

    async def connect(self):
        user = self.scope.get('user')
        if not user or not getattr(user, 'is_authenticated', False):
            await self.close(code=4401)
            return

        self.session_id = int(self.scope['url_route']['kwargs']['session_id'])
        self.group_name = f'live_session_{self.session_id}'

        session = await self._get_session(self.session_id)
        if not session:
            await self.close(code=4404)
            return

        ok = await self._has_access(session, user.id)
        if not ok and not user.is_staff:
            await self.close(code=4403)
            return

        is_existing = await self._is_active_participant(self.session_id, user.id)
        if not is_existing:
            cnt = await self._active_participant_count(self.session_id)
            if cnt >= 5:
                await self.close(code=4429)
                return

        await self._upsert_participant(session, user.id)

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        # 广播 user_joined 事件给所有人
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'live_event',
                'payload': {
                    'type': 'user_joined',
                    'user_id': user.id,
                    'user': {
                        'user_id': user.id,
                        'username': user.username,
                    },
                },
            },
        )

        # 广播更新后的参与者列表给所有人
        participants = await self._participants_payload(self.session_id)
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'live_event',
                'payload': {'type': 'participants', 'participants': participants},
            },
        )

    async def disconnect(self, close_code):
        user = self.scope.get('user')
        if user and getattr(user, 'is_authenticated', False) and self.session_id:
            await self._mark_left(self.session_id, user.id)

        if self.group_name:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

        if user and getattr(user, 'is_authenticated', False) and self.group_name:
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'live_event',
                    'payload': {
                        'type': 'user_left',
                        'user_id': user.id,
                    },
                },
            )

    async def receive(self, text_data=None, bytes_data=None):
        if not text_data:
            return
        try:
            data = json.loads(text_data)
        except Exception:
            return

        user = self.scope.get('user')
        if not user or not getattr(user, 'is_authenticated', False):
            return

        msg_type = data.get('type')
        if msg_type == 'signal':
            to_user_id = data.get('to_user_id')
            payload = {
                'type': 'signal',
                'from_user_id': user.id,
                'to_user_id': to_user_id,
                'signal_type': data.get('signal_type'),
                'data': data.get('data'),
            }
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'live_event',
                    'payload': payload,
                },
            )
            return

        if msg_type == 'raise_hand':
            hand_raised = bool(data.get('hand_raised'))
            await database_sync_to_async(LiveParticipant.objects.filter(session_id=self.session_id, user_id=user.id, left_at__isnull=True).update)(hand_raised=hand_raised)
            participants = await self._participants_payload(self.session_id)
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'live_event',
                    'payload': {'type': 'participants', 'participants': participants},
                },
            )

    async def live_event(self, event):
        payload = event.get('payload') or {}
        if payload.get('type') == 'signal':
            user = self.scope.get('user')
            if not user or not getattr(user, 'is_authenticated', False):
                return
            if payload.get('to_user_id') != user.id:
                return
        await self.send_json(payload)
