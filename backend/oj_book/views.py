import json
import secrets
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from .models import Book, Chapter, Section, UserBookProgress, BookRedeemCode, UserBookPurchase
from .serializers import (
    BookListSerializer, BookDetailSerializer, BookEditSerializer,
    ChapterSerializer, ChapterEditSerializer,
    SectionDetailSerializer, SectionEditSerializer,
    UserBookProgressSerializer, BookRedeemCodeSerializer
)

PAYMENT_NOTE_PREFIX = 'PAYREQ:'


def _parse_payment_note(note):
    if not note or not str(note).startswith(PAYMENT_NOTE_PREFIX):
        return None
    raw = str(note)[len(PAYMENT_NOTE_PREFIX):]
    try:
        payload = json.loads(raw)
    except (TypeError, ValueError):
        return None
    return payload if isinstance(payload, dict) else None


def _build_payment_note(payload):
    data = dict(payload or {})
    data['remark'] = str(data.get('remark', '') or '')
    data['payment_reference'] = str(data.get('payment_reference', '') or '')

    while True:
        raw = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
        note = f'{PAYMENT_NOTE_PREFIX}{raw}'
        if len(note) <= 200:
            return note

        if data.get('remark'):
            data['remark'] = data['remark'][:-1]
            continue
        if data.get('payment_reference'):
            data['payment_reference'] = data['payment_reference'][:-1]
            continue
        return note[:200]


def _payment_status(code_obj, payload=None):
    payload = payload or _parse_payment_note(code_obj.note) or {}
    status_value = str(payload.get('status') or '').strip()
    if status_value in ['activated', 'rejected', 'pending']:
        return status_value

    if UserBookPurchase.objects.filter(user=code_obj.created_by, book=code_obj.book).exists():
        return 'activated'

    return 'pending'


def _serialize_payment_request(code_obj):
    payload = _parse_payment_note(code_obj.note) or {}
    status_value = _payment_status(code_obj, payload)

    amount_cents = int(payload.get('amount_cents') or 0)
    return {
        'request_id': code_obj.id,
        'book_id': code_obj.book_id,
        'amount_cents': amount_cents,
        'amount_yuan': round(amount_cents / 100, 2),
        'payment_reference': payload.get('payment_reference', ''),
        'remark': payload.get('remark', ''),
        'status': status_value,
        'created_at': code_obj.created_at,
        'paid_at': payload.get('paid_at'),
        'paid_by': payload.get('paid_by'),
        'activated_at': payload.get('activated_at'),
        'activated_by': payload.get('activated_by'),
        'rejected_at': payload.get('rejected_at'),
        'rejected_by': payload.get('rejected_by'),
        'rejected_reason': payload.get('rejected_reason', ''),
    }


def _is_payment_request_code(code_obj):
    return _parse_payment_note(code_obj.note) is not None


class IsBookAdmin(IsAuthenticated):
    """检查用户是否有电子书管理权限"""
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return request.user.is_staff or 'class' in getattr(request.user, 'permissions', [])


class BookViewSet(viewsets.ModelViewSet):
    """电子书视图集"""

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsBookAdmin()]
        return [IsAuthenticatedOrReadOnly()]

    def get_queryset(self):
        if self.request.user.is_authenticated and (
            self.request.user.is_staff or 'class' in getattr(self.request.user, 'permissions', [])
        ):
            queryset = Book.objects.all()
        else:
            queryset = Book.objects.filter(is_published=True)

        difficulty = self.request.query_params.get('difficulty')
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)

        tag = self.request.query_params.get('tag')
        if tag:
            queryset = queryset.filter(tags__contains=[tag])

        return queryset

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return BookEditSerializer
        if self.action == 'retrieve':
            return BookDetailSerializer
        return BookListSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def start_reading(self, request, pk=None):
        """开始阅读书籍"""
        book = self.get_object()
        progress, created = UserBookProgress.objects.get_or_create(
            user=request.user,
            book=book
        )

        if created:
            book.reader_count += 1
            book.save(update_fields=['reader_count'])

        first_section = Section.objects.filter(chapter__book=book).order_by('chapter__order', 'order').first()

        return Response({
            'progress': UserBookProgressSerializer(progress, context={'request': request}).data,
            'first_section_id': first_section.id if first_section else None
        })

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def my_progress(self, request, pk=None):
        """获取我的阅读进度"""
        book = self.get_object()
        try:
            progress = UserBookProgress.objects.get(user=request.user, book=book)
            return Response(UserBookProgressSerializer(progress, context={'request': request}).data)
        except UserBookProgress.DoesNotExist:
            return Response({'detail': '尚未开始阅读'}, status=404)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def redeem(self, request, pk=None):
        """使用兑换码兑换书籍"""
        book = self.get_object()
        code = str(request.data.get('code', '') or '').strip()

        if not code:
            return Response({'detail': '请输入兑换码'}, status=status.HTTP_400_BAD_REQUEST)

        if UserBookPurchase.objects.filter(user=request.user, book=book).exists():
            return Response({'detail': '您已拥有此书籍'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            redeem_code = BookRedeemCode.objects.get(code=code, book=book)
        except BookRedeemCode.DoesNotExist:
            return Response({'detail': '兑换码无效'}, status=status.HTTP_400_BAD_REQUEST)

        if not redeem_code.is_valid:
            return Response({'detail': '兑换码已失效或已用完'}, status=status.HTTP_400_BAD_REQUEST)

        UserBookPurchase.objects.create(
            user=request.user,
            book=book,
            redeem_code=redeem_code
        )

        redeem_code.used_count += 1
        redeem_code.save(update_fields=['used_count'])

        return Response({'detail': '兑换成功', 'purchased': True})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def payment_request(self, request, pk=None):
        """提交付费申请（测试支付流程）"""
        book = self.get_object()

        if book.is_free:
            return Response({'detail': '免费书籍无需付费申请'}, status=status.HTTP_400_BAD_REQUEST)

        if UserBookPurchase.objects.filter(user=request.user, book=book).exists():
            return Response({'detail': '您已拥有此书籍'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            amount_cents = int(request.data.get('amount_cents', 0))
        except (TypeError, ValueError):
            return Response({'detail': '支付金额格式错误'}, status=status.HTTP_400_BAD_REQUEST)

        if amount_cents <= 0:
            return Response({'detail': '支付金额必须大于 0'}, status=status.HTTP_400_BAD_REQUEST)
        if amount_cents > 100000000:
            return Response({'detail': '支付金额过大'}, status=status.HTTP_400_BAD_REQUEST)

        payment_reference = str(request.data.get('payment_reference', '') or '').strip()
        remark = str(request.data.get('remark', '') or '').strip()

        existing = BookRedeemCode.objects.filter(
            book=book,
            created_by=request.user,
            note__startswith=PAYMENT_NOTE_PREFIX,
        ).order_by('-created_at')

        for req in existing:
            status_value = _payment_status(req)
            if status_value == 'pending':
                return Response({
                    'detail': '您已有待确认的支付申请，请等待教师审核',
                    'request': _serialize_payment_request(req)
                }, status=status.HTTP_200_OK)

        for _ in range(8):
            code = secrets.token_hex(8).upper()
            if not BookRedeemCode.objects.filter(code=code).exists():
                break
        else:
            return Response({'detail': '系统繁忙，请稍后重试'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        payload = {
            'type': 'self_purchase_manual_review',
            'status': 'pending',
            'amount_cents': amount_cents,
            'payment_reference': payment_reference,
            'remark': remark,
            'requested_at': timezone.now().isoformat(),
        }

        req = BookRedeemCode.objects.create(
            book=book,
            code=code,
            max_uses=1,
            used_count=0,
            is_active=False,
            created_by=request.user,
            note=_build_payment_note(payload),
        )

        return Response({
            'detail': '支付申请已提交，支付确认后将自动开通电子书',
            'request': _serialize_payment_request(req)
        })

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def payment_requests(self, request, pk=None):
        """获取当前用户针对该书的付费申请记录"""
        book = self.get_object()
        qs = BookRedeemCode.objects.filter(
            book=book,
            created_by=request.user,
            note__startswith=PAYMENT_NOTE_PREFIX,
        ).order_by('-created_at')

        results = [_serialize_payment_request(code) for code in qs]
        return Response({'results': results, 'count': len(results)})

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def check_access(self, request, pk=None):
        """检查用户是否有权访问此书籍"""
        book = self.get_object()

        if book.is_free:
            return Response({'has_access': True, 'is_free': True})

        if request.user.is_staff or 'class' in getattr(request.user, 'permissions', []):
            return Response({'has_access': True, 'is_admin': True})

        has_purchased = UserBookPurchase.objects.filter(user=request.user, book=book).exists()
        return Response({'has_access': has_purchased, 'purchased': has_purchased})


class ChapterViewSet(viewsets.ModelViewSet):
    """章节视图集"""

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsBookAdmin()]
        return [IsAuthenticatedOrReadOnly()]

    def get_queryset(self):
        book_id = self.request.query_params.get('book_id')
        queryset = Chapter.objects.all()
        if book_id:
            queryset = queryset.filter(book_id=book_id)
        return queryset.order_by('order', 'id')

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ChapterEditSerializer
        return ChapterSerializer


class SectionViewSet(viewsets.ModelViewSet):
    """小节视图集"""

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsBookAdmin()]
        return [IsAuthenticatedOrReadOnly()]

    def get_queryset(self):
        chapter_id = self.request.query_params.get('chapter_id')
        book_id = self.request.query_params.get('book_id')
        queryset = Section.objects.all()
        if chapter_id:
            queryset = queryset.filter(chapter_id=chapter_id)
        if book_id:
            queryset = queryset.filter(chapter__book_id=book_id)
        return queryset.order_by('chapter__order', 'order', 'id')

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return SectionEditSerializer
        return SectionDetailSerializer

    def check_book_access(self, book):
        """检查用户是否有权访问书籍内容"""
        if book.is_free:
            return True

        if not self.request.user.is_authenticated:
            return False

        if self.request.user.is_staff or 'class' in getattr(self.request.user, 'permissions', []):
            return True

        return UserBookPurchase.objects.filter(user=self.request.user, book=book).exists()

    def retrieve(self, request, *args, **kwargs):
        """获取小节详情，需要检查付费权限"""
        instance = self.get_object()
        book = instance.chapter.book

        if not self.check_book_access(book):
            return Response(
                {'detail': '您尚未开通此书籍，请先完成购买后再阅读'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def complete(self, request, pk=None):
        """标记小节为已完成"""
        section = self.get_object()
        book = section.chapter.book

        progress, created = UserBookProgress.objects.get_or_create(
            user=request.user,
            book=book
        )

        if created:
            book.reader_count += 1
            book.save(update_fields=['reader_count'])

        progress.completed_sections.add(section)
        progress.last_section = section
        progress.save()

        return Response({
            'completed': True,
            'completed_count': progress.completed_count,
            'total_count': progress.total_count,
            'progress_percent': progress.progress_percent
        })

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def uncomplete(self, request, pk=None):
        """取消标记小节为已完成"""
        section = self.get_object()
        book = section.chapter.book

        try:
            progress = UserBookProgress.objects.get(user=request.user, book=book)
            progress.completed_sections.remove(section)

            return Response({
                'completed': False,
                'completed_count': progress.completed_count,
                'total_count': progress.total_count,
                'progress_percent': progress.progress_percent
            })
        except UserBookProgress.DoesNotExist:
            return Response({'detail': '尚未开始阅读'}, status=404)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def record_read(self, request, pk=None):
        """记录阅读（更新最后阅读位置）"""
        section = self.get_object()
        book = section.chapter.book

        progress, created = UserBookProgress.objects.get_or_create(
            user=request.user,
            book=book
        )

        if created:
            book.reader_count += 1
            book.save(update_fields=['reader_count'])

        progress.last_section = section
        progress.save()

        return Response({'recorded': True})


class MyBooksViewSet(viewsets.ReadOnlyModelViewSet):
    """我的书籍（阅读中的书籍）"""
    permission_classes = [IsAuthenticated]
    serializer_class = UserBookProgressSerializer

    def get_queryset(self):
        return UserBookProgress.objects.filter(user=self.request.user).select_related('book')


class BookRedeemCodeViewSet(viewsets.ModelViewSet):
    """兑换码管理视图集"""
    permission_classes = [IsBookAdmin]
    serializer_class = BookRedeemCodeSerializer

    def get_queryset(self):
        book_id = self.request.query_params.get('book_id')
        payment_request = str(self.request.query_params.get('payment_request', '')).lower()

        queryset = BookRedeemCode.objects.all().select_related('book', 'created_by')
        if book_id:
            queryset = queryset.filter(book_id=book_id)
        if payment_request in ['1', 'true', 'yes']:
            queryset = queryset.filter(note__startswith=PAYMENT_NOTE_PREFIX)
        return queryset.order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=False, methods=['post'])
    def generate(self, request):
        """批量生成兑换码"""
        book_id = request.data.get('book_id')
        count = int(request.data.get('count', 1))
        max_uses = 1  # 兑换码只能使用一次
        note = request.data.get('note', '')

        if not book_id:
            return Response({'detail': '请指定书籍'}, status=status.HTTP_400_BAD_REQUEST)

        book = get_object_or_404(Book, id=book_id)

        codes = []
        for _ in range(min(count, 100)):
            code = secrets.token_hex(8).upper()
            redeem_code = BookRedeemCode.objects.create(
                book=book,
                code=code,
                max_uses=max_uses,
                note=note,
                created_by=request.user
            )
            codes.append({
                'id': redeem_code.id,
                'code': code,
                'max_uses': max_uses
            })

        return Response({'codes': codes, 'count': len(codes)})

    @action(detail=True, methods=['post'], url_path='confirm-payment')
    def confirm_payment(self, request, pk=None):
        """管理员确认支付并自动开通电子书"""
        redeem_code = self.get_object()
        payload = _parse_payment_note(redeem_code.note)

        if payload is None:
            return Response({'detail': '该记录不是支付申请'}, status=status.HTTP_400_BAD_REQUEST)

        if _payment_status(redeem_code, payload) == 'activated':
            return Response({
                'detail': '该支付申请已开通，无需重复确认',
                'request': _serialize_payment_request(redeem_code),
            })

        if _payment_status(redeem_code, payload) == 'rejected':
            payload.pop('rejected_at', None)
            payload.pop('rejected_by', None)
            payload.pop('rejected_reason', None)

        purchase, _ = UserBookPurchase.objects.get_or_create(
            user=redeem_code.created_by,
            book=redeem_code.book,
            defaults={'redeem_code': redeem_code},
        )

        if purchase.redeem_code_id is None:
            purchase.redeem_code = redeem_code
            purchase.save(update_fields=['redeem_code'])

        payload['status'] = 'activated'
        payload['paid_at'] = timezone.now().isoformat()
        payload['paid_by'] = request.user.username
        payload['activated_at'] = payload['paid_at']
        payload['activated_by'] = request.user.username

        redeem_code.is_active = False
        redeem_code.used_count = 1
        redeem_code.note = _build_payment_note(payload)
        redeem_code.save(update_fields=['is_active', 'used_count', 'note'])

        return Response({
            'detail': '支付已确认，电子书已自动开通',
            'request': _serialize_payment_request(redeem_code),
        })

    @action(detail=True, methods=['post'], url_path='reject-payment')
    def reject_payment(self, request, pk=None):
        """管理员驳回支付申请"""
        redeem_code = self.get_object()
        payload = _parse_payment_note(redeem_code.note)
        if payload is None:
            return Response({'detail': '该记录不是支付申请'}, status=status.HTTP_400_BAD_REQUEST)

        if _payment_status(redeem_code, payload) == 'activated':
            return Response({'detail': '该支付申请已开通，无法驳回'}, status=status.HTTP_400_BAD_REQUEST)

        reason = str(request.data.get('reason', '') or '').strip()
        payload['status'] = 'rejected'
        payload['rejected_at'] = timezone.now().isoformat()
        payload['rejected_by'] = request.user.username
        payload['rejected_reason'] = reason

        redeem_code.is_active = False
        redeem_code.note = _build_payment_note(payload)
        redeem_code.save(update_fields=['is_active', 'note'])

        return Response({
            'detail': '已驳回支付申请',
            'request': _serialize_payment_request(redeem_code),
        })
