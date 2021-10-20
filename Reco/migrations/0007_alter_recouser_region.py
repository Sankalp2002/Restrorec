# Generated by Django 3.2.7 on 2021-10-20 05:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Reco', '0006_auto_20211017_0405'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recouser',
            name='region',
            field=models.CharField(choices=[('North', 'North'), ('South', 'South'), ('East', 'East'), ('West', 'West'), ('North-East', 'North-East'), ('Indo-chinese', 'Indo-chinese'), ('Western', 'Western'), ('N/P', 'No Preference')], default='N/P', help_text='Select your region', max_length=32),
        ),
    ]