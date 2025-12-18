import hashlib
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
    """班级视图集"""
    queryset = Class.objects.all()
    serializer_class = ClassSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """过滤查询集"""
        user = self.request.user
        queryset = Class.objects.all()
        
        # 过滤已解散的班级
        queryset = queryset.filter(is_disbanded=False)
        
        # 非管理员只能看到自己的班级
        if not user.is_staff:
            queryset = queryset.filter(
                Q(teacher=user) |  # 自己创建的
                Q(members__user=user)  # 自己加入的
            ).distinct()
        
        # 过滤隐藏的班级（非教师）
        if not user.is_staff:
            queryset = queryset.exclude(
                Q(is_hidden=True) & ~Q(teacher=user)
            )
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        """创建班级时设置教师为当前用户"""
        class_obj = serializer.save(teacher=self.request.user)
        # 自动将创建者添加为教师成员
        ClassStudent.objects.create(
            class_obj=class_obj,
            user=self.request.user,
            role='teacher'
        )
    
    @action(detail=True, methods=['get'])
    def students(self, request, pk=None):
        """获取班级学生列表"""
        class_obj = self.get_object()
        students = class_obj.members.all()
        serializer = ClassStudentSerializer(students, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_student(self, request, pk=None):
        """添加学生到班级"""
        class_obj = self.get_object()
        
        # 检查权限：只有教师可以添加学生
        if class_obj.teacher != request.user:
            return Response(
                {'error': '只有教师可以添加学生'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        user_id = request.data.get('user_id')
        role = request.data.get('role', 'student')
        
        if not user_id:
            return Response(
                {'error': '缺少 user_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 检查用户是否已在班级中
        if class_obj.members.filter(user_id=user_id).exists():
            return Response(
                {'error': '用户已在班级中'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 添加学生
        membership = ClassStudent.objects.create(
            class_obj=class_obj,
            user_id=user_id,
            role=role
        )
        
        serializer = ClassStudentSerializer(membership)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def remove_student(self, request, pk=None):
        """从班级移除学生"""
        class_obj = self.get_object()
        
        # 检查权限
        if class_obj.teacher != request.user:
            return Response(
                {'error': '只有教师可以移除学生'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        user_id = request.data.get('user_id')
        if not user_id:
            return Response(
                {'error': '缺少 user_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 移除学生
        deleted_count, _ = class_obj.members.filter(user_id=user_id).delete()
        
        if deleted_count == 0:
            return Response(
                {'error': '用户不在班级中'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response({'message': '移除成功'})
    
    @action(detail=True, methods=['post'])
    def disband(self, request, pk=None):
        """解散班级"""
        class_obj = self.get_object()
        
        # 检查权限：只有教师可以解散班级
        if class_obj.teacher != request.user:
            return Response(
                {'error': '只有教师可以解散班级'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # 标记班级为已解散
        class_obj.is_disbanded = True
        class_obj.save()
        
        # 移除所有成员
        class_obj.members.all().delete()
        
        return Response({'message': '班级已解散'})
    
    @action(detail=True, methods=['post'])
    def update_member_role(self, request, pk=None):
        """更新班级成员角色"""
        class_obj = self.get_object()
        
        # 检查权限：只有教师可以更新成员角色
        if class_obj.teacher != request.user:
            return Response(
                {'error': '只有教师可以更新成员角色'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        user_id = request.data.get('user_id')
        role = request.data.get('role')
        
        if not user_id:
            return Response(
                {'error': '缺少 user_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if role not in ['student', 'teacher']:
            return Response(
                {'error': '角色必须是 student 或 teacher'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 更新成员角色
        try:
            membership = class_obj.members.get(user_id=user_id)
            membership.role = role
            membership.save()
            
            serializer = ClassStudentSerializer(membership)
            return Response(serializer.data)
        except ClassStudent.DoesNotExist:
            return Response(
                {'error': '用户不在班级中'},
                status=status.HTTP_404_NOT_FOUND
            )


class ClassProblemViewSet(viewsets.ModelViewSet):
    """班级题目视图集"""
    queryset = ClassProblem.objects.all()
    serializer_class = ClassProblemSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """过滤查询集"""
        queryset = ClassProblem.objects.all()
        
        # 按班级过滤
        class_id = self.request.query_params.get('class_id')
        if class_id:
            queryset = queryset.filter(class_obj_id=class_id)
        
        return queryset.order_by('order', 'created_at')
    
    def perform_create(self, serializer):
        """创建题目时检查权限"""
        from rest_framework.exceptions import PermissionDenied
        
        class_obj = serializer.validated_data.get('class_obj')
        
        # 检查权限：只有教师可以添加题目
        if class_obj.teacher != self.request.user:
            raise PermissionDenied('只有教师可以添加题目')
        
        serializer.save()
    
    @action(detail=False, methods=['post'])
    def reference(self, request):
        """引用主题库题目到班级"""
        class_id = request.data.get('class_id')
        problem_id = request.data.get('problem_id')
        
        if not class_id or not problem_id:
            return Response(
                {'error': '缺少 class_id 或 problem_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        class_obj = get_object_or_404(Class, id=class_id)
        
        # 检查权限
        if class_obj.teacher != request.user:
            return Response(
                {'error': '只有教师可以添加题目'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        problem = get_object_or_404(Problem, id=problem_id)
        
        # 检查是否已引用
        if class_obj.problems.filter(reference_problem=problem).exists():
            return Response(
                {'error': '该题目已被引用'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 创建引用
        class_problem = ClassProblem.objects.create(
            class_obj=class_obj,
            reference_problem=problem,
            is_reference=True
        )
        
        serializer = self.get_serializer(class_problem)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'], url_path='upload-test-data')
    def upload_test_data(self, request, pk=None):
        """上传测试数据（.zip文件）"""
        class_problem = self.get_object()
        
        # 检查权限：只有教师可以上传测试数据，且不能是引用题目
        if class_problem.class_obj.teacher != request.user:
            return Response(
                {'error': '只有教师可以上传测试数据'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if class_problem.is_reference:
            return Response(
                {'error': '引用题目不能上传测试数据'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        test_cases_file = request.FILES.get('file')
        if not test_cases_file:
            return Response(
                {'error': '未上传文件'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 检查文件类型
        if not test_cases_file.name.endswith('.zip'):
            return Response(
                {'error': '只支持 .zip 格式的文件'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 创建测试数据目录（使用题目ID）
        data_dir = settings.TEST_DATA_ROOT / 'class' / str(pk)
        data_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # 解压文件
            test_cases = ZipFile(test_cases_file, 'r')
            test_cases.extractall(data_dir)
            
            # 处理答案文件并计算MD5
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
            
            # 更新题目的测试用例配置
            if not class_problem.test_case_config:
                # 自动生成测试用例配置
                config = {
                    'test_cases': []
                }
                # 查找所有 .in 文件
                in_files = sorted([f['name'] for f in test_case_files if f['ext'] == 'in'])
                for in_file in in_files:
                    # 查找对应的输出文件（.ans 或 .out）
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
                'message': '测试数据上传成功',
                'files': [f'{f["name"]}.{f["ext"]}' for f in test_case_files]
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'解压或处理文件失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AssignmentViewSet(viewsets.ModelViewSet):
    """作业视图集"""
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """过滤查询集"""
        queryset = Assignment.objects.all()
        
        # 按班级过滤
        class_id = self.request.query_params.get('class_id')
        if class_id:
            queryset = queryset.filter(class_obj_id=class_id)
        
        # 学生只能看到未隐藏的作业
        user = self.request.user
        if not user.is_staff:
            # 获取用户是教师的班级
            teacher_class_ids = Class.objects.filter(teacher=user).values_list('id', flat=True)
            # 如果不是教师，则过滤隐藏的作业
            queryset = queryset.exclude(
                Q(is_hidden=True) & ~Q(class_obj_id__in=teacher_class_ids)
            )
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        """创建作业时检查权限"""
        from rest_framework.exceptions import PermissionDenied, ValidationError
        from .models import AssignmentProblem
        from oj_problem.models import Problem
        import logging
        
        logger = logging.getLogger(__name__)
        class_obj = serializer.validated_data.get('class_obj')
        
        # 检查权限：只有教师可以创建作业
        if class_obj.teacher != self.request.user:
            raise PermissionDenied('只有教师可以创建作业')
        
        assignment = serializer.save()
        
        # 处理题目ID列表
        problem_ids = self.request.data.get('problem_ids', [])
        if problem_ids:
            for order, problem_id in enumerate(problem_ids):
                try:
                    # 验证题目是否存在
                    if not Problem.objects.filter(id=problem_id).exists():
                        logger.error(f"Problem with id {problem_id} does not exist")
                        raise ValidationError(f'题目 ID {problem_id} 不存在')
                    
                    # 先检查或创建班级题目引用
                    class_problem, created = ClassProblem.objects.get_or_create(
                        class_obj=class_obj,
                        reference_problem_id=problem_id,
                        defaults={
                            'is_reference': True,
                            'order': order,
                        }
                    )
                    # 创建作业题目关联
                    AssignmentProblem.objects.create(
                        assignment=assignment,
                        problem=class_problem,
                        order=order
                    )
                except Exception as e:
                    logger.error(f"Error adding problem {problem_id} to assignment: {str(e)}")
                    raise ValidationError(f'添加题目失败: {str(e)}')
    
    def perform_update(self, serializer):
        """更新作业"""
        from rest_framework.exceptions import PermissionDenied, ValidationError
        from .models import AssignmentProblem
        from oj_problem.models import Problem
        import logging
        
        logger = logging.getLogger(__name__)
        assignment = self.get_object()
        
        # 检查权限
        if assignment.class_obj.teacher != self.request.user:
            raise PermissionDenied('只有教师可以编辑作业')
        
        serializer.save()
        
        # 更新题目列表
        problem_ids = self.request.data.get('problem_ids', None)
        if problem_ids is not None:
            # 删除旧的题目关联
            AssignmentProblem.objects.filter(assignment=assignment).delete()
            
            # 添加新的题目关联
            for order, problem_id in enumerate(problem_ids):
                try:
                    # 验证题目是否存在
                    if not Problem.objects.filter(id=problem_id).exists():
                        logger.error(f"Problem with id {problem_id} does not exist")
                        raise ValidationError(f'题目 ID {problem_id} 不存在')
                    
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
                    raise ValidationError(f'添加题目失败: {str(e)}')
    
    @action(detail=True, methods=['get'], url_path='problems')
    def get_problems(self, request, pk=None):
        """获取作业的题目列表"""
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
        """获取作业成绩表"""
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            assignment = self.get_object()
            class_obj = assignment.class_obj
            
            # 检查权限：只有教师可以查看成绩表
            if class_obj.teacher != request.user:
                return Response(
                    {'error': '只有教师可以查看成绩表'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            from .models import AssignmentProblem
            from oj_submission.models import Submission
            
            # 获取班级学生
            students = class_obj.members.filter(role='student').select_related('user')
            
            # 获取作业题目列表
            assignment_problems = AssignmentProblem.objects.filter(
                assignment=assignment
            ).select_related('problem', 'problem__reference_problem').order_by('order')
            
            # 构建成绩数据
            grades_data = []
            for student_membership in students:
                student = student_membership.user
                student_data = {
                    'student_id': student.student_id or student.username,
                    'real_name': student.real_name or student.username,
                    'username': student.username,
                    'problems': []
                }
                
                # 检查每道题的完成情况
                for ap in assignment_problems:
                    try:
                        problem_id = ap.problem.reference_problem_id if ap.problem.is_reference else ap.problem.id
                        
                        # 查找该学生对该题目的最佳提交
                        # 优先查找 AC 的提交，如果没有则取最新的提交
                        ac_submission = Submission.objects.filter(
                            user=student,
                            problem_id=problem_id,
                            status=0  # ACCEPTED
                        ).first()
                        
                        if not ac_submission:
                            # 如果没有 AC，取最新的提交
                            best_submission = Submission.objects.filter(
                                user=student,
                                problem_id=problem_id,
                            ).order_by('-create_time').first()
                        else:
                            best_submission = ac_submission
                        
                        # 将状态码转换为字符串
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
                        # 添加错误信息的题目状态
                        student_data['problems'].append({
                            'problem_id': None,
                            'problem_title': f'错误: {str(e)}',
                            'status': None,
                        })
                
                grades_data.append(student_data)
            
            # 按完成数排序（降序）
            for student_data in grades_data:
                student_data['completed_count'] = sum(1 for p in student_data['problems'] if p['status'] == 'AC')
            grades_data.sort(key=lambda x: x['completed_count'], reverse=True)
            
            # 添加排名序号
            for rank, student_data in enumerate(grades_data, start=1):
                student_data['rank'] = rank
            
            return Response(grades_data)
        except Exception as e:
            logger.error(f"Error in get_grades: {str(e)}", exc_info=True)
            return Response(
                {'error': f'获取成绩表失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """获取作业统计信息"""
        assignment = self.get_object()
        class_obj = assignment.class_obj
        
        # 检查权限：只有教师可以查看统计
        if class_obj.teacher != request.user:
            return Response(
                {'error': '只有教师可以查看统计'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # 获取班级学生
        students = class_obj.members.filter(role='student')
        
        # TODO: 实现详细的统计逻辑
        # 这里需要关联 submission 模型来统计每个学生的完成情况
        stats_data = []
        for student_membership in students:
            stats_data.append({
                'student': student_membership.user,
                'total_problems': assignment.problems.count(),
                'solved_problems': 0,  # TODO: 从 submission 统计
                'submission_count': 0,  # TODO: 从 submission 统计
                'completion_rate': 0.0,
                'last_submit_time': None,
            })
        
        serializer = AssignmentStatSerializer(stats_data, many=True)
        return Response(serializer.data)
