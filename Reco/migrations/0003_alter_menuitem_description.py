# Generated by Django 3.2.7 on 2021-10-16 20:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Reco', '0002_auto_20211017_0155'),
    ]

    operations = [
        migrations.AlterField(
            model_name='menuitem',
            name='description',
            field=models.CharField(max_length=256),
        ),
    ]