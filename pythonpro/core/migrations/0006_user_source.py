# Generated by Django 2.2.2 on 2019-06-24 19:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_auto_20180603_2026'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='source',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='source'),
        ),
    ]