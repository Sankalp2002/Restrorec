# Generated by Django 3.2.7 on 2021-11-16 16:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Reco', '0010_menuitem_link'),
    ]

    operations = [
        migrations.AddField(
            model_name='recouser',
            name='features',
            field=models.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name='recouser',
            name='negativeFeature',
            field=models.JSONField(default=list),
        ),
        migrations.AddField(
            model_name='recouser',
            name='positiveFeature',
            field=models.JSONField(default=list),
        ),
        migrations.AlterField(
            model_name='recouser',
            name='ingredient',
            field=models.CharField(default='', help_text='Enter your ingredient preferences separated by commas', max_length=128),
        ),
    ]
