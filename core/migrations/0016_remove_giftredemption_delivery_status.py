# Generated manually

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_remove_privacypolicy_content_uz_cyrillic_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='giftredemption',
            name='delivery_status',
        ),
    ]

