from django.db.models import Case, IntegerField, Value, When
from rest_framework import serializers

from .models import Problem, TestCase, Tags, ProblemSolve, JudgeModeChoices


class SampleSerializer(serializers.Field):

    def to_representation(self, value):
        samples = [{
            'index': 1,
            **value.sample_1,
        }, {
            'index': 2,
            **value.sample_2,
        }, {
            'index': 3,
            **value.sample_3,
        }]
        return samples

    def to_internal_value(self, data):
        for i in range(3):
            if data[i].get('index') is not None:
                data[i].pop('index')
        formatted = {
            'sample_1': data[0],
            'sample_2': data[1],
            'sample_3': data[2],
        }
        return formatted


class TestCaseDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = TestCase
        fields = [
            'test_case_config', 'spj_source', 'spj_mode', 'subcheck_config',
            'use_spj', 'use_subcheck', 'allow_download'
        ]


class TestCaseUpdateSerializer(serializers.ModelSerializer):
    test_cases = serializers.FileField(allow_empty_file=True, required=False)
    spj_source = serializers.CharField(allow_blank=True)
    delete_cases = serializers.JSONField()

    class Meta:
        model = TestCase
        fields = [
            'test_cases', 'test_case_config', 'spj_source', 'spj_mode',
            'delete_cases', 'subcheck_config', 'use_spj', 'use_subcheck',
            'allow_download'
        ]


class ProblemSolved(serializers.ReadOnlyField):

    def to_internal_value(self, data):
        pass

    def to_representation(self, value):
        request = self.context.get('request')
        if not request or not getattr(request, 'user', None) or not request.user.is_authenticated:
            return False

        solved_ids = self.context.get('solved_problem_ids', None)
        instance = getattr(value, 'instance', None)
        if solved_ids is not None and instance is not None:
            try:
                return instance.id in solved_ids
            except TypeError:
                pass

        return value.filter(user=request.user).exists()


class ProblemSerializer(serializers.ModelSerializer):
    solved = ProblemSolved(source='problem_solve')

    class Meta:
        model = Problem
        fields = [
            'id', 'title', 'difficulty', 'tags', 'solved', 'is_hidden',
            'submission_count', 'accepted_count'
        ]


class ProblemBriefSerializer(serializers.ModelSerializer):

    class Meta:
        model = Problem
        fields = ['id', 'title', 'difficulty']


class ProblemSolveSerializer(serializers.ModelSerializer):
    problem = ProblemBriefSerializer(read_only=True)

    class Meta:
        model = ProblemSolve
        fields = ['problem', 'create_time']


class TagsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tags
        fields = ['id', 'name']


class TagsField(serializers.Field):

    def to_representation(self, value):
        return TagsSerializer(value, many=True).data

    def to_internal_value(self, data):
        return [Tags.objects.get(id=i) for i in data]


class AllowSubmit(serializers.ReadOnlyField):

    def to_internal_value(self, data):
        pass

    def to_representation(self, value):
        return value




def _normalize_language_template(data):
    if not isinstance(data, dict):
        return {'prepend': '', 'append': '', 'starter': ''}
    return {
        'prepend': str(data.get('prepend', '')),
        'append': str(data.get('append', '')),
        'starter': str(data.get('starter', '')),
    }


class ProblemDetailSerializer(serializers.ModelSerializer):
    samples = SampleSerializer(source='*')
    solved = ProblemSolved(source='problem_solve')
    tags = TagsField()
    allow_submit = serializers.BooleanField(read_only=True)
    hide_submissions = serializers.BooleanField(read_only=True)
    hide_discussions = serializers.BooleanField(read_only=True)
    editorial = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Problem
        exclude = ['sample_1', 'sample_2', 'sample_3']

    def get_editorial(self, obj):
        from oj_discussion.models import Discussion

        discussion = (
            Discussion.objects
            .filter(related_problem_id=obj.id)
            .select_related('author')
            .annotate(
                _admin_priority=Case(
                    When(author__username__iexact='admin', then=Value(0)),
                    default=Value(1),
                    output_field=IntegerField(),
                )
            )
            .order_by('_admin_priority', '-update_time', '-id')
            .first()
        )
        if not discussion:
            return None

        first_reply = discussion.replies.order_by('id').first()
        content = str(getattr(first_reply, 'content', '') or '').strip()
        if not content:
            return None

        return {
            'discussion_id': discussion.id,
            'title': discussion.title,
            'author': getattr(discussion.author, 'username', ''),
            'content': content,
            'update_time': discussion.update_time,
        }

    def validate_leetcode_templates(self, value):
        if value is None:
            return {
                'c': {'prepend': '', 'append': '', 'starter': ''},
                'cpp': {'prepend': '', 'append': '', 'starter': ''},
                'python3': {'prepend': '', 'append': '', 'starter': ''},
            }
        if not isinstance(value, dict):
            raise serializers.ValidationError('leetcode_templates 必须是对象。')

        normalized = {}
        for lang in ['c', 'cpp', 'python3']:
            normalized[lang] = _normalize_language_template(value.get(lang, {}))
        return normalized

    def validate(self, attrs):
        judge_mode = attrs.get('judge_mode', getattr(self.instance, 'judge_mode', JudgeModeChoices.ACM))
        templates = attrs.get('leetcode_templates', getattr(self.instance, 'leetcode_templates', {}))

        if judge_mode == JudgeModeChoices.LEETCODE:
            if not isinstance(templates, dict):
                raise serializers.ValidationError({'leetcode_templates': 'LeetCode 模式下模板不能为空。'})
        return attrs

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        problem = Problem.objects.create(**validated_data)
        problem.tags.set(tags)
        problem.save()
        TestCase.objects.create(problem=problem)
        return problem
