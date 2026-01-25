from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from django.utils import timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('oj_course', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='LiveSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, default='', max_length=100)),
                ('status', models.CharField(choices=[('active', 'Active'), ('ended', 'Ended')], default='active', max_length=20)),
                ('start_time', models.DateTimeField(default=timezone.now)),
                ('end_time', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='live_sessions', to='oj_course.course')),
                ('started_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='started_live_sessions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-start_time'],
            },
        ),
        migrations.CreateModel(
            name='LiveParticipant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('teacher', 'Teacher'), ('student', 'Student')], default='student', max_length=10)),
                ('joined_at', models.DateTimeField(default=timezone.now)),
                ('left_at', models.DateTimeField(blank=True, null=True)),
                ('muted', models.BooleanField(default=False)),
                ('hand_raised', models.BooleanField(default=False)),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='participants', to='oj_live.livesession')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='live_participants', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['joined_at'],
                'unique_together': {('session', 'user')},
            },
        ),
    ]
