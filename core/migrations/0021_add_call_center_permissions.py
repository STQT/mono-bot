# Generated migration

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_remove_privacypolicy_content_fields'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='giftredemption',
            options={
                'ordering': ['-requested_at'],
                'permissions': [('change_status_call_center', 'Call Center: Can change redemption status')],
                'verbose_name': "Sovg'a olish",
                'verbose_name_plural': "Sovg'a olishlar",
            },
        ),
        migrations.AlterModelOptions(
            name='telegramuser',
            options={
                'ordering': ['region', 'district', '-created_at'],
                'permissions': [
                    ('send_region_messages', 'Can send messages to users by region'),
                    ('change_user_type_call_center', 'Call Center: Can change user type'),
                ],
                'verbose_name': 'Telegram foydalanuvchi',
                'verbose_name_plural': 'Telegram foydalanuvchilar',
            },
        ),
    ]

