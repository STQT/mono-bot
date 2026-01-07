# Generated manually on 2025-12-26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0021_add_call_center_permissions'),
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
                    ('not_received', "Sovg'a berilmagan (foydalanuvchi olmadi)")
                ], 
                default='pending', 
                max_length=20, 
                verbose_name='Holat'
            ),
        ),
    ]

