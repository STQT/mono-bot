# Расширяем причину изменения в истории пользователя (отмена сканирований и др.)

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0045_historicalqrcode_reason_textfield'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicaltelegramuser',
            name='history_change_reason',
            field=models.TextField(blank=True, null=True),
        ),
    ]
