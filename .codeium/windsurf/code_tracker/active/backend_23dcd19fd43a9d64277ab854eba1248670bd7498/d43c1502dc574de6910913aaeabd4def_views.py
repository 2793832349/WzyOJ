ï@from django.core.cache import cache
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
        
        # æ ¹æ® problem_list_mode å‚æ•°è¿‡æ»¤
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
        
        # é¢˜å•æ¨¡å¼ï¼šç»Ÿè®¡ACé¢˜ç›®æ•°é‡
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
                # èŽ·å–æ‰€æœ‰æäº¤ï¼Œä¸é™æ—¶é—´
                submissions = user.submissions.filter(
                    problem_id__in=problem_ids,
                ).order_by('create_time')
                
                item = {
                    **UserBriefSerializer(user).data,
                    'latest_submit': 0,
                    'problems': [],
                    'ac_count': 0  # ACé¢˜ç›®æ•°é‡
                }
                
                solved_problems = {}
                for submission in submissions:
                    # åªè®°å½•æ¯é“é¢˜çš„æœ€é«˜åˆ†æäº¤
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
                
                # ç»Ÿè®¡ACé¢˜ç›®æ•°é‡ï¼ˆscore == 100ï¼‰
                item['ac_count'] = sum(1 for p in solved_problems.values() if p['score'] == 100)
                item['score'] = sum([i['score'] for i in solved_problems.values()])
                
                for problem in solved_problems.values():
                    item['problems'].append(problem)
                item['problems'].sort(key=lambda x: problem_ids.index(x['id']))
                res['users'].append(item)
            
            # æŒ‰ACæ•°é‡æŽ’åºï¼ŒACæ•°é‡ç›¸åŒåˆ™æŒ‰æ€»åˆ†æŽ’åºï¼Œæ€»åˆ†ç›¸åŒåˆ™æŒ‰æœ€åŽæäº¤æ—¶é—´æŽ’åº
            res['users'].sort(key=lambda x: (-x['ac_count'], -x['score'], x['latest_submit']))
            for i in res['users']:
                i.pop('latest_submit')
            
            cache.set(f'problemset_ranking_{pk}', res, 300)  # ç¼“å­˜5åˆ†é’Ÿ
            return Response(res)
        
        # æ¯”èµ›æ¨¡å¼ï¼šåŽŸæœ‰é€»è¾‘
        if contest.start_time > timezone.now():
            return Response({'detail': _('Contest has not started.')})
        if not (self.permission in self.request.user.permissions
                and request.GET.get('force_update') == 'true'):
            data = cache.get(f'contest_ranking_{pk}')
            if data is not None:
                return Response(data)

        res = {'users': [], 'time': timezone.now().isoformat()}

        users = contest.users.all()
        problems = contest.problems.all()
        problem_ids = [i.id for i in problems]
        for user in users:
            submissions = user.submissions.filter(
                create_time__range=(contest.start_time, contest.end_time),
                problem_id__in=problem_ids,
            ).order_by('create_time')
            item = {
                **UserBriefSerializer(user).data, 'latest_submit': 0,
                'problems': []
            }
            problems = {}
            for submission in submissions:
                if problems.get(submission.problem_id
                                ) is None or submission.score > problems[
                                    submission.problem_id]['score']:
                    problems[submission.problem.id] = {
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
            item['score'] = sum([i['score'] for i in problems.values()])
            for problem in problems.values():
                item['problems'].append(problem)
            item['problems'].sort(key=lambda x: problem_ids.index(x['id']))
            res['users'].append(item)

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
Õ *cascade08ÕŒ*cascade08Œ¶ *cascade08¶©*cascade08©¹ *cascade08¹Þ*cascade08Þà *cascade08àû*cascade08ûü *cascade08ü”*cascade08”• *cascade08•«*cascade08«¬ *cascade08¬ÿ*cascade08ÿ€ *cascade08€„*cascade08„… *cascade08…Ø*cascade08ØÙ *cascade08ÙŒ*cascade08Œ *cascade08Í*cascade08ÍÎ *cascade08ÎÓ*cascade08ÓÔ *cascade08Ôá*cascade08áã *cascade08ãå*cascade08åæ *cascade08æç*cascade08çè *cascade08è *cascade08 ¡ *cascade08¡°*cascade08°± *cascade08±æ*cascade08æç *cascade08çè*cascade08èé *cascade08é” *cascade08” •  *cascade08• ¯ *cascade08¯ ²  *cascade08² š!*cascade08š!›! *cascade08›!Ô#*cascade08Ô#Û# *cascade08Û#‡$*cascade08‡$ˆ$ *cascade08ˆ$·$*cascade08·$¸$ *cascade08¸$ý$*cascade08ý$þ$ *cascade08þ$€%*cascade08€%% *cascade08%¯%*cascade08¯%°% *cascade08°%Ø%*cascade08Ø%Ù% *cascade08Ù%â%*cascade08â%ã% *cascade08ã%ç%*cascade08ç%è% *cascade08è%ý%*cascade08ý%þ% *cascade08þ%ˆ&*cascade08ˆ&‰& *cascade08‰&Ž&*cascade08Ž&& *cascade08&—&*cascade08—&˜& *cascade08˜&œ&*cascade08œ&& *cascade08&ª)*cascade08ª)«) *cascade08«)¶)*cascade08¶)·) *cascade08·)˜**cascade08˜*ï@ *cascade08"(23dcd19fd43a9d64277ab854eba1248670bd74982(file:///root/backend/oj_contest/views.py:file:///root/backend