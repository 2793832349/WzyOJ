from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oj_course', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='is_free',
            field=models.BooleanField(default=True, verbose_name='is free'),
        ),
    ]
