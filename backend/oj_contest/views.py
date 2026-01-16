from django.core.cache import cache, caches
from django.db.models import F
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from oj_backend.permissions import Granted, IsAuthenticatedAndReadOnly
from oj_problem.models import Problem
from oj_problem.serializers import ProblemBriefSerializer
from oj_submission.models import LanguageChoices, StatusChoices, Submission
from oj_submission.tasks import judge
from oj_user.models import User
from oj_user.serializers import UserBriefSerializer
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from zipfile import ZipFile
from pathlib import PurePosixPath
import json
import re

from .models import Contest, ContestProblem
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
        perms = getattr(self.request.user, 'permissions', []) if self.request.user.is_authenticated else []
        if self.permission in perms:
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

    def perform_update(self, serializer):
        contest = serializer.save()
        cache.delete(f'contest_ranking_{contest.id}')
        cache.delete(f'contest_ranking_{contest.id}_admin')
        cache.delete(f'contest_ranking_{contest.id}_frozen')
        cache.delete(f'problemset_ranking_{contest.id}')
        cache.delete(f'contest_ranking_revealed_at_{contest.id}')

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated],
        url_path='reveal_ranking',
    )
    def reveal_ranking(self, request, pk):
        contest = self.get_object()
        perms = getattr(request.user, 'permissions', [])
        is_admin = request.user.is_staff or ('contest' in perms)
        if not is_admin:
            return Response({'detail': 'Only admin can reveal ranking.'}, status=403)

        if contest.end_time is None or contest.end_time > timezone.now():
            return Response({'detail': 'Contest has not ended.'}, status=400)

        revealed_at = timezone.now().isoformat()
        cache.set(
            f'contest_ranking_revealed_at_{contest.id}',
            revealed_at,
            60 * 60 * 24 * 365 * 10,
        )

        cache.delete(f'contest_ranking_{contest.id}')
        cache.delete(f'contest_ranking_{contest.id}_admin')
        cache.delete(f'contest_ranking_{contest.id}_frozen')
        return Response({'ranking_revealed_at': revealed_at})

    @action(detail=True, methods=['get'], url_path='ranking')
    def get_ranking(self, request, pk):
        contest = self.get_object()
        perms = getattr(request.user, 'permissions', []) if request.user.is_authenticated else []
        now = timezone.now()
        
        # 检查公开排行榜权限
        if not contest.public_ranking and not request.user.is_authenticated:
            return Response({'detail': _('Please login to view ranking.')}, status=401)

        is_admin = self.permission in perms
        if contest.rule_type == 'OI':
            in_window = (
                (contest.start_time is None or contest.start_time < now)
                and (contest.end_time is None or contest.end_time > now)
            )
            if in_window and not is_admin:
                return Response({'detail': 'OI 模式比赛进行中不开放排行榜'}, status=403)
        
        # 题单模式：统计AC题目数量
        if contest.problem_list_mode:
            if not request.user.is_authenticated:
                return Response({'detail': _('Please login to view ranking.')}, status=401)

            progress_cache = caches['contest_progress']

            is_admin = self.permission in perms
            if not is_admin and not contest.users.filter(id=request.user.id).exists():
                return Response({'detail': _('Please sign up first.')}, status=403)

            if not (self.permission in perms
                    and request.GET.get('force_update') == 'true'):
                data = cache.get(f'problemset_ranking_{pk}')
                if data is not None:
                    return Response(data)
            
            res = {'users': [], 'time': timezone.now().isoformat()}
            users = contest.users.all()
            cps = (
                ContestProblem.objects
                .filter(contest=contest)
                .select_related('problem')
                .order_by('order', 'id')
            )
            problems = [cp.problem for cp in cps]
            problem_ids = [p.id for p in problems]
            
            for user in users:
                # 获取所有提交，不限时间
                reset_ts = progress_cache.get(f'contest_progress_reset_{pk}_{user.id}')
                reset_dt = None
                if reset_ts:
                    reset_dt = timezone.datetime.fromtimestamp(
                        float(reset_ts),
                        tz=timezone.get_current_timezone(),
                    )

                submissions = user.submissions.filter(problem_id__in=problem_ids)
                if reset_dt is not None:
                    submissions = submissions.filter(create_time__gte=reset_dt)
                submissions = submissions.order_by('create_time')
                
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
        if contest.start_time and contest.start_time > timezone.now():
            return Response({'detail': _('Contest has not started.')})

        is_admin = bool(request.user.is_authenticated and (request.user.is_staff or (self.permission in perms)))
        public_view = request.GET.get('public_view') == 'true'
        admin_as_public = bool(is_admin and public_view)
        revealed_at = cache.get(f'contest_ranking_revealed_at_{contest.id}')
        revealed = revealed_at is not None
        freeze_active = (
            contest.rule_type == 'ACM'
            and contest.freeze_time
            and contest.end_time
            and contest.freeze_time <= now
            and (now < contest.end_time or not revealed)
        )
        public_frozen = bool(freeze_active and (not is_admin or admin_as_public))

        cache_key = f'contest_ranking_{pk}'
        if contest.rule_type == 'ACM' and freeze_active:
            cache_key = f'{cache_key}_admin' if (is_admin and not admin_as_public) else f'{cache_key}_frozen'

        if not (self.permission in perms and request.GET.get('force_update') == 'true'):
            data = cache.get(cache_key)
            if data is not None:
                return Response(data)

        res = {
            'users': [], 
            'time': timezone.now().isoformat(), 
            'rule_type': contest.rule_type,
            'is_frozen': False,
        }

        users = contest.users.all()
        cps = (
            ContestProblem.objects
            .filter(contest=contest)
            .select_related('problem')
            .order_by('order', 'id')
        )
        problems = [cp.problem for cp in cps]
        problem_ids = [p.id for p in problems]

        # ACM: provide ordered problem meta for front-end columns
        if contest.rule_type == 'ACM':
            def _label(idx: int) -> str:
                # 0 -> A, 1 -> B ...
                return chr(ord('A') + idx)

            res['problems'] = [
                {
                    'id': p.id,
                    'title': p.title,
                    'label': _label(i),
                }
                for i, p in enumerate(problems)
            ]
        
        if public_frozen:
            res['is_frozen'] = True

        first_blood = {}
        if contest.rule_type == 'ACM' and problem_ids:
            fb_qs = Submission.objects.filter(
                problem_id__in=problem_ids,
                user_id__in=users.values_list('id', flat=True),
            )
            fb_qs = fb_qs.exclude(status__in=[StatusChoices.PENDING, StatusChoices.JUDGING])
            fb_qs = fb_qs.filter(Q(score=100) | Q(status=StatusChoices.ACCEPTED))
            if contest.start_time is not None:
                fb_qs = fb_qs.filter(create_time__gte=contest.start_time)
            fb_end = contest.freeze_time if public_frozen else (contest.end_time or timezone.now())
            if fb_end is not None:
                fb_qs = fb_qs.filter(create_time__lte=fb_end)

            for pid, uid in fb_qs.order_by('create_time').values_list('problem_id', 'user_id'):
                if pid not in first_blood:
                    first_blood[pid] = uid

        for user in users:
            # 封榜期间，普通用户只能看到封榜前的提交
            if public_frozen:
                submissions = user.submissions.filter(
                    create_time__range=(contest.start_time, contest.freeze_time),
                    problem_id__in=problem_ids,
                ).order_by('create_time')
            else:
                if contest.end_time is None:
                    end_time = timezone.now()
                else:
                    end_time = contest.end_time
                submissions = user.submissions.filter(
                    create_time__range=(contest.start_time, end_time),
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
            problem_statuses = {}
            
            for submission in submissions:
                pid = submission.problem_id
                
                # ACM 赛制
                if contest.rule_type == 'ACM':
                    if pid not in problem_attempts:
                        problem_attempts[pid] = {'wa_count': 0, 'ac_time': None}
                        problem_statuses[pid] = {'status': 'unsubmitted', 'wrong_count': 0, 'time': None}
                    
                    # 如果已经 AC，跳过后续提交
                    if problem_attempts[pid]['ac_time'] is not None:
                        continue

                    # 未出结果的提交不计入榜单
                    if submission.status in [StatusChoices.PENDING, StatusChoices.JUDGING]:
                        continue
                    
                    # AC
                    if submission.score == 100:
                        problem_attempts[pid]['ac_time'] = submission.create_time
                        problem_statuses[pid] = {
                            'status': 'ac',
                            'wrong_count': problem_attempts[pid]['wa_count'],
                            'time': int((submission.create_time - contest.start_time).total_seconds() / 60),
                        }
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
                        problem_statuses[pid] = {
                            'status': 'not_ac',
                            'wrong_count': problem_attempts[pid]['wa_count'],
                            'time': None,
                        }
                
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

            if contest.rule_type == 'ACM':
                # Ensure every problem has a status entry
                for pid in problem_ids:
                    if pid not in problem_statuses:
                        problem_statuses[pid] = {
                            'status': 'unsubmitted',
                            'wrong_count': 0,
                            'time': None,
                        }

                # Mark first blood (deep green on front-end)
                for pid in problem_ids:
                    if (
                        problem_statuses.get(pid, {}).get('status') == 'ac'
                        and first_blood.get(pid) == user.id
                    ):
                        problem_statuses[pid]['first_blood'] = True

                # Public frozen view: mark problems that have any submission after freeze
                if public_frozen:
                    after_end = contest.end_time or timezone.now()
                    after_submissions = user.submissions.filter(
                        create_time__gte=contest.freeze_time,
                        create_time__lte=after_end,
                        problem_id__in=problem_ids,
                    )
                    after_pids = set(after_submissions.values_list('problem_id', flat=True).distinct())
                    for pid in after_pids:
                        if problem_statuses.get(pid, {}).get('status') != 'ac':
                            problem_statuses[pid]['frozen'] = True

                item['problem_statuses'] = problem_statuses

            res['users'].append(item)

        # 根据赛制排序
        if contest.rule_type == 'ACM':
            # ACM: AC数 降序 -> 罚时 升序
            res['users'].sort(key=lambda x: (-x['ac_count'], x['penalty']))

            # Add tie-aware rank
            prev_key = None
            current_rank = 0
            for idx, u in enumerate(res['users'], start=1):
                key = (u.get('ac_count', 0), u.get('penalty', 0))
                if key != prev_key:
                    current_rank = idx
                    prev_key = key
                u['rank'] = current_rank
        else:
            # IOI/OI: 总分 降序 -> 最后提交时间 升序

            res['users'].sort(key=lambda x: (-x['score'], x['latest_submit']))
        
        for i in res['users']:
            i.pop('latest_submit')

        cache.set(
            cache_key,
            res,
            60 if contest.end_time and contest.end_time > timezone.now() else None,
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
        elif (not contest.problem_list_mode) and contest.end_time and contest.end_time < timezone.now():
            raise ValidationError(_('The contest is over.'))
        contest.users.add(request.user)
        return Response(status=204)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated],
        url_path='reset_progress',
    )
    def reset_progress(self, request, pk):
        contest = self.get_object()
        perms = getattr(request.user, 'permissions', [])
        is_admin = request.user.is_staff or ('contest' in perms)
        if not is_admin and not contest.users.filter(id=request.user.id).exists():
            return Response({'error': '请先报名/加入该题单'}, status=403)

        now = timezone.now()
        progress_cache = caches['contest_progress']
        progress_cache.set(
            f'contest_progress_reset_{contest.id}_{request.user.id}',
            now.timestamp(),
            60 * 60 * 24 * 365,
        )

        if contest.problem_list_mode:
            cache.delete(f'problemset_ranking_{contest.id}')
        return Response({'reset_time': now.isoformat()})

    @action(detail=True,
            methods=['post'],
            permission_classes=[IsAuthenticated],
            url_path='batch-upload-submissions')
    def batch_upload_submissions(self, request, pk=None):
        contest = self.get_object()

        perms = getattr(request.user, 'permissions', [])
        if self.permission not in perms:
            return Response({'error': '只有管理员可以批量上传评测'}, status=403)

        upload = request.FILES.get('file')
        if not upload:
            return Response({'error': '未上传文件'}, status=400)
        if not upload.name.lower().endswith('.zip'):
            return Response({'error': '只支持 .zip 格式的文件'}, status=400)

        problem_map_raw = request.data.get('problem_map')
        problem_map = None
        if problem_map_raw:
            try:
                problem_map = json.loads(problem_map_raw)
            except Exception:
                return Response({'error': 'problem_map 必须是 JSON'}, status=400)
            if not isinstance(problem_map, dict) or not problem_map:
                return Response({'error': 'problem_map 必须是非空对象'}, status=400)

        student_match = (request.data.get('student_match') or 'student_id').strip()
        if student_match not in ['student_id', 'username']:
            return Response({'error': 'student_match 只能是 student_id 或 username'}, status=400)

        freopen_policy = (request.data.get('freopen_policy') or 'ignore').strip()
        if freopen_policy not in ['ignore', 'require', 'forbid', 'keep']:
            return Response({'error': 'freopen_policy 只能是 ignore/require/forbid/keep'}, status=400)

        allowed_problem_ids = set(
            ContestProblem.objects.filter(contest=contest).values_list('problem_id', flat=True)
        )

        if problem_map is not None:
            mapped_problem_ids = set()
            for k, v in problem_map.items():
                try:
                    mapped_problem_ids.add(int(v))
                except Exception:
                    return Response({'error': f'problem_map 的值必须是题目ID: {k} -> {v}'}, status=400)

            invalid = [pid for pid in mapped_problem_ids if pid not in allowed_problem_ids]
            if invalid:
                return Response({'error': f'problem_map 含有不属于该比赛的题目ID: {invalid}'}, status=400)

        def _decode_code(data: bytes) -> str:
            try:
                return data.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    return data.decode('gbk')
                except Exception:
                    return data.decode('utf-8', errors='replace')

        freopen_re = re.compile(r'freopen\s*\([^;]*\)\s*;', re.S)

        def _has_freopen(source: str) -> bool:
            return bool(re.search(r'\bfreopen\s*\(', source))

        def _strip_freopen(source: str) -> str:
            return freopen_re.sub(';', source)

        ext_lang = {
            '.c': LanguageChoices.C,
            '.cpp': LanguageChoices.CPP,
            '.cc': LanguageChoices.CPP,
            '.cxx': LanguageChoices.CPP,
            '.py': LanguageChoices.PYTHON3,
        }

        created = []
        errors = []

        zf = None
        try:
            zf = ZipFile(upload, 'r')
            for name in zf.namelist():
                if not name or name.endswith('/'):
                    continue
                p = PurePosixPath(name)
                parts = p.parts
                if len(parts) < 3:
                    errors.append({'path': name, 'error': '路径结构错误，应为 考号/题目英文名/代码文件'})
                    continue

                exam_no = parts[0].strip()
                english_dir = parts[1].strip()
                filename = parts[-1]
                suffix = PurePosixPath(filename).suffix.lower()

                if not exam_no:
                    errors.append({'path': name, 'error': '考号为空'})
                    continue
                if suffix not in ext_lang:
                    errors.append({'path': name, 'error': f'不支持的代码后缀: {suffix}'})
                    continue

                if problem_map is not None:
                    if english_dir not in problem_map:
                        errors.append({'path': name, 'error': f'题目目录未在映射表中: {english_dir}'})
                        continue
                    try:
                        problem_id = int(problem_map[english_dir])
                    except Exception:
                        errors.append({'path': name, 'error': f'题目ID解析失败: {english_dir} -> {problem_map[english_dir]}'})
                        continue
                else:
                    try:
                        problem_id = int(english_dir)
                    except Exception:
                        errors.append({'path': name, 'error': f'题目目录必须是题目ID: {english_dir}'})
                        continue

                if problem_id not in allowed_problem_ids:
                    errors.append({'path': name, 'error': f'题目不属于该比赛: {problem_id}'})
                    continue

                try:
                    problem = Problem.objects.get(id=problem_id)
                except Problem.DoesNotExist:
                    errors.append({'path': name, 'error': f'题目不存在: {problem_id}'})
                    continue

                try:
                    if student_match == 'student_id':
                        user = User.objects.get(student_id=exam_no)
                    else:
                        user = User.objects.get(username=exam_no)
                except User.DoesNotExist:
                    errors.append({'path': name, 'error': f'找不到学生: {exam_no} (match={student_match})'})
                    continue

                if not contest.users.filter(id=user.id).exists():
                    contest.users.add(user)

                try:
                    code_bytes = zf.read(name)
                except Exception:
                    errors.append({'path': name, 'error': '读取压缩包文件失败'})
                    continue

                source = _decode_code(code_bytes)
                lang = ext_lang[suffix]

                has_freopen = _has_freopen(source)
                if freopen_policy == 'require' and not has_freopen:
                    submission = Submission.objects.create(
                        user=user,
                        problem=problem,
                        source=source,
                        language=lang,
                        status=StatusChoices.RUNTIME_ERROR,
                        score=0,
                        log='Missing freopen() while contest requires freopen',
                    )
                    Problem.objects.filter(id=problem.id).update(submission_count=F('submission_count') + 1)
                    created.append({
                        'path': name,
                        'student': exam_no,
                        'user_id': user.id,
                        'problem_id': problem.id,
                        'submission_id': submission.id,
                    })
                    continue

                if freopen_policy == 'forbid' and has_freopen:
                    submission = Submission.objects.create(
                        user=user,
                        problem=problem,
                        source=source,
                        language=lang,
                        status=StatusChoices.RUNTIME_ERROR,
                        score=0,
                        log='Found freopen() while contest forbids freopen',
                    )
                    Problem.objects.filter(id=problem.id).update(submission_count=F('submission_count') + 1)
                    created.append({
                        'path': name,
                        'student': exam_no,
                        'user_id': user.id,
                        'problem_id': problem.id,
                        'submission_id': submission.id,
                    })
                    continue

                if has_freopen and freopen_policy in ['ignore', 'require']:
                    source = _strip_freopen(source)

                submission = Submission.objects.create(
                    user=user,
                    problem=problem,
                    source=source,
                    language=lang,
                )
                Problem.objects.filter(id=problem.id).update(submission_count=F('submission_count') + 1)

                judge.delay(
                    submission.id,
                    submission.problem.test_case.test_case_id,
                    submission.problem.test_case.spj_id if submission.problem.test_case.use_spj else None,
                    submission.problem.test_case.test_case_config,
                    submission.problem.test_case.subcheck_config if submission.problem.test_case.use_subcheck else None,
                    submission.language,
                    submission.source,
                    {
                        'max_cpu_time': submission.problem.time_limit,
                        'max_memory': submission.problem.memory_limit * 1024 * 1024,
                    },
                )

                created.append({
                    'path': name,
                    'student': exam_no,
                    'user_id': user.id,
                    'problem_id': problem.id,
                    'submission_id': submission.id,
                })
        finally:
            if zf is not None:
                try:
                    zf.close()
                except Exception:
                    pass

        return Response({'created': created, 'errors': errors})
