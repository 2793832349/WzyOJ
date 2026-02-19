from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import oj_objective.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('oj_objective', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ObjectivePaper',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=120, verbose_name='title')),
                ('description', models.TextField(blank=True, default='', verbose_name='description')),
                ('pass_score', models.IntegerField(default=60, verbose_name='pass score')),
                ('_is_hidden', models.BooleanField(default=False, verbose_name='hide')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='create time')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='update time')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_objective_papers', to=settings.AUTH_USER_MODEL, verbose_name='created by')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_objective_papers', to=settings.AUTH_USER_MODEL, verbose_name='updated by')),
            ],
            options={
                'verbose_name': 'objective paper',
                'verbose_name_plural': 'objective papers',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='ObjectivePaperSubmission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answers', models.JSONField(default=oj_objective.models.get_default_paper_answers, verbose_name='answers')),
                ('total_score', models.IntegerField(default=0, verbose_name='total score')),
                ('max_score', models.IntegerField(default=0, verbose_name='max score')),
                ('is_pass', models.BooleanField(default=False, verbose_name='is pass')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='create time')),
                ('paper', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='submissions', to='oj_objective.objectivepaper', verbose_name='paper')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='objective_paper_submissions', to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
            options={
                'verbose_name': 'objective paper submission',
                'verbose_name_plural': 'objective paper submissions',
                'ordering': ['-create_time'],
            },
        ),
        migrations.CreateModel(
            name='ObjectivePaperItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.IntegerField(default=1, verbose_name='order')),
                ('score', models.IntegerField(default=2, verbose_name='score')),
                ('paper', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='oj_objective.objectivepaper', verbose_name='paper')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='paper_items', to='oj_objective.objectivequestion', verbose_name='question')),
            ],
            options={
                'verbose_name': 'objective paper item',
                'verbose_name_plural': 'objective paper items',
                'ordering': ['order', 'id'],
            },
        ),
    ]
