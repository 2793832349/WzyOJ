from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('oj_battle', '0002_add_difficulty_range'),
    ]

    operations = [
        migrations.AlterField(
            model_name='battleroom',
            name='finish_reason',
            field=models.CharField(blank=True, choices=[('first_ac', 'First AC'), ('timeout_draw', 'Timeout Draw'), ('timeout_by_wa', 'Timeout By Wrong Attempts'), ('both_gave_up', 'Both Gave Up'), ('one_gave_up', 'One Gave Up')], max_length=30, null=True),
        ),
        migrations.CreateModel(
            name='BattleSeason',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='season name')),
                ('start_time', models.DateTimeField(verbose_name='start time')),
                ('end_time', models.DateTimeField(verbose_name='end time')),
                ('is_active', models.BooleanField(default=True, verbose_name='is active')),
                ('inherit_ratio', models.FloatField(default=0.5, help_text='继承上赛季分数的比例', verbose_name='inherit ratio')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'battle season',
                'verbose_name_plural': 'battle seasons',
                'ordering': ['-start_time'],
            },
        ),
        migrations.CreateModel(
            name='BattleRating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField(default=500, verbose_name='rating')),
                ('battle_level', models.IntegerField(default=1, verbose_name='battle level')),
                ('experience', models.IntegerField(default=0, verbose_name='experience')),
                ('total_battles', models.IntegerField(default=0, verbose_name='total battles')),
                ('wins', models.IntegerField(default=0, verbose_name='wins')),
                ('losses', models.IntegerField(default=0, verbose_name='losses')),
                ('peak_rating', models.IntegerField(default=500, verbose_name='peak rating')),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('season', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ratings', to='oj_battle.battleseason')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='battle_ratings', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'battle rating',
                'verbose_name_plural': 'battle ratings',
                'ordering': ['-rating', '-peak_rating'],
                'unique_together': {('user', 'season')},
            },
        ),
        migrations.CreateModel(
            name='BattleResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_a_rating_before', models.IntegerField(default=500)),
                ('user_a_rating_change', models.IntegerField(default=0)),
                ('user_a_exp_change', models.IntegerField(default=0)),
                ('user_a_ac_time', models.DateTimeField(blank=True, null=True, verbose_name='A AC time')),
                ('user_a_gave_up', models.BooleanField(default=False)),
                ('user_b_rating_before', models.IntegerField(default=500)),
                ('user_b_rating_change', models.IntegerField(default=0)),
                ('user_b_exp_change', models.IntegerField(default=0)),
                ('user_b_ac_time', models.DateTimeField(blank=True, null=True, verbose_name='B AC time')),
                ('user_b_gave_up', models.BooleanField(default=False)),
                ('user_a_bonus_time', models.BooleanField(default=False)),
                ('user_b_bonus_time', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('room', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='result', to='oj_battle.battleroom')),
                ('season', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='results', to='oj_battle.battleseason')),
                ('user_a', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='battle_results_as_a', to=settings.AUTH_USER_MODEL)),
                ('user_b', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='battle_results_as_b', to=settings.AUTH_USER_MODEL)),
                ('winner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='battle_wins', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'battle result',
                'verbose_name_plural': 'battle results',
                'ordering': ['-created_at'],
            },
        ),
    ]
