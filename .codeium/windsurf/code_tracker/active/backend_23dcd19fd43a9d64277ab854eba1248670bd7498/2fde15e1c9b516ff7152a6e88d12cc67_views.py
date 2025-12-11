•¿import hashlib
from zipfile import ZipFile
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.shortcuts import get_object_or_404

from .models import Class, ClassStudent, ClassProblem, Assignment
from .serializers import (
    ClassSerializer, ClassStudentSerializer, ClassProblemSerializer,
    AssignmentSerializer, AssignmentStatSerializer
)
from oj_problem.models import Problem


class ClassViewSet(viewsets.ModelViewSet):
    """ç­çº§è§†å›¾é›†"""
    queryset = Class.objects.all()
    serializer_class = ClassSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """è¿‡æ»¤æŸ¥è¯¢é›†"""
        user = self.request.user
        queryset = Class.objects.all()
        
        # éç®¡ç†å‘˜åªèƒ½çœ‹åˆ°è‡ªå·±çš„ç­çº§
        if not user.is_staff:
            queryset = queryset.filter(
                Q(teacher=user) |  # è‡ªå·±åˆ›å»ºçš„
                Q(members__user=user)  # è‡ªå·±åŠ å…¥çš„
            ).distinct()
        
        # è¿‡æ»¤éšè—çš„ç­çº§ï¼ˆéæ•™å¸ˆï¼‰
        if not user.is_staff:
            queryset = queryset.exclude(
                Q(is_hidden=True) & ~Q(teacher=user)
            )
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        """åˆ›å»ºç­çº§æ—¶è®¾ç½®æ•™å¸ˆä¸ºå½“å‰ç”¨æˆ·"""
        class_obj = serializer.save(teacher=self.request.user)
        # è‡ªåŠ¨å°†åˆ›å»ºè€…æ·»åŠ ä¸ºæ•™å¸ˆæˆå‘˜
        ClassStudent.objects.create(
            class_obj=class_obj,
            user=self.request.user,
            role='teacher'
        )
    
    @action(detail=True, methods=['get'])
    def students(self, request, pk=None):
        """è·å–ç­çº§å­¦ç”Ÿåˆ—è¡¨"""
        class_obj = self.get_object()
        students = class_obj.members.all()
        serializer = ClassStudentSerializer(students, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_student(self, request, pk=None):
        """æ·»åŠ å­¦ç”Ÿåˆ°ç­çº§"""
        class_obj = self.get_object()
        
        # æ£€æŸ¥æƒé™ï¼šåªæœ‰æ•™å¸ˆå¯ä»¥æ·»åŠ å­¦ç”Ÿ
        if class_obj.teacher != request.user:
            return Response(
                {'error': 'åªæœ‰æ•™å¸ˆå¯ä»¥æ·»åŠ å­¦ç”Ÿ'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        user_id = request.data.get('user_id')
        role = request.data.get('role', 'student')
        
        if not user_id:
            return Response(
                {'error': 'ç¼ºå°‘ user_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # æ£€æŸ¥ç”¨æˆ·æ˜¯å¦å·²åœ¨ç­çº§ä¸­
        if class_obj.members.filter(user_id=user_id).exists():
            return Response(
                {'error': 'ç”¨æˆ·å·²åœ¨ç­çº§ä¸­'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # æ·»åŠ å­¦ç”Ÿ
        membership = ClassStudent.objects.create(
            class_obj=class_obj,
            user_id=user_id,
            role=role
        )
        
        serializer = ClassStudentSerializer(membership)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def remove_student(self, request, pk=None):
        """ä»ç­çº§ç§»é™¤å­¦ç”Ÿ"""
        class_obj = self.get_object()
        
        # æ£€æŸ¥æƒé™
        if class_obj.teacher != request.user:
            return Response(
                {'error': 'åªæœ‰æ•™å¸ˆå¯ä»¥ç§»é™¤å­¦ç”Ÿ'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        user_id = request.data.get('user_id')
        if not user_id:
            return Response(
                {'error': 'ç¼ºå°‘ user_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # ç§»é™¤å­¦ç”Ÿ
        deleted_count, _ = class_obj.members.filter(user_id=user_id).delete()
        
        if deleted_count == 0:
            return Response(
                {'error': 'ç”¨æˆ·ä¸åœ¨ç­çº§ä¸­'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response({'message': 'ç§»é™¤æˆåŠŸ'})
    
    @action(detail=True, methods=['post'])
    def update_member_role(self, request, pk=None):
        """æ›´æ–°ç­çº§æˆå‘˜è§’è‰²"""
        class_obj = self.get_object()
        
        # æ£€æŸ¥æƒé™ï¼šåªæœ‰æ•™å¸ˆå¯ä»¥æ›´æ–°æˆå‘˜è§’è‰²
        if class_obj.teacher != request.user:
            return Response(
                {'error': 'åªæœ‰æ•™å¸ˆå¯ä»¥æ›´æ–°æˆå‘˜è§’è‰²'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        user_id = request.data.get('user_id')
        role = request.data.get('role')
        
        if not user_id:
            return Response(
                {'error': 'ç¼ºå°‘ user_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if role not in ['student', 'teacher']:
            return Response(
                {'error': 'è§’è‰²å¿…é¡»æ˜¯ student æˆ– teacher'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # æ›´æ–°æˆå‘˜è§’è‰²
        try:
            membership = class_obj.members.get(user_id=user_id)
            membership.role = role
            membership.save()
            
            serializer = ClassStudentSerializer(membership)
            return Response(serializer.data)
        except ClassStudent.DoesNotExist:
            return Response(
                {'error': 'ç”¨æˆ·ä¸åœ¨ç­çº§ä¸­'},
                status=status.HTTP_404_NOT_FOUND
            )


class ClassProblemViewSet(viewsets.ModelViewSet):
    """ç­çº§é¢˜ç›®è§†å›¾é›†"""
    queryset = ClassProblem.objects.all()
    serializer_class = ClassProblemSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """è¿‡æ»¤æŸ¥è¯¢é›†"""
        queryset = ClassProblem.objects.all()
        
        # æŒ‰ç­çº§è¿‡æ»¤
        class_id = self.request.query_params.get('class_id')
        if class_id:
            queryset = queryset.filter(class_obj_id=class_id)
        
        return queryset.order_by('order', 'created_at')
    
    def perform_create(self, serializer):
        """åˆ›å»ºé¢˜ç›®æ—¶æ£€æŸ¥æƒé™"""
        from rest_framework.exceptions import PermissionDenied
        
        class_obj = serializer.validated_data.get('class_obj')
        
        # æ£€æŸ¥æƒé™ï¼šåªæœ‰æ•™å¸ˆå¯ä»¥æ·»åŠ é¢˜ç›®
        if class_obj.teacher != self.request.user:
            raise PermissionDenied('åªæœ‰æ•™å¸ˆå¯ä»¥æ·»åŠ é¢˜ç›®')
        
        serializer.save()
    
    @action(detail=False, methods=['post'])
    def reference(self, request):
        """å¼•ç”¨ä¸»é¢˜åº“é¢˜ç›®åˆ°ç­çº§"""
        class_id = request.data.get('class_id')
        problem_id = request.data.get('problem_id')
        
        if not class_id or not problem_id:
            return Response(
                {'error': 'ç¼ºå°‘ class_id æˆ– problem_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        class_obj = get_object_or_404(Class, id=class_id)
        
        # æ£€æŸ¥æƒé™
        if class_obj.teacher != request.user:
            return Response(
                {'error': 'åªæœ‰æ•™å¸ˆå¯ä»¥æ·»åŠ é¢˜ç›®'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        problem = get_object_or_404(Problem, id=problem_id)
        
        # æ£€æŸ¥æ˜¯å¦å·²å¼•ç”¨
        if class_obj.problems.filter(reference_problem=problem).exists():
            return Response(
                {'error': 'è¯¥é¢˜ç›®å·²è¢«å¼•ç”¨'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # åˆ›å»ºå¼•ç”¨
        class_problem = ClassProblem.objects.create(
            class_obj=class_obj,
            reference_problem=problem,
            is_reference=True
        )
        
        serializer = self.get_serializer(class_problem)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'], url_path='upload-test-data')
    def upload_test_data(self, request, pk=None):
        """ä¸Šä¼ æµ‹è¯•æ•°æ®ï¼ˆ.zipæ–‡ä»¶ï¼‰"""
        class_problem = self.get_object()
        
        # æ£€æŸ¥æƒé™ï¼šåªæœ‰æ•™å¸ˆå¯ä»¥ä¸Šä¼ æµ‹è¯•æ•°æ®ï¼Œä¸”ä¸èƒ½æ˜¯å¼•ç”¨é¢˜ç›®
        if class_problem.class_obj.teacher != request.user:
            return Response(
                {'error': 'åªæœ‰æ•™å¸ˆå¯ä»¥ä¸Šä¼ æµ‹è¯•æ•°æ®'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if class_problem.is_reference:
            return Response(
                {'error': 'å¼•ç”¨é¢˜ç›®ä¸èƒ½ä¸Šä¼ æµ‹è¯•æ•°æ®'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        test_cases_file = request.FILES.get('file')
        if not test_cases_file:
            return Response(
                {'error': 'æœªä¸Šä¼ æ–‡ä»¶'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # æ£€æŸ¥æ–‡ä»¶ç±»å‹
        if not test_cases_file.name.endswith('.zip'):
            return Response(
                {'error': 'åªæ”¯æŒ .zip æ ¼å¼çš„æ–‡ä»¶'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # åˆ›å»ºæµ‹è¯•æ•°æ®ç›®å½•ï¼ˆä½¿ç”¨é¢˜ç›®IDï¼‰
        data_dir = settings.TEST_DATA_ROOT / 'class' / str(pk)
        data_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # è§£å‹æ–‡ä»¶
            test_cases = ZipFile(test_cases_file, 'r')
            test_cases.extractall(data_dir)
            
            # å¤„ç†ç­”æ¡ˆæ–‡ä»¶å¹¶è®¡ç®—MD5
            test_case_files = []
            for file in test_cases.namelist():
                if '.' in file:
                    file_name, file_ext = file.rsplit('.', 1)
                    test_case_files.append({'name': file_name, 'ext': file_ext})
                    
                    if file_ext == 'ans' or file_ext == 'out':
                        file_data = test_cases.read(file)
                        file_data = b'\n'.join(
                            map(bytes.rstrip,
                                file_data.rstrip().splitlines()))
                        file_hash = hashlib.md5(file_data).hexdigest()
                        (data_dir / f'{file_name}.md5').write_text(
                            file_hash, encoding='utf-8')
            
            test_cases.close()
            
            # æ›´æ–°é¢˜ç›®çš„æµ‹è¯•ç”¨ä¾‹é…ç½®
            if not class_problem.test_case_config:
                # è‡ªåŠ¨ç”Ÿæˆæµ‹è¯•ç”¨ä¾‹é…ç½®
                config = {
                    'test_cases': []
                }
                # æŸ¥æ‰¾æ‰€æœ‰ .in æ–‡ä»¶
                in_files = sorted([f['name'] for f in test_case_files if f['ext'] == 'in'])
                for in_file in in_files:
                    # æŸ¥æ‰¾å¯¹åº”çš„è¾“å‡ºæ–‡ä»¶ï¼ˆ.ans æˆ– .outï¼‰
                    out_file = None
                    for f in test_case_files:
                        if f['name'] == in_file and f['ext'] in ['ans', 'out']:
                            out_file = f'{in_file}.{f["ext"]}'
                            break
                    
                    if out_file:
                        config['test_cases'].append({
                            'input': f'{in_file}.in',
                            'output': out_file,
                            'score': 10
                        })
                
                import json
                class_problem.test_case_config = json.dumps(config)
                class_problem.save()
            
            return Response({
                'message': 'æµ‹è¯•æ•°æ®ä¸Šä¼ æˆåŠŸ',
                'files': [f'{f["name"]}.{f["ext"]}' for f in test_case_files]
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'è§£å‹æˆ–å¤„ç†æ–‡ä»¶å¤±è´¥: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AssignmentViewSet(viewsets.ModelViewSet):
    """ä½œä¸šè§†å›¾é›†"""
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """è¿‡æ»¤æŸ¥è¯¢é›†"""
        queryset = Assignment.objects.all()
        
        # æŒ‰ç­çº§è¿‡æ»¤
        class_id = self.request.query_params.get('class_id')
        if class_id:
            queryset = queryset.filter(class_obj_id=class_id)
        
        # å­¦ç”Ÿåªèƒ½çœ‹åˆ°æœªéšè—çš„ä½œä¸š
        user = self.request.user
        if not user.is_staff:
            # è·å–ç”¨æˆ·æ˜¯æ•™å¸ˆçš„ç­çº§
            teacher_class_ids = Class.objects.filter(teacher=user).values_list('id', flat=True)
            # å¦‚æœä¸æ˜¯æ•™å¸ˆï¼Œåˆ™è¿‡æ»¤éšè—çš„ä½œä¸š
            queryset = queryset.exclude(
                Q(is_hidden=True) & ~Q(class_obj_id__in=teacher_class_ids)
            )
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        """åˆ›å»ºä½œä¸šæ—¶æ£€æŸ¥æƒé™"""
        from rest_framework.exceptions import PermissionDenied, ValidationError
        from .models import AssignmentProblem
        from oj_problem.models import Problem
        import logging
        
        logger = logging.getLogger(__name__)
        class_obj = serializer.validated_data.get('class_obj')
        
        # æ£€æŸ¥æƒé™ï¼šåªæœ‰æ•™å¸ˆå¯ä»¥åˆ›å»ºä½œä¸š
        if class_obj.teacher != self.request.user:
            raise PermissionDenied('åªæœ‰æ•™å¸ˆå¯ä»¥åˆ›å»ºä½œä¸š')
        
        assignment = serializer.save()
        
        # å¤„ç†é¢˜ç›®IDåˆ—è¡¨
        problem_ids = self.request.data.get('problem_ids', [])
        if problem_ids:
            for order, problem_id in enumerate(problem_ids):
                try:
                    # éªŒè¯é¢˜ç›®æ˜¯å¦å­˜åœ¨
                    if not Problem.objects.filter(id=problem_id).exists():
                        logger.error(f"Problem with id {problem_id} does not exist")
                        raise ValidationError(f'é¢˜ç›® ID {problem_id} ä¸å­˜åœ¨')
                    
                    # å…ˆæ£€æŸ¥æˆ–åˆ›å»ºç­çº§é¢˜ç›®å¼•ç”¨
                    class_problem, created = ClassProblem.objects.get_or_create(
                        class_obj=class_obj,
                        reference_problem_id=problem_id,
                        defaults={
                            'is_reference': True,
                            'order': order,
                        }
                    )
                    # åˆ›å»ºä½œä¸šé¢˜ç›®å…³è”
                    AssignmentProblem.objects.create(
                        assignment=assignment,
                        problem=class_problem,
                        order=order
                    )
                except Exception as e:
                    logger.error(f"Error adding problem {problem_id} to assignment: {str(e)}")
                    raise ValidationError(f'æ·»åŠ é¢˜ç›®å¤±è´¥: {str(e)}')
    
    def perform_update(self, serializer):
        """æ›´æ–°ä½œä¸š"""
        from rest_framework.exceptions import PermissionDenied, ValidationError
        from .models import AssignmentProblem
        from oj_problem.models import Problem
        import logging
        
        logger = logging.getLogger(__name__)
        assignment = self.get_object()
        
        # æ£€æŸ¥æƒé™
        if assignment.class_obj.teacher != self.request.user:
            raise PermissionDenied('åªæœ‰æ•™å¸ˆå¯ä»¥ç¼–è¾‘ä½œä¸š')
        
        serializer.save()
        
        # æ›´æ–°é¢˜ç›®åˆ—è¡¨
        problem_ids = self.request.data.get('problem_ids', None)
        if problem_ids is not None:
            # åˆ é™¤æ—§çš„é¢˜ç›®å…³è”
            AssignmentProblem.objects.filter(assignment=assignment).delete()
            
            # æ·»åŠ æ–°çš„é¢˜ç›®å…³è”
            for order, problem_id in enumerate(problem_ids):
                try:
                    # éªŒè¯é¢˜ç›®æ˜¯å¦å­˜åœ¨
                    if not Problem.objects.filter(id=problem_id).exists():
                        logger.error(f"Problem with id {problem_id} does not exist")
                        raise ValidationError(f'é¢˜ç›® ID {problem_id} ä¸å­˜åœ¨')
                    
                    class_problem, created = ClassProblem.objects.get_or_create(
                        class_obj=assignment.class_obj,
                        reference_problem_id=problem_id,
                        defaults={
                            'is_reference': True,
                            'order': order,
                        }
                    )
                    AssignmentProblem.objects.create(
                        assignment=assignment,
                        problem=class_problem,
                        order=order
                    )
                except Exception as e:
                    logger.error(f"Error adding problem {problem_id} to assignment: {str(e)}")
                    raise ValidationError(f'æ·»åŠ é¢˜ç›®å¤±è´¥: {str(e)}')
    
    @action(detail=True, methods=['get'], url_path='problems')
    def get_problems(self, request, pk=None):
        """è·å–ä½œä¸šçš„é¢˜ç›®åˆ—è¡¨"""
        assignment = self.get_object()
        from .models import AssignmentProblem
        
        assignment_problems = AssignmentProblem.objects.filter(
            assignment=assignment
        ).select_related('problem', 'problem__reference_problem').order_by('order')
        
        from .serializers import AssignmentProblemSerializer
        serializer = AssignmentProblemSerializer(assignment_problems, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='grades')
    def get_grades(self, request, pk=None):
        """è·å–ä½œä¸šæˆç»©è¡¨"""
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            assignment = self.get_object()
            class_obj = assignment.class_obj
            
            # æ£€æŸ¥æƒé™ï¼šåªæœ‰æ•™å¸ˆå¯ä»¥æŸ¥çœ‹æˆç»©è¡¨
            if class_obj.teacher != request.user:
                return Response(
                    {'error': 'åªæœ‰æ•™å¸ˆå¯ä»¥æŸ¥çœ‹æˆç»©è¡¨'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            from .models import AssignmentProblem
            from oj_submission.models import Submission
            
            # è·å–ç­çº§å­¦ç”Ÿ
            students = class_obj.members.filter(role='student').select_related('user')
            
            # è·å–ä½œä¸šé¢˜ç›®åˆ—è¡¨
            assignment_problems = AssignmentProblem.objects.filter(
                assignment=assignment
            ).select_related('problem', 'problem__reference_problem').order_by('order')
            
            # æ„å»ºæˆç»©æ•°æ®
            grades_data = []
            for student_membership in students:
                student = student_membership.user
                student_data = {
                    'student_id': student.student_id or student.username,
                    'real_name': student.real_name or student.username,
                    'username': student.username,
                    'problems': []
                }
                
                # æ£€æŸ¥æ¯é“é¢˜çš„å®Œæˆæƒ…å†µ
                for ap in assignment_problems:
                    try:
                        problem_id = ap.problem.reference_problem_id if ap.problem.is_reference else ap.problem.id
                        
                        # æŸ¥æ‰¾è¯¥å­¦ç”Ÿå¯¹è¯¥é¢˜ç›®çš„æœ€ä½³æäº¤
                        # ä¼˜å…ˆæŸ¥æ‰¾ AC çš„æäº¤ï¼Œå¦‚æœæ²¡æœ‰åˆ™å–æœ€æ–°çš„æäº¤
                        ac_submission = Submission.objects.filter(
                            user=student,
                            problem_id=problem_id,
                            status=0  # ACCEPTED
                        ).first()
                        
                        if not ac_submission:
                            # å¦‚æœæ²¡æœ‰ ACï¼Œå–æœ€æ–°çš„æäº¤
                            best_submission = Submission.objects.filter(
                                user=student,
                                problem_id=problem_id,
                            ).order_by('-create_time').first()
                        else:
                            best_submission = ac_submission
                        
                        # å°†çŠ¶æ€ç è½¬æ¢ä¸ºå­—ç¬¦ä¸²
                        status_str = None
                        if best_submission:
                            if best_submission.status == 0:
                                status_str = 'AC'
                            elif best_submission.status == -1:
                                status_str = 'WA'
                            elif best_submission.status == -2:
                                status_str = 'CE'
                            elif best_submission.status == 1:
                                status_str = 'TLE'
                            elif best_submission.status == 2:
                                status_str = 'MLE'
                            elif best_submission.status == 3:
                                status_str = 'RE'
                            else:
                                status_str = 'ERROR'
                        
                        problem_status = {
                            'problem_id': problem_id,
                            'problem_title': ap.problem.get_title(),
                            'status': status_str,
                        }
                        student_data['problems'].append(problem_status)
                    except Exception as e:
                        logger.error(f"Error processing problem {ap.id}: {str(e)}", exc_info=True)
                        # æ·»åŠ é”™è¯¯ä¿¡æ¯çš„é¢˜ç›®çŠ¶æ€
                        student_data['problems'].append({
                            'problem_id': None,
                            'problem_title': f'é”™è¯¯: {str(e)}',
                            'status': None,
                        })
                
                grades_data.append(student_data)
            
            # æŒ‰å®Œæˆæ•°æ’åºï¼ˆé™åºï¼‰
            for student_data in grades_data:
                student_data['completed_count'] = sum(1 for p in student_data['problems'] if p['status'] == 'AC')
            grades_data.sort(key=lambda x: x['completed_count'], reverse=True)
            
            # æ·»åŠ æ’ååºå·
            for rank, student_data in enumerate(grades_data, start=1):
                student_data['rank'] = rank
            
            return Response(grades_data)
        except Exception as e:
            logger.error(f"Error in get_grades: {str(e)}", exc_info=True)
            return Response(
                {'error': f'è·å–æˆç»©è¡¨å¤±è´¥: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """è·å–ä½œä¸šç»Ÿè®¡ä¿¡æ¯"""
        assignment = self.get_object()
        class_obj = assignment.class_obj
        
        # æ£€æŸ¥æƒé™ï¼šåªæœ‰æ•™å¸ˆå¯ä»¥æŸ¥çœ‹ç»Ÿè®¡
        if class_obj.teacher != request.user:
            return Response(
                {'error': 'åªæœ‰æ•™å¸ˆå¯ä»¥æŸ¥çœ‹ç»Ÿè®¡'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # è·å–ç­çº§å­¦ç”Ÿ
        students = class_obj.members.filter(role='student')
        
        # TODO: å®ç°è¯¦ç»†çš„ç»Ÿè®¡é€»è¾‘
        # è¿™é‡Œéœ€è¦å…³è” submission æ¨¡å‹æ¥ç»Ÿè®¡æ¯ä¸ªå­¦ç”Ÿçš„å®Œæˆæƒ…å†µ
        stats_data = []
        for student_membership in students:
            stats_data.append({
                'student': student_membership.user,
                'total_problems': assignment.problems.count(),
                'solved_problems': 0,  # TODO: ä» submission ç»Ÿè®¡
                'submission_count': 0,  # TODO: ä» submission ç»Ÿè®¡
                'completion_rate': 0.0,
                'last_submit_time': None,
            })
        
        serializer = AssignmentStatSerializer(stats_data, many=True)
        return Response(serializer.data)
L*cascade08L’" *cascade08’"-*cascade08-·2 *cascade08·2ÿ2*cascade08ÿ2·4 *cascade08·4º4*cascade08º4¼4 *cascade08¼4½4*cascade08½4¾4 *cascade08¾4Â4*cascade08Â4Ã4 *cascade08Ã4Ä4*cascade08Ä4Æ4 *cascade08Æ4Ç4*cascade08Ç4È4 *cascade08È4Ê4*cascade08Ê4Ë4 *cascade08Ë4Í4*cascade08Í4ˆ@ *cascade08ˆ@¶_*cascade08¶_ûg *cascade08ûg±h *cascade08±hÂh*cascade08Âhùh *cascade08ùhëi*cascade08ëiôi *cascade08ôi¬k *cascade08¬k¯k*cascade08¯k±k *cascade08±k²k*cascade08²k³k *cascade08³k·k*cascade08·k¸k *cascade08¸k¹k*cascade08¹k»k *cascade08»k¼k*cascade08¼k½k *cascade08½k¿k*cascade08¿kÀk *cascade08ÀkÂk*cascade08Âkõk *cascade08õk‚l*cascade08‚l’l *cascade08’l’m *cascade08’m’m*cascade08’màm *cascade08àm°p*cascade08°p×p *cascade08×pÛp*cascade08Ûp¨q *cascade08¨q¬q*cascade08¬qéq *cascade08éqíq*cascade08íq¢r *cascade08¢r¦r*cascade08¦r±r *cascade08±r²r*cascade08²rÊr *cascade08ÊrÍr*cascade08Írûr *cascade08ûrÿr*cascade08ÿrs *cascade08s‘s*cascade08‘s¥s *cascade08¥s§s*cascade08§s©s *cascade08©s­s*cascade08­s¿s *cascade08¿sÂs*cascade08ÂsÒs *cascade08ÒsÓs*cascade08Ósîs *cascade08îsòs*cascade08òs¤t *cascade08¤t§t*cascade08§t»t *cascade08»t¼t*cascade08¼tÓt *cascade08Ót×t*cascade08×t–u *cascade08–ušu*cascade08šu¶u *cascade08¶u‹w*cascade08‹wßw *cascade08ßw•x *cascade08•x¦x*cascade08¦xİx *cascade08İxÏy*cascade08ÏyØy *cascade08Øyâz *cascade08âzåz*cascade08åzçz *cascade08çzèz*cascade08èzéz *cascade08ézíz*cascade08ízîz *cascade08îzïz*cascade08ïzñz *cascade08ñzòz*cascade08òzóz *cascade08ózõz*cascade08õzöz *cascade08özøz*cascade08øzÇ| *cascade08Ç|Ç|*cascade08Ç|½~ *cascade08½~*cascade08Ê *cascade08ÊÍ*cascade08Íá *cascade08áâ*cascade08â‚‚ *cascade08‚‚†‚*cascade08†‚»‚ *cascade08»‚¿‚*cascade08¿‚ö‚ *cascade08ö‚ú‚*cascade08ú‚¨ƒ *cascade08¨ƒ¬ƒ*cascade08¬ƒ¼ƒ *cascade08¼ƒ½ƒ*cascade08½ƒÑƒ *cascade08ÑƒÔƒ*cascade08ÔƒÖƒ *cascade08ÖƒÚƒ*cascade08Úƒìƒ *cascade08ìƒğƒ*cascade08ğƒ¶„ *cascade08¶„º„*cascade08º„Ñ„ *cascade08Ñ„Ó„*cascade08Ó„ç„ *cascade08ç„é„*cascade08é„”… *cascade08”…˜…*cascade08˜…´… *cascade08´…‰‡*cascade08‰‡¸‡ *cascade08¸‡ù‹ *cascade08ù‹û‹ *cascade08û‹‘ *cascade08‘ï*cascade08ï *cascade08’*cascade08’» *cascade08»¼*cascade08¼Ä *cascade08ÄÇ*cascade08ÇÈ *cascade08ÈÌ*cascade08Ì‡ *cascade08‡‰*cascade08‰‘ *cascade08‘“*cascade08“Å *cascade08ÅÉ*cascade08ÉÚ *cascade08ÚÜ*cascade08Üì *cascade08ìî*cascade08î *cascade08¢*cascade08¢ß *cascade08ßã*cascade08ãå *cascade08åæ*cascade08æî *cascade08îñ*cascade08ñò *cascade08òô*cascade08ôü *cascade08üş*cascade08ş¤‘ *cascade08¤‘¨‘*cascade08¨‘Ü‘ *cascade08Ü‘ß‘*cascade08ß‘ç‘ *cascade08ç‘è‘*cascade08è‘é‘ *cascade08é‘í‘*cascade08í‘Š’ *cascade08Š’’*cascade08’•’ *cascade08•’–’*cascade08–’é’ *cascade08é’í’*cascade08í’î’ *cascade08î’ñ’*cascade08ñ’ù’ *cascade08ù’ú’*cascade08ú’•“ *cascade08•“™“*cascade08™“Ù“ *cascade08Ù“Ü“*cascade08Ü“è“ *cascade08è“é“*cascade08é“ÿ“ *cascade08ÿ“ƒ”*cascade08ƒ”ß” *cascade08ß”ã”*cascade08ã”ä” *cascade08ä”è”*cascade08è”…• *cascade08…•‰•*cascade08‰•ª• *cascade08ª•®•*cascade08®•Ò• *cascade08Ò•Ö•*cascade08Ö•– *cascade08–”–*cascade08”–¥– *cascade08¥–©–*cascade08©–ÿ– *cascade08ÿ–ƒ—*cascade08ƒ—Ç— *cascade08Ç—Ë—*cascade08Ë—é— *cascade08é—ê—*cascade08ê—ú— *cascade08ú—ı—*cascade08ı—˜˜ *cascade08˜˜œ˜*cascade08œ˜˜ *cascade08˜Ÿ˜*cascade08Ÿ˜«˜ *cascade08«˜®˜*cascade08®˜¯˜ *cascade08¯˜³˜*cascade08³˜à˜ *cascade08à˜ä˜*cascade08ä˜Ÿ™ *cascade08Ÿ™À™*cascade08À™›š *cascade08›š š*cascade08 š°š *cascade08°š³š*cascade08³š´š *cascade08´š¼š*cascade08¼šùš *cascade08ùš›*cascade08›‘› *cascade08‘›ê*cascade08ê—Ÿ *cascade08—Ÿ™Ÿ*cascade08™Ÿ­Ÿ *cascade08­ŸµŸ*cascade08µŸ·Ÿ*cascade08·ŸÅŸ *cascade08ÅŸÉŸ*cascade08ÉŸÏŸ*cascade08ÏŸãŸ *cascade08ãŸåŸ*cascade08åŸüŸ *cascade08üŸ„ *cascade08„ ”  *cascade08” ˜ *cascade08˜ ¥  *cascade08¥ ÿ¡*cascade08ÿ¡…¢ *cascade08…¢¦£*cascade08¦£§£ *cascade08§£–¤*cascade08–¤˜¤ *cascade08˜¤¸¤*cascade08¸¤¹¤ *cascade08¹¤Ï¤*cascade08Ï¤Ñ¤ *cascade08Ñ¤©¥*cascade08©¥ª¥ *cascade08ª¥²¥*cascade08²¥³¥ *cascade08³¥À¥*cascade08À¥Â¥ *cascade08Â¥ø¥*cascade08ø¥ù¥ *cascade08ù¥®¦*cascade08®¦¯¦ *cascade08¯¦§*cascade08§§ *cascade08§™§*cascade08™§š§ *cascade08š§Ö§*cascade08Ö§×§ *cascade08×§¡¨*cascade08¡¨£¨ *cascade08£¨µ¨*cascade08µ¨¶¨ *cascade08¶¨½¨*cascade08½¨Í¨ *cascade08Í¨Î¨*cascade08Î¨Ï¨ *cascade08Ï¨×¨*cascade08×¨ú¨ *cascade08ú¨©*cascade08©•© *cascade08•©–©*cascade08–©°© *cascade08°©¸©*cascade08¸©õ© *cascade08õ©ı©*cascade08ı©¡ª *cascade08¡ª¢ª*cascade08¢ª¤ª *cascade08¤ª¥ª*cascade08¥ª·ª *cascade08·ª¿ª*cascade08¿ªÁª *cascade08ÁªÉª*cascade08Éª•« *cascade08•«³«*cascade08³«´« *cascade08´«Û®*cascade08Û®ˆ¯ *cascade08ˆ¯Š¯*cascade08Š¯’¯ *cascade08’¯”¯*cascade08”¯•¯ *cascade08•¯™¯*cascade08™¯¡¯ *cascade08
¡¯ê²ê²…³ *cascade08…³•µ*cascade08•µÄµ *cascade08Äµ•¿ *cascade08"(23dcd19fd43a9d64277ab854eba1248670bd74982&file:///root/backend/oj_class/views.py:file:///root/backend