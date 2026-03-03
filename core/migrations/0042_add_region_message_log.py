# Generated manually

from django.conf import settings
from django.db import migrations, models
from django.db.models import deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0041_remove_giftredemption_processed_at_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='RegionMessageLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('region_code', models.CharField(db_index=True, max_length=50, verbose_name='Область')),
                ('user_type_filter', models.CharField(blank=True, max_length=20, null=True, verbose_name='Фильтр типа')),
                ('language_filter', models.CharField(blank=True, max_length=15, null=True, verbose_name='Фильтр языка')),
                ('total', models.IntegerField(default=0, verbose_name='Всего получателей')),
                ('sent_count', models.IntegerField(default=0, verbose_name='Отправлено')),
                ('failed_count', models.IntegerField(default=0, verbose_name='Ошибок')),
                ('status', models.CharField(choices=[('running', 'Выполняется'), ('completed', 'Завершена'), ('failed', 'Ошибка')], db_index=True, default='running', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Запущена')),
                ('completed_at', models.DateTimeField(blank=True, null=True, verbose_name='Завершена')),
                ('error_message', models.TextField(blank=True, verbose_name='Сообщение об ошибке')),
                ('initiated_by', models.ForeignKey(blank=True, null=True, on_delete=deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Запустил')),
            ],
            options={
                'verbose_name': 'Лог рассылки по области',
                'verbose_name_plural': 'Логи рассылок по областям',
                'ordering': ['-created_at'],
            },
        ),
    ]
