# Generated by Django 3.2.7 on 2021-11-15 08:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Reco', '0008_alter_recouser_ingredient'),
    ]

    operations = [
        migrations.AddField(
            model_name='menuitem',
            name='numRatings',
            field=models.IntegerField(default=0),
        ),
    ]
