# Generated by Django 3.2.7 on 2021-11-29 13:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Reco', '0013_recouser_recentfeature'),
    ]

    operations = [
        migrations.AddField(
            model_name='recouser',
            name='pastRatings',
            field=models.JSONField(default=list),
        ),
        migrations.AlterField(
            model_name='menuitem',
            name='numRatings',
            field=models.IntegerField(default=1),
        ),
    ]
