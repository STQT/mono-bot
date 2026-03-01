# Generated manually - add image field to BroadcastMessage

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0037_remove_qrcodescanattempt_unique_constraint'),
    ]

    operations = [
        migrations.AddField(
            model_name='broadcastmessage',
            name='image',
            field=models.ImageField(
                blank=True,
                help_text="Ixtiyoriy. Rasm qo'shilsa, xabar caption sifatida yuboriladi. HTML formatlash va havolalar qo'llab-quvvatlanadi.",
                null=True,
                upload_to='broadcasts/',
                verbose_name='Rasm'
            ),
        ),
    ]
