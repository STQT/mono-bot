# Generated manually on 2026-02-06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0035_historicaltelegramuser_smartup_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='giftredemption',
            name='status',
            field=models.CharField(
                choices=[
                    ('pending', "So'rov qabul qilindi"),
                    ('approved', 'Mahsulot tayyorlash bosqichida'),
                    ('sent', 'Mahsulot yetkazib berish xizmatiga topshirildi'),
                    ('completed', 'Mahsulotni qabul qilganingizni tasdiqlang'),
                    ('rejected', "So'rov bekor qilindi (administrator bilan bog'laning)"),
                    ('not_received', "Sovg'a berilmagan (foydalanuvchi olmadi)"),
                    ('cancelled_by_user', 'Foydalanuvchi tomonidan bekor qilindi'),
                ],
                default='pending',
                max_length=20,
                verbose_name='Holat'
            ),
        ),
        migrations.AlterField(
            model_name='historicalgiftredemption',
            name='status',
            field=models.CharField(
                choices=[
                    ('pending', "So'rov qabul qilindi"),
                    ('approved', 'Mahsulot tayyorlash bosqichida'),
                    ('sent', 'Mahsulot yetkazib berish xizmatiga topshirildi'),
                    ('completed', 'Mahsulotni qabul qilganingizni tasdiqlang'),
                    ('rejected', "So'rov bekor qilindi (administrator bilan bog'laning)"),
                    ('not_received', "Sovg'a berilmagan (foydalanuvchi olmadi)"),
                    ('cancelled_by_user', 'Foydalanuvchi tomonidan bekor qilindi'),
                ],
                default='pending',
                max_length=20,
                verbose_name='Holat'
            ),
        ),
    ]
