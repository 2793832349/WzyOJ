# Generated manually for oj_objective
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import oj_objective.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ObjectiveQuestion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=120, verbose_name='title')),
                ('content', models.TextField(blank=True, default='', verbose_name='content')),
                ('question_type', models.CharField(choices=[('single', 'Single Choice'), ('multiple', 'Multiple Choice'), ('judge', 'True/False')], default='single', max_length=20, verbose_name='question type')),
                ('options', models.JSONField(default=oj_objective.models.get_default_options, verbose_name='options')),
                ('correct_answers', models.JSONField(default=oj_objective.models.get_default_answers, verbose_name='correct answers')),
                ('explanation', models.TextField(blank=True, default='', verbose_name='explanation')),
                ('difficulty', models.IntegerField(default=0, verbose_name='difficulty')),
                ('_is_hidden', models.BooleanField(default=False, verbose_name='hide')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='create time')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='update time')),
                ('submission_count', models.IntegerField(default=0, verbose_name='submission count')),
                ('accepted_count', models.IntegerField(default=0, verbose_name='accepted user count')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_objective_questions', to=settings.AUTH_USER_MODEL, verbose_name='created by')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_objective_questions', to=settings.AUTH_USER_MODEL, verbose_name='updated by')),
            ],
            options={
                'verbose_name': 'objective question',
                'verbose_name_plural': 'objective questions',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='ObjectiveSubmission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('selected_answers', models.JSONField(default=oj_objective.models.get_default_answers, verbose_name='selected answers')),
                ('is_correct', models.BooleanField(default=False, verbose_name='is correct')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='create time')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='submissions', to='oj_objective.objectivequestion', verbose_name='question')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='objective_submissions', to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
            options={
                'verbose_name': 'objective submission',
                'verbose_name_plural': 'objective submissions',
                'ordering': ['-create_time'],
            },
        ),
    ]
