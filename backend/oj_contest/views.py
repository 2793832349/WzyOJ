from django.core.cache import cache
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from oj_backend.permissions import Granted, IsAuthenticatedAndReadOnly
from oj_problem.serializers import ProblemBriefSerializer
from oj_user.serializers import UserBriefSerializer
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Contest
from .serializers import ContestDetailSerializer, ContestSerializer


class ContestPagination(LimitOffsetPagination):
    default_limit = 50
    max_limit = 200


class ContestViewSet(ModelViewSet):
    permission_classes = [Granted | IsAuthenticatedAndReadOnly]
    permission = 'contest'
    lookup_value_regex = r'\d+'
    pagination_class = ContestPagination
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ['id', 'title']
    ordering_fields = ['id', 'title']
    filterset_fields = []

    def get_queryset(self):
        if self.permission in self.request.user.permissions:
            queryset = Contest.objects.all()
        else:
            queryset = Contest.objects.filter(
                Q(is_hidden=False) | Q(users=self.request.user.id)).distinct()
        
        # 根据 problem_list_mode 参数过滤
        problem_list_mode = self.request.query_params.get('problem_list_mode')
        if problem_list_mode is not None:
            if problem_list_mode.lower() in ['true', '1']:
                queryset = queryset.filter(problem_list_mode=True)
            elif problem_list_mode.lower() in ['false', '0']:
                queryset = queryset.filter(problem_list_mode=False)
        
        return queryset.order_by('-id')

    def get_serializer_class(self):
        if self.action == 'list':
            return ContestSerializer
        return ContestDetailSerializer

    @action(detail=True, methods=['get'], url_path='ranking')
    def get_ranking(self, request, pk):
        contest = self.get_object()
        
        # 检查公开排行榜权限
        if not contest.public_ranking and not request.user.is_authenticated:
            return Response({'detail': _('Please login to view ranking.')}, status=401)
        
        # 题单模式：统计AC题目数量
        if contest.problem_list_mode:
            if not (self.permission in self.request.user.permissions
                    and request.GET.get('force_update') == 'true'):
                data = cache.get(f'problemset_ranking_{pk}')
                if data is not None:
                    return Response(data)
            
            res = {'users': [], 'time': timezone.now().isoformat()}
            users = contest.users.all()
            problems = contest.problems.all()
            problem_ids = [i.id for i in problems]
            
            for user in users:
                # 获取所有提交，不限时间
                submissions = user.submissions.filter(
                    problem_id__in=problem_ids,
                ).order_by('create_time')
                
                item = {
                    **UserBriefSerializer(user).data,
                    'latest_submit': 0,
                    'problems': [],
                    'ac_count': 0  # AC题目数量
                }
                
                solved_problems = {}
                for submission in submissions:
                    # 只记录每道题的最高分提交
                    if solved_problems.get(submission.problem_id) is None or \
                       submission.score > solved_problems[submission.problem_id]['score']:
                        solved_problems[submission.problem.id] = {
                            'id': submission.problem.id,
                            'title': submission.problem.title,
                            'status': submission.status,
                            'score': submission.score,
                            'time': submission.create_time.isoformat(),
                            'submission_id': submission.id,
                        }
                        item['latest_submit'] = max(
                            item['latest_submit'],
                            submission.create_time.timestamp(),
                        )
                
                # 统计AC题目数量（score == 100）
                item['ac_count'] = sum(1 for p in solved_problems.values() if p['score'] == 100)
                item['score'] = sum([i['score'] for i in solved_problems.values()])
                
                for problem in solved_problems.values():
                    item['problems'].append(problem)
                item['problems'].sort(key=lambda x: problem_ids.index(x['id']))
                res['users'].append(item)
            
            # 按AC数量排序，AC数量相同则按总分排序，总分相同则按最后提交时间排序
            res['users'].sort(key=lambda x: (-x['ac_count'], -x['score'], x['latest_submit']))
            for i in res['users']:
                i.pop('latest_submit')
            
            cache.set(f'problemset_ranking_{pk}', res, 300)  # 缓存5分钟
            return Response(res)
        
        # 比赛模式：根据赛制计算排名
        if contest.start_time > timezone.now():
            return Response({'detail': _('Contest has not started.')})
        if not (self.permission in self.request.user.permissions
                and request.GET.get('force_update') == 'true'):
            data = cache.get(f'contest_ranking_{pk}')
            if data is not None:
                return Response(data)

        res = {
            'users': [], 
            'time': timezone.now().isoformat(), 
            'rule_type': contest.rule_type,
            'is_frozen': False,
        }

        users = contest.users.all()
        problems = contest.problems.all()
        problem_ids = [i.id for i in problems]
        
        # 判断是否封榜
        now = timezone.now()
        is_frozen = (contest.freeze_time and 
                    contest.freeze_time <= now < contest.end_time and
                    contest.rule_type == 'ACM')
        
        # 管理员可以看到实时榜单
        is_admin = self.permission in request.user.permissions if request.user.is_authenticated else False
        
        if is_frozen and not is_admin:
            res['is_frozen'] = True
        
        for user in users:
            # 封榜期间，普通用户只能看到封榜前的提交
            if is_frozen and not is_admin:
                submissions = user.submissions.filter(
                    create_time__range=(contest.start_time, contest.freeze_time),
                    problem_id__in=problem_ids,
                ).order_by('create_time')
            else:
                submissions = user.submissions.filter(
                    create_time__range=(contest.start_time, contest.end_time),
                    problem_id__in=problem_ids,
                ).order_by('create_time')
            
            item = {
                **UserBriefSerializer(user).data,
                'latest_submit': 0,
                'problems': [],
                'penalty': 0,  # ACM 罚时
                'ac_count': 0,  # ACM AC 数量
            }
            
            solved_problems = {}
            problem_attempts = {}  # 记录每题的尝试次数（用于 ACM 罚时）
            
            for submission in submissions:
                pid = submission.problem_id
                
                # ACM 赛制
                if contest.rule_type == 'ACM':
                    if pid not in problem_attempts:
                        problem_attempts[pid] = {'wa_count': 0, 'ac_time': None}
                    
                    # 如果已经 AC，跳过后续提交
                    if problem_attempts[pid]['ac_time'] is not None:
                        continue
                    
                    # AC
                    if submission.score == 100:
                        problem_attempts[pid]['ac_time'] = submission.create_time
                        solved_problems[pid] = {
                            'id': submission.problem.id,
                            'title': submission.problem.title,
                            'status': submission.status,
                            'score': 100,
                            'time': submission.create_time.isoformat(),
                            'submission_id': submission.id,
                            'wa_count': problem_attempts[pid]['wa_count'],
                        }
                        item['ac_count'] += 1
                        # 计算罚时：提交时间（分钟）+ WA次数 * 20
                        time_penalty = int((submission.create_time - contest.start_time).total_seconds() / 60)
                        item['penalty'] += time_penalty + problem_attempts[pid]['wa_count'] * 20
                    else:
                        # WA
                        problem_attempts[pid]['wa_count'] += 1
                
                # IOI/OI 赛制：取最高分
                else:
                    if pid not in solved_problems or submission.score > solved_problems[pid]['score']:
                        solved_problems[pid] = {
                            'id': submission.problem.id,
                            'title': submission.problem.title,
                            'status': submission.status,
                            'score': submission.score,
                            'time': submission.create_time.isoformat(),
                            'submission_id': submission.id,
                        }
                        item['latest_submit'] = max(
                            item['latest_submit'],
                            submission.create_time.timestamp(),
                        )
            
            item['score'] = sum([i['score'] for i in solved_problems.values()])
            for problem in solved_problems.values():
                item['problems'].append(problem)
            item['problems'].sort(key=lambda x: problem_ids.index(x['id']))
            res['users'].append(item)

        # 根据赛制排序
        if contest.rule_type == 'ACM':
            # ACM: AC数 降序 -> 罚时 升序
            res['users'].sort(key=lambda x: (-x['ac_count'], x['penalty']))
        else:
            # IOI/OI: 总分 降序 -> 最后提交时间 升序
            res['users'].sort(key=lambda x: (-x['score'], x['latest_submit']))
        
        for i in res['users']:
            i.pop('latest_submit')

        cache.set(
            f'contest_ranking_{pk}',
            res,
            60 if contest.end_time > timezone.now() else None,
        )

        return Response(res)

    @action(detail=True,
            methods=['post'],
            permission_classes=[IsAuthenticated],
            url_path='sign_up')
    def sign_up(self, request, pk):
        contest = self.get_object()
        if not contest.allow_sign_up:
            raise ValidationError(_('The contest disallows sign up.'))
        elif contest.end_time < timezone.now():
            raise ValidationError(_('The contest is over.'))
        contest.users.add(request.user)
        return Response(status=204)
