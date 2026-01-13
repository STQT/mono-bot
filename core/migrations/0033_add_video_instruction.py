# Generated manually on 2026-01-08

import django.db.models.deletion
import simple_history.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0032_add_gift_order'),
    ]

    operations = [
        migrations.CreateModel(
            name='VideoInstruction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('video_uz_latin', models.FileField(blank=True, help_text="Video fayl o'zbek tilida (lotin)", null=True, upload_to='video_instructions/', verbose_name="Video (O'zbek lotin)")),
                ('video_ru', models.FileField(blank=True, help_text='Video fayl rus tilida', null=True, upload_to='video_instructions/', verbose_name='Video (Ruscha)')),
                ('file_id_uz_latin', models.CharField(blank=True, help_text="Telegram file_id o'zbek tili uchun (avtomatik to'ldiriladi)", max_length=255, null=True, verbose_name="Telegram file_id (O'zbek)")),
                ('file_id_ru', models.CharField(blank=True, help_text='Telegram file_id rus tili uchun (avtomatik to\'ldiriladi)', max_length=255, null=True, verbose_name='Telegram file_id (Ruscha)')),
                ('is_active', models.BooleanField(default=True, verbose_name='Faol')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Yaratilgan')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Yangilangan')),
            ],
            options={
                'verbose_name': 'Video ko\'rsatma',
                'verbose_name_plural': 'Video ko\'rsatmalar',
                'ordering': ['-updated_at'],
            },
        ),
        migrations.CreateModel(
            name='HistoricalVideoInstruction',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('video_uz_latin', models.TextField(blank=True, help_text="Video fayl o'zbek tilida (lotin)", max_length=100, null=True, verbose_name="Video (O'zbek lotin)")),
                ('video_ru', models.TextField(blank=True, help_text='Video fayl rus tilida', max_length=100, null=True, verbose_name='Video (Ruscha)')),
                ('file_id_uz_latin', models.CharField(blank=True, help_text="Telegram file_id o'zbek tili uchun (avtomatik to'ldiriladi)", max_length=255, null=True, verbose_name="Telegram file_id (O'zbek)")),
                ('file_id_ru', models.CharField(blank=True, help_text='Telegram file_id rus tili uchun (avtomatik to\'ldiriladi)', max_length=255, null=True, verbose_name='Telegram file_id (Ruscha)')),
                ('is_active', models.BooleanField(default=True, verbose_name='Faol')),
                ('created_at', models.DateTimeField(blank=True, editable=False, verbose_name='Yaratilgan')),
                ('updated_at', models.DateTimeField(blank=True, editable=False, verbose_name='Yangilangan')),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='auth.user')),
            ],
            options={
                'verbose_name': 'historical Video ko\'rsatma',
                'verbose_name_plural': 'historical Video ko\'rsatmalar',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]
