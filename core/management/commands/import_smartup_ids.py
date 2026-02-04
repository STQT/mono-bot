"""
Менеджмент команда для импорта SmartUP ID из CSV файла.
"""
import csv
import os
from django.core.management.base import BaseCommand, CommandError
from core.models import SmartUPId


class Command(BaseCommand):
    help = 'Импортирует SmartUP ID из CSV файла'

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file',
            type=str,
            help='Путь к CSV файлу с SmartUP ID'
        )

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']
        
        # Проверяем существование файла
        if not os.path.exists(csv_file_path):
            raise CommandError(f'Файл "{csv_file_path}" не найден')
        
        # Читаем CSV файл
        imported_count = 0
        skipped_count = 0
        error_count = 0
        
        try:
            with open(csv_file_path, 'r', encoding='utf-8') as f:
                # Пробуем определить разделитель
                sample = f.read(1024)
                f.seek(0)
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.reader(f, delimiter=delimiter)
                
                # Пропускаем заголовок, если есть
                first_row = next(reader, None)
                if first_row:
                    # Проверяем, является ли первая строка заголовком (содержит нечисловые значения)
                    try:
                        int(first_row[0])
                        # Если первая строка - число, возвращаемся к началу
                        f.seek(0)
                        reader = csv.reader(f, delimiter=delimiter)
                    except ValueError:
                        # Первая строка - заголовок, продолжаем со следующей
                        pass
                
                for row_num, row in enumerate(reader, start=2):  # Начинаем с 2, так как первая строка может быть заголовком
                    if not row:
                        continue
                    
                    # Берем первое значение из строки
                    id_value_str = row[0].strip()
                    
                    if not id_value_str:
                        skipped_count += 1
                        continue
                    
                    try:
                        id_value = int(id_value_str)
                        
                        # Создаем или получаем существующий ID
                        smartup_id, created = SmartUPId.objects.get_or_create(
                            id_value=id_value,
                            defaults={'id_value': id_value}
                        )
                        
                        if created:
                            imported_count += 1
                        else:
                            skipped_count += 1
                            self.stdout.write(
                                self.style.WARNING(
                                    f'Строка {row_num}: ID {id_value} уже существует, пропущено'
                                )
                            )
                    except ValueError:
                        error_count += 1
                        self.stdout.write(
                            self.style.ERROR(
                                f'Строка {row_num}: Неверное значение "{id_value_str}", не является числом'
                            )
                        )
                    except Exception as e:
                        error_count += 1
                        self.stdout.write(
                            self.style.ERROR(
                                f'Строка {row_num}: Ошибка при обработке "{id_value_str}": {e}'
                            )
                        )
        
        except Exception as e:
            raise CommandError(f'Ошибка при чтении CSV файла: {e}')
        
        # Выводим статистику
        self.stdout.write(
            self.style.SUCCESS(
                f'\nИмпорт завершен:\n'
                f'  Импортировано: {imported_count}\n'
                f'  Пропущено (уже существует): {skipped_count}\n'
                f'  Ошибок: {error_count}\n'
                f'  Всего в базе: {SmartUPId.objects.count()}'
            )
        )
