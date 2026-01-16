import uuid

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('oj_submission', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BattleRoom',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('room_type', models.CharField(choices=[('friend', 'Friend'), ('match', 'Match')], default='friend', max_length=20)),
                ('status', models.CharField(choices=[('waiting', 'Waiting'), ('running', 'Running'), ('finished', 'Finished')], default='waiting', max_length=20)),
                ('duration_seconds', models.IntegerField(default=1800)),
                ('start_time', models.DateTimeField(blank=True, null=True)),
                ('end_time', models.DateTimeField(blank=True, null=True)),
                ('finish_reason', models.CharField(blank=True, choices=[('first_ac', 'First AC'), ('timeout_draw', 'Timeout Draw'), ('timeout_by_wa', 'Timeout By Wrong Attempts')], max_length=30, null=True)),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_battle_rooms', to=settings.AUTH_USER_MODEL)),
                ('problem', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='battle_rooms', to='oj_problem.problem')),
                ('winner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='won_battle_rooms', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'battle room',
                'verbose_name_plural': 'battle rooms',
            },
        ),
        migrations.CreateModel(
            name='BattleSubmissionLink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='battle_submissions', to='oj_battle.battleroom')),
                ('submission', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='battle_link', to='oj_submission.submission')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='battle_submissions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'battle submission link',
                'verbose_name_plural': 'battle submission links',
            },
        ),
        migrations.CreateModel(
            name='BattleParticipant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('side', models.CharField(choices=[('A', 'A'), ('B', 'B')], max_length=1)),
                ('joined_at', models.DateTimeField(auto_now_add=True)),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='participants', to='oj_battle.battleroom')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='battle_participations', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'battle participant',
                'verbose_name_plural': 'battle participants',
                'unique_together': {('room', 'user'), ('room', 'side')},
            },
        ),
    ]
