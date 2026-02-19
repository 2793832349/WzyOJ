from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Announcement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=120, verbose_name='title')),
                ('content', models.TextField(verbose_name='content')),
                ('is_published', models.BooleanField(default=True, verbose_name='is published')),
                ('is_pinned', models.BooleanField(default=False, verbose_name='is pinned')),
                ('start_time', models.DateTimeField(blank=True, null=True, verbose_name='start time')),
                ('end_time', models.DateTimeField(blank=True, null=True, verbose_name='end time')),
                ('order', models.IntegerField(default=0, verbose_name='order')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated at')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_announcements', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_announcements', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'announcement',
                'verbose_name_plural': 'announcements',
                'ordering': ['-is_pinned', 'order', '-id'],
            },
        ),
    ]
