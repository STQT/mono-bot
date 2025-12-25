# Generated manually on 2025-12-26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0022_add_not_received_status'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='giftredemption',
            options={
                'ordering': ['-requested_at'],
                'permissions': [
                    ('change_status_call_center', 'Call Center: Can change redemption status'),
                    ('change_status_agent', 'Agent: Can change redemption status (sent/completed only)'),
                ],
                'verbose_name': "Sovg'a olish",
                'verbose_name_plural': "Sovg'a olishlar"
            },
        ),
    ]

