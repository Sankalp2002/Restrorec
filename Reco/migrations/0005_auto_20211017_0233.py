# Generated by Django 3.2.7 on 2021-10-16 21:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Reco', '0004_alter_menuitem_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='menuitem',
            name='category',
            field=models.CharField(max_length=128),
        ),
        migrations.AlterField(
            model_name='menuitem',
            name='description',
            field=models.CharField(max_length=512),
        ),
        migrations.AlterField(
            model_name='menuitem',
            name='name',
            field=models.CharField(max_length=256),
        ),
    ]
