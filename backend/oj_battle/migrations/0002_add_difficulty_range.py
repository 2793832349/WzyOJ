from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oj_battle', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='battleroom',
            name='difficulty_min',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='battleroom',
            name='difficulty_max',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
