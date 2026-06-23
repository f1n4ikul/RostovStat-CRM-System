# Миграция: смена значения по умолчанию file_format с MP3 на MP4

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0015_additionaldocument'),
    ]

    operations = [
        migrations.AlterField(
            model_name='audiorecord',
            name='file_format',
            field=models.CharField(
                default='MP4',
                max_length=10,
                verbose_name='Формат'
            ),
        ),
    ]
