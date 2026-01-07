# Generated manually

from django.db import migrations, models


def migrate_name_data(apps, schema_editor):
    """Переносит данные из name в name_uz_latin."""
    Gift = apps.get_model('core', 'Gift')
    for gift in Gift.objects.all():
        if hasattr(gift, 'name') and gift.name:
            gift.name_uz_latin = gift.name
            gift.save(update_fields=['name_uz_latin'])


def reverse_migrate_name_data(apps, schema_editor):
    """Обратная миграция - переносит данные обратно."""
    Gift = apps.get_model('core', 'Gift')
    for gift in Gift.objects.all():
        if hasattr(gift, 'name_uz_latin') and gift.name_uz_latin:
            # В обратной миграции мы не можем установить name, так как поле будет удалено
            pass


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0027_remove_uz_cyrillic_from_language_choices'),
    ]

    operations = [
        # Добавляем новые поля для названия (временно nullable)
        migrations.AddField(
            model_name='gift',
            name='name_uz_latin',
            field=models.CharField(null=True, blank=True, max_length=255, verbose_name='Nomi (O\'zbek lotin)'),
        ),
        migrations.AddField(
            model_name='gift',
            name='name_ru',
            field=models.CharField(blank=True, max_length=255, verbose_name='Nomi (Ruscha)'),
        ),
        # Копируем данные из старого поля name в name_uz_latin
        migrations.RunPython(
            code=migrate_name_data,
            reverse_code=reverse_migrate_name_data,
        ),
        # Удаляем старое поле name
        migrations.RemoveField(
            model_name='gift',
            name='name',
        ),
        # Делаем name_uz_latin обязательным полем
        migrations.AlterField(
            model_name='gift',
            name='name_uz_latin',
            field=models.CharField(max_length=255, verbose_name='Nomi (O\'zbek lotin)'),
        ),
        # Обновляем ordering
        migrations.AlterModelOptions(
            name='gift',
            options={
                'ordering': ['points_cost', 'name_uz_latin'],
                'verbose_name': 'Sovg\'a',
                'verbose_name_plural': 'Sovg\'alar',
            },
        ),
    ]

