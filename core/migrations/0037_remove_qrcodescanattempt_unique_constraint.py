# Generated manually on 2026-02-17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0036_add_cancelled_by_user_status'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='qrcodescanattempt',
            unique_together=set(),
        ),
    ]
