from django.db import transaction
from rest_framework import serializers

from .models import (
    ObjectivePaper,
    ObjectivePaperItem,
    ObjectivePaperSubmission,
    ObjectiveQuestion,
    ObjectiveQuestionTypeChoices,
    ObjectiveSubmission,
)


def normalize_answer_value(value):
    return str(value).strip().upper()


def normalize_options(options):
    normalized = []
    if not isinstance(options, list):
        return normalized
    for idx, item in enumerate(options):
        if not isinstance(item, dict):
            continue
        key = normalize_answer_value(item.get('key') or chr(ord('A') + idx))
        text = str(item.get('text', '')).strip()
        if not key:
            continue
        normalized.append({'key': key, 'text': text})
    return normalized


def normalize_answers(answers):
    if answers is None:
        return []
    if not isinstance(answers, list):
        answers = [answers]
    res = []
    seen = set()
    for ans in answers:
        val = normalize_answer_value(ans)
        if not val or val in seen:
            continue
        seen.add(val)
        res.append(val)
    return res


def build_question_title(title, content, order=None):
    raw_title = str(title or '').strip()
    if raw_title:
        return raw_title[:120]

    plain = str(content or '')
    plain = plain.replace('\r', ' ').replace('\n', ' ').strip()
    if plain:
        return plain[:120]

    if order is not None:
        return f'第{order}题'
    return '未命名题目'


def validate_question_payload(payload):
    q_type = payload.get('question_type', ObjectiveQuestionTypeChoices.SINGLE)
    options = payload.get('options', [])
    answers = payload.get('correct_answers', [])

    if q_type == ObjectiveQuestionTypeChoices.JUDGE:
        normalized_options = [
            {'key': 'T', 'text': '正确'},
            {'key': 'F', 'text': '错误'},
        ]
        normalized_answers = normalize_answers(answers)
        if not normalized_answers:
            raise serializers.ValidationError({'correct_answers': '判断题必须设置正确答案（T 或 F）。'})
        if len(normalized_answers) != 1 or normalized_answers[0] not in {'T', 'F'}:
            raise serializers.ValidationError({'correct_answers': '判断题答案只能是 T 或 F。'})
        payload['options'] = normalized_options
        payload['correct_answers'] = normalized_answers
        return payload

    normalized_options = normalize_options(options)
    if len(normalized_options) < 2:
        raise serializers.ValidationError({'options': '选择题至少需要 2 个选项。'})

    valid_keys = {item['key'] for item in normalized_options}
    normalized_answers = normalize_answers(answers)
    if not normalized_answers:
        raise serializers.ValidationError({'correct_answers': '请至少设置一个正确答案。'})
    if any(ans not in valid_keys for ans in normalized_answers):
        raise serializers.ValidationError({'correct_answers': '正确答案必须在选项 key 中。'})

    if q_type == ObjectiveQuestionTypeChoices.SINGLE and len(normalized_answers) != 1:
        raise serializers.ValidationError({'correct_answers': '单选题只能有一个正确答案。'})

    payload['options'] = normalized_options
    payload['correct_answers'] = normalized_answers
    return payload


class ObjectiveSolved(serializers.ReadOnlyField):
    def to_internal_value(self, data):
        pass

    def to_representation(self, value):
        request = self.context.get('request')
        if not request or not getattr(request, 'user', None) or not request.user.is_authenticated:
            return False
        return value.filter(user=request.user, is_correct=True).exists()


class ObjectiveQuestionListSerializer(serializers.ModelSerializer):
    solved = ObjectiveSolved(source='submissions')

    class Meta:
        model = ObjectiveQuestion
        fields = [
            'id',
            'title',
            'content',
            'question_type',
            'difficulty',
            'is_hidden',
            'submission_count',
            'accepted_count',
            'solved',
        ]


class ObjectiveQuestionDetailSerializer(serializers.ModelSerializer):
    solved = ObjectiveSolved(source='submissions')
    is_hidden = serializers.BooleanField(read_only=True)
    title = serializers.CharField(required=False, allow_blank=True, default='')

    class Meta:
        model = ObjectiveQuestion
        fields = [
            'id',
            'title',
            'content',
            'question_type',
            'options',
            'correct_answers',
            'explanation',
            'difficulty',
            '_is_hidden',
            'is_hidden',
            'submission_count',
            'accepted_count',
            'solved',
            'create_time',
            'update_time',
            'created_by',
            'updated_by',
        ]
        read_only_fields = [
            'id',
            'is_hidden',
            'submission_count',
            'accepted_count',
            'solved',
            'create_time',
            'update_time',
            'created_by',
            'updated_by',
        ]

    def validate(self, attrs):
        base = {
            'question_type': attrs.get('question_type', getattr(self.instance, 'question_type', ObjectiveQuestionTypeChoices.SINGLE)),
            'options': attrs.get('options', getattr(self.instance, 'options', [])),
            'correct_answers': attrs.get('correct_answers', getattr(self.instance, 'correct_answers', [])),
        }
        base = validate_question_payload(base)
        attrs['options'] = base['options']
        attrs['correct_answers'] = base['correct_answers']

        raw_title = attrs.get('title', getattr(self.instance, 'title', ''))
        raw_content = attrs.get('content', getattr(self.instance, 'content', ''))
        attrs['title'] = build_question_title(raw_title, raw_content)
        return attrs

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if not self.context.get('show_answer', False):
            data.pop('correct_answers', None)
        return data


class ObjectiveSubmitSerializer(serializers.Serializer):
    answers = serializers.ListField(child=serializers.CharField(), allow_empty=False)

    def validate_answers(self, value):
        answers = normalize_answers(value)
        if not answers:
            raise serializers.ValidationError('请至少选择一个答案。')
        return answers


class ObjectiveSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ObjectiveSubmission
        fields = ['id', 'question', 'user', 'selected_answers', 'is_correct', 'create_time']
        read_only_fields = fields


class ObjectivePaperItemWriteSerializer(serializers.Serializer):
    question_id = serializers.IntegerField(min_value=1)
    order = serializers.IntegerField(default=1)
    score = serializers.IntegerField(default=2, min_value=1)


class ObjectiveQuestionMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = ObjectiveQuestion
        fields = ['id', 'title', 'content', 'question_type', 'options', 'explanation', 'difficulty', 'correct_answers']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if not self.context.get('show_answer', False):
            data.pop('correct_answers', None)
        return data


class ObjectivePaperItemReadSerializer(serializers.ModelSerializer):
    question = ObjectiveQuestionMiniSerializer(read_only=True)

    class Meta:
        model = ObjectivePaperItem
        fields = ['id', 'order', 'score', 'question']


class ObjectivePaperListSerializer(serializers.ModelSerializer):
    question_count = serializers.IntegerField(read_only=True)
    total_score = serializers.IntegerField(read_only=True)

    class Meta:
        model = ObjectivePaper
        fields = ['id', 'title', 'pass_score', 'is_hidden', 'question_count', 'total_score', 'create_time', 'update_time']


class ObjectivePaperDetailSerializer(serializers.ModelSerializer):
    items = ObjectivePaperItemReadSerializer(many=True, read_only=True)
    write_items = ObjectivePaperItemWriteSerializer(many=True, write_only=True, required=False)
    total_score = serializers.SerializerMethodField()
    question_count = serializers.SerializerMethodField()
    is_hidden = serializers.BooleanField(read_only=True)

    class Meta:
        model = ObjectivePaper
        fields = [
            'id',
            'title',
            'description',
            'pass_score',
            '_is_hidden',
            'is_hidden',
            'question_count',
            'total_score',
            'items',
            'write_items',
            'create_time',
            'update_time',
        ]

    def get_total_score(self, obj):
        return sum(i.score for i in obj.items.all())

    def get_question_count(self, obj):
        return obj.items.count()

    def to_representation(self, instance):
        self.fields['items'].context.update(self.context)
        return super().to_representation(instance)

    def validate_write_items(self, value):
        if not value:
            raise serializers.ValidationError('套卷至少需要一道题目。')
        qids = [i['question_id'] for i in value]
        exists = set(ObjectiveQuestion.objects.filter(id__in=qids).values_list('id', flat=True))
        not_found = [str(i) for i in qids if i not in exists]
        if not_found:
            raise serializers.ValidationError(f"题目不存在：{', '.join(not_found)}")
        return value

    @transaction.atomic
    def create(self, validated_data):
        items = validated_data.pop('write_items', [])
        user = self.context['request'].user
        paper = ObjectivePaper.objects.create(created_by=user, updated_by=user, **validated_data)
        for idx, row in enumerate(items):
            ObjectivePaperItem.objects.create(
                paper=paper,
                question_id=row['question_id'],
                order=row.get('order', idx + 1),
                score=row.get('score', 2),
            )
        return paper

    @transaction.atomic
    def update(self, instance, validated_data):
        items = validated_data.pop('write_items', None)
        for k, v in validated_data.items():
            setattr(instance, k, v)
        instance.updated_by = self.context['request'].user
        instance.save()
        if items is not None:
            instance.items.all().delete()
            for idx, row in enumerate(items):
                ObjectivePaperItem.objects.create(
                    paper=instance,
                    question_id=row['question_id'],
                    order=row.get('order', idx + 1),
                    score=row.get('score', 2),
                )
        return instance


class ObjectivePaperCreateQuestionSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=120, required=False, allow_blank=True, default='')
    content = serializers.CharField(allow_blank=True, required=False, default='')
    question_type = serializers.ChoiceField(choices=ObjectiveQuestionTypeChoices.choices)
    options = serializers.ListField(required=False, default=list)
    correct_answers = serializers.ListField(required=False, default=list)
    explanation = serializers.CharField(allow_blank=True, required=False, default='')
    difficulty = serializers.IntegerField(required=False, default=0)
    score = serializers.IntegerField(required=False, default=2, min_value=1)
    order = serializers.IntegerField(required=False, default=1)

    def validate(self, attrs):
        base = {
            'question_type': attrs.get('question_type'),
            'options': attrs.get('options', []),
            'correct_answers': attrs.get('correct_answers', []),
        }
        base = validate_question_payload(base)
        attrs['options'] = base['options']
        attrs['correct_answers'] = base['correct_answers']
        return attrs


class ObjectivePaperCreateWithQuestionsSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=120)
    description = serializers.CharField(allow_blank=True, required=False, default='')
    pass_score = serializers.IntegerField(required=False, default=60)
    _is_hidden = serializers.BooleanField(required=False, default=False)
    questions = ObjectivePaperCreateQuestionSerializer(many=True)

    def validate_questions(self, value):
        if not value:
            raise serializers.ValidationError('至少添加一道题目。')
        return value

    @transaction.atomic
    def create(self, validated_data):
        user = self.context['request'].user
        questions = validated_data.pop('questions', [])
        paper = ObjectivePaper.objects.create(created_by=user, updated_by=user, **validated_data)
        for idx, row in enumerate(questions):
            score = row.pop('score', 2)
            order = row.pop('order', idx + 1)
            row['title'] = build_question_title(row.get('title'), row.get('content'), order)
            q = ObjectiveQuestion.objects.create(created_by=user, updated_by=user, **row)
            ObjectivePaperItem.objects.create(paper=paper, question=q, order=order, score=score)
        return paper


class ObjectivePaperSubmitSerializer(serializers.Serializer):
    answers = serializers.DictField(child=serializers.ListField(child=serializers.CharField()), allow_empty=False)


class ObjectivePaperSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ObjectivePaperSubmission
        fields = ['id', 'paper', 'user', 'answers', 'total_score', 'max_score', 'is_pass', 'create_time']
        read_only_fields = fields
