’[from django.core.cache import cache
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
        
        # æ£€æŸ¥å…¬å¼€æ’è¡Œæ¦œæƒé™
        if not contest.public_ranking and not request.user.is_authenticated:
            return Response({'detail': _('Please login to view ranking.')}, status=401)
        
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
                # è·å–æ‰€æœ‰æäº¤ï¼Œä¸é™æ—¶é—´
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
            
            # æŒ‰ACæ•°é‡æ’åºï¼ŒACæ•°é‡ç›¸åŒåˆ™æŒ‰æ€»åˆ†æ’åºï¼Œæ€»åˆ†ç›¸åŒåˆ™æŒ‰æœ€åæäº¤æ—¶é—´æ’åº
            res['users'].sort(key=lambda x: (-x['ac_count'], -x['score'], x['latest_submit']))
            for i in res['users']:
                i.pop('latest_submit')
            
            cache.set(f'problemset_ranking_{pk}', res, 300)  # ç¼“å­˜5åˆ†é’Ÿ
            return Response(res)
        
        # æ¯”èµ›æ¨¡å¼ï¼šæ ¹æ®èµ›åˆ¶è®¡ç®—æ’å
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
        
        # åˆ¤æ–­æ˜¯å¦å°æ¦œ
        now = timezone.now()
        is_frozen = (contest.freeze_time and 
                    contest.freeze_time <= now < contest.end_time and
                    contest.rule_type == 'ACM')
        
        # ç®¡ç†å‘˜å¯ä»¥çœ‹åˆ°å®æ—¶æ¦œå•
        is_admin = self.permission in request.user.permissions if request.user.is_authenticated else False
        
        if is_frozen and not is_admin:
            res['is_frozen'] = True
        
        for user in users:
            # å°æ¦œæœŸé—´ï¼Œæ™®é€šç”¨æˆ·åªèƒ½çœ‹åˆ°å°æ¦œå‰çš„æäº¤
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
                'penalty': 0,  # ACM ç½šæ—¶
                'ac_count': 0,  # ACM AC æ•°é‡
            }
            
            solved_problems = {}
            problem_attempts = {}  # è®°å½•æ¯é¢˜çš„å°è¯•æ¬¡æ•°ï¼ˆç”¨äº ACM ç½šæ—¶ï¼‰
            
            for submission in submissions:
                pid = submission.problem_id
                
                # ACM èµ›åˆ¶
                if contest.rule_type == 'ACM':
                    if pid not in problem_attempts:
                        problem_attempts[pid] = {'wa_count': 0, 'ac_time': None}
                    
                    # å¦‚æœå·²ç» ACï¼Œè·³è¿‡åç»­æäº¤
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
                        # è®¡ç®—ç½šæ—¶ï¼šæäº¤æ—¶é—´ï¼ˆåˆ†é’Ÿï¼‰+ WAæ¬¡æ•° * 20
                        time_penalty = int((submission.create_time - contest.start_time).total_seconds() / 60)
                        item['penalty'] += time_penalty + problem_attempts[pid]['wa_count'] * 20
                    else:
                        # WA
                        problem_attempts[pid]['wa_count'] += 1
                
                # IOI/OI èµ›åˆ¶ï¼šå–æœ€é«˜åˆ†
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

        # æ ¹æ®èµ›åˆ¶æ’åº
        if contest.rule_type == 'ACM':
            # ACM: ACæ•° é™åº -> ç½šæ—¶ å‡åº
            res['users'].sort(key=lambda x: (-x['ac_count'], x['penalty']))
        else:
            # IOI/OI: æ€»åˆ† é™åº -> æœ€åæäº¤æ—¶é—´ å‡åº
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
à à´*cascade08
´à+ à+ø+*cascade08
ø+ş. ş.‹/*cascade08
‹/˜/ ˜/¥/*cascade08
¥/Ç/ Ç/É/ *cascade08É/Ö/*cascade08Ö/ô/ *cascade08ô/0*cascade08
01 1§1*cascade08
§1¯1 ¯1ì1*cascade08
ì1í1 í1î1*cascade08
î1ï1 ï1ÿ1*cascade08
ÿ1€2 €22*cascade08
22 2ò2*cascade08
ò2ó2 ó2Ã3*cascade08
Ã3Ä3 Ä3Ó3*cascade08
Ó3Õ3 Õ3Ü3*cascade08
Ü3à3 à3è3*cascade08
è3ì3 ì3ò3*cascade08
ò3ó3 ó3Ó4*cascade08
Ó4á4 á4 6*cascade08
 6Ç6 Ç6À8*cascade08
À8‹9 ‹99*cascade08
9»9 »9¿9*cascade08
¿9å9 å9ò9*cascade08
ò9¸: ¸:È:*cascade08
È:û: û:Ø;*cascade08
Ø;ó; ó;‡<*cascade08
‡<¡< ¡<†=*cascade08
†=µ= µ=¶=*cascade08
¶=·= ·=¸=*cascade08
¸=¹= ¹=Æ=*cascade08
Æ=Í= Í=—>*cascade08
—>˜> ˜>™>*cascade08
™>š> š>>*cascade08
>> >Ÿ>*cascade08
Ÿ> >  >®A*cascade08
®A¹A ¹AßA*cascade08
ßAçA çAñA*cascade08
ñAóA óA˜B*cascade08
˜B±B ±BÛB*cascade08
ÛBãB ãBäB*cascade08
äBåB åBçB*cascade08
çBèB èBëB*cascade08
ëBìB ìBôB*cascade08
ôBöB öBüB*cascade08
üBıB ıB…C*cascade08
…C†C †C°C*cascade08
°C±C ±C´C*cascade08
´CµC µCçC*cascade08
çCôC ôC™D*cascade08
™DD D·D*cascade08
·D¸D ¸DĞE*cascade08
ĞEØE ØEàE*cascade08
àEâE âEóE*cascade08
óE†F †FG*cascade08
GŸG ŸG¹G*cascade08
¹GÄG ÄG¶H*cascade08
¶H¾H ¾HÈH*cascade08
ÈHÍH ÍHĞH*cascade08
ĞHÒH ÒH­I*cascade08
­I®I ®I±I*cascade08
±I²I ²IËI*cascade08
ËIÍI ÍI§J*cascade08
§J½J ½JÒJ*cascade08
ÒJÚJ ÚJŞJ*cascade08
ŞJéJ éJøJ*cascade08
øJÿJ ÿJ¹K*cascade08
¹KÁK ÁKÅK*cascade08
ÅKúK úKşK*cascade08
şKÑL ÑLÕL*cascade08
ÕLòL òLöL*cascade08
öLÁM ÁMÅM*cascade08
ÅMñM ñMõM*cascade08
õMÁN ÁNÅN*cascade08
ÅNÇN ÇNËN*cascade08
ËN”O ”O˜O*cascade08
˜O¯O ¯O³O*cascade08
³OƒP ƒP‡P*cascade08
‡P•P •P¢P*cascade08
¢PËP ËPÒP*cascade08
ÒPQ QˆQ*cascade08
ˆQÇR ÇRÛT*cascade08
ÛTU U¦U*cascade08
¦U’[ "(6b457f522aa10499b55789fae01ec35627afe7b62(file:///root/backend/oj_contest/views.py:file:///root/backend