# Расширяем причину изменения в истории QR-кода для полного описания отмены сканирований

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0044_alter_historicaltelegramuser_promo_block_stage_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalqrcode',
            name='history_change_reason',
            field=models.TextField(blank=True, null=True),
        ),
    ]
