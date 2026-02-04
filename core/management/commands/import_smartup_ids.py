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
        
        # Пробуем разные кодировки и определяем разделитель
        encodings = ['utf-8', 'utf-8-sig', 'cp1251', 'latin-1']
        file_encoding = None
        delimiter = ','
        
        for encoding in encodings:
            try:
                with open(csv_file_path, 'r', encoding=encoding) as f:
                    # Читаем первые строки для анализа
                    sample_lines = []
                    for i in range(10):
                        line = f.readline()
                        if not line:
                            break
                        sample_lines.append(line)
                    
                    if not sample_lines:
                        raise CommandError('Файл пуст')
                    
                    # Пробуем определить разделитель
                    sample = ''.join(sample_lines[:5])  # Используем первые 5 строк для анализа
                    
                    try:
                        sniffer = csv.Sniffer()
                        detected_delimiter = sniffer.sniff(sample).delimiter
                        # Проверяем, что разделитель действительно есть в файле
                        if detected_delimiter and detected_delimiter in sample:
                            delimiter = detected_delimiter
                    except (csv.Error, AttributeError, TypeError):
                        pass
                    
                    # Если не удалось определить автоматически, пробуем стандартные разделители
                    if delimiter == ',':
                        common_delimiters = [',', ';', '\t', '|']
                        delimiter_counts = {}
                        for delim in common_delimiters:
                            delimiter_counts[delim] = sample.count(delim)
                        
                        # Выбираем разделитель, который встречается чаще всего
                        if delimiter_counts and max(delimiter_counts.values()) > 0:
                            delimiter = max(delimiter_counts, key=delimiter_counts.get)
                    
                    file_encoding = encoding
                    break
            except UnicodeDecodeError:
                continue
            except Exception as e:
                if 'encoding' not in str(e).lower():
                    raise
        
        if not file_encoding:
            raise CommandError(f'Не удалось открыть файл с кодировками: {", ".join(encodings)}')
        
        try:
            with open(csv_file_path, 'r', encoding=file_encoding) as f:
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
