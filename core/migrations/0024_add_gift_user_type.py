# Generated manually on 2025-12-26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0023_add_agent_permissions'),
    ]

    operations = [
        migrations.AddField(
            model_name='gift',
            name='user_type',
            field=models.CharField(
                blank=True,
                choices=[('electrician', 'Elektrik (E)'), ('seller', 'Sotuvchi (D)')],
                help_text="Agar bo'sh qoldirilsa, barcha foydalanuvchilar uchun ko'rsatiladi",
                max_length=20,
                null=True,
                verbose_name='Foydalanuvchi turi'
            ),
        ),
        migrations.AddIndex(
            model_name='gift',
            index=models.Index(fields=['user_type', 'is_active'], name='core_gift_user_ty_7a8b2d_idx'),
        ),
    ]

