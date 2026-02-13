"""
Management команда для импорта пользователей Telegram из SQL бэкапа.
Использование: python manage.py import_telegram_users <sql_file> [--start-line <line>] [--end-line <line>]
"""
import os
import re
from datetime import datetime, timezone as dt_timezone
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.db import connection
from core.models import TelegramUser


class Command(BaseCommand):
    help = 'Импортирует пользователей Telegram из SQL бэкапа с логикой UPSERT (создание или обновление)'

    def add_arguments(self, parser):
        parser.add_argument(
            'sql_file',
            type=str,
            help='Путь к SQL файлу бэкапа'
        )
        parser.add_argument(
            '--start-line',
            type=int,
            default=None,
            help='Номер начальной строки для извлечения данных (по умолчанию ищет автоматически)'
        )
        parser.add_argument(
            '--end-line',
            type=int,
            default=None,
            help='Номер конечной строки для извлечения данных (по умолчанию ищет автоматически)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Показать что будет импортировано без сохранения в базу данных'
        )

    def parse_null(self, value):
        r"""Преобразует \N в None."""
        if value == '\\N' or value == '':
            return None
        return value

    def parse_bool(self, value):
        """Преобразует строку в boolean."""
        if value is None or value == '\\N':
            return None
        return value.lower() in ('t', 'true', '1', 'yes')

    def parse_int(self, value):
        """Преобразует строку в integer."""
        if value is None or value == '\\N' or value == '':
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    def parse_float(self, value):
        """Преобразует строку в float."""
        if value is None or value == '\\N' or value == '':
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    def parse_datetime(self, value):
        """Преобразует строку в timezone-aware datetime."""
        if value is None or value == '\\N' or value == '':
            return None
        try:
            # Формат: 2026-01-12 13:52:01.028087+00
            # Используем datetime.timezone.utc для создания aware datetime
            dt_str = value.replace('+00', '').strip()
            try:
                dt = datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S.%f')
            except ValueError:
                dt = datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
            # Делаем datetime timezone-aware (UTC)
            return timezone.make_aware(dt, dt_timezone.utc)
        except (ValueError, TypeError) as e:
            return None

    def find_copy_section(self, lines):
        """Находит начало и конец COPY секции для core_telegramuser."""
        start_line = None
        end_line = None
        
        for i, line in enumerate(lines, start=1):
            if 'COPY public.core_telegramuser' in line.upper() and 'FROM stdin' in line.upper():
                start_line = i + 1  # Данные начинаются со следующей строки
            elif start_line and line.strip() == '\\.':
                end_line = i - 1  # Данные заканчиваются на предыдущей строке
                break
        
        return start_line, end_line

    def parse_user_line(self, line):
        """Парсит строку данных пользователя."""
        # Разделяем по табуляции
        parts = line.rstrip('\n').split('\t')
        
        if len(parts) < 20:
            return None
        
        try:
            return {
                'id': self.parse_int(parts[0]),
                'telegram_id': self.parse_int(parts[1]),
                'username': self.parse_null(parts[2]),
                'first_name': self.parse_null(parts[3]),
                'last_name': self.parse_null(parts[4]),
                'phone_number': self.parse_null(parts[5]),
                'latitude': self.parse_float(parts[6]),
                'longitude': self.parse_float(parts[7]),
                'user_type': self.parse_null(parts[8]),
                'points': self.parse_int(parts[9]) or 0,
                'is_active': self.parse_bool(parts[10]),
                'last_message_sent_at': self.parse_datetime(parts[11]),
                'blocked_bot_at': self.parse_datetime(parts[12]),
                'created_at': self.parse_datetime(parts[13]),
                'updated_at': self.parse_datetime(parts[14]),
                'language': self.parse_null(parts[15]) or 'uz_latin',
                'privacy_accepted': self.parse_bool(parts[16]),
                'district': self.parse_null(parts[17]),
                'region': self.parse_null(parts[18]),
                'smartup_id': self.parse_int(parts[19]),
            }
        except (IndexError, ValueError) as e:
            self.stdout.write(
                self.style.WARNING(f'Ошибка парсинга строки: {line[:100]}... - {e}')
            )
            return None

    def handle(self, *args, **options):
        sql_file_path = options['sql_file']
        start_line = options.get('start_line')
        end_line = options.get('end_line')
        dry_run = options.get('dry_run', False)
        
        # Проверяем существование файла
        if not os.path.exists(sql_file_path):
            raise CommandError(f'Файл "{sql_file_path}" не найден')
        
        self.stdout.write(f'Чтение SQL файла: {sql_file_path}')
        
        # Читаем файл
        try:
            with open(sql_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
        except Exception as e:
            raise CommandError(f'Ошибка при чтении файла: {e}')
        
        # Определяем диапазон строк
        if start_line is None or end_line is None:
            auto_start, auto_end = self.find_copy_section(lines)
            if auto_start and auto_end:
                start_line = auto_start
                end_line = auto_end
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Автоматически найдена COPY секция: строки {start_line}-{end_line}'
                    )
                )
            else:
                raise CommandError(
                    'Не удалось найти COPY секцию для core_telegramuser. '
                    'Укажите --start-line и --end-line вручную.'
                )
        
        # Извлекаем данные
        data_lines = lines[start_line - 1:end_line]  # -1 потому что индексы с 0
        
        if not data_lines:
            raise CommandError(f'Не найдено данных в диапазоне строк {start_line}-{end_line}')
        
        self.stdout.write(f'Найдено строк данных: {len(data_lines)}')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('РЕЖИМ ПРОВЕРКИ (dry-run) - изменения не будут сохранены'))
        
        # Статистика
        imported_count = 0
        updated_count = 0
        skipped_count = 0
        error_count = 0
        
        # Обрабатываем каждую строку
        for line_num, line in enumerate(data_lines, start=start_line):
            if not line.strip() or line.strip().startswith('--'):
                continue
            
            user_data = self.parse_user_line(line)
            
            if not user_data:
                skipped_count += 1
                continue
            
            telegram_id = user_data.get('telegram_id')
            if not telegram_id:
                skipped_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Строка {line_num}: пропущена (нет telegram_id)')
                )
                continue
            
            try:
                # Подготавливаем данные для обновления/создания
                defaults_data = {
                    'username': user_data.get('username'),
                    'first_name': user_data.get('first_name'),
                    'last_name': user_data.get('last_name'),
                    'phone_number': user_data.get('phone_number'),
                    'latitude': user_data.get('latitude'),
                    'longitude': user_data.get('longitude'),
                    'user_type': user_data.get('user_type'),
                    'points': user_data.get('points', 0),
                    'is_active': user_data.get('is_active', True),
                    'last_message_sent_at': user_data.get('last_message_sent_at'),
                    'blocked_bot_at': user_data.get('blocked_bot_at'),
                    'language': user_data.get('language', 'uz_latin'),
                    'privacy_accepted': user_data.get('privacy_accepted', False),
                    'district': user_data.get('district'),
                    'region': user_data.get('region'),
                    'smartup_id': user_data.get('smartup_id'),
                }
                
                if dry_run:
                    # В режиме dry-run только проверяем существование
                    try:
                        existing_user = TelegramUser.objects.get(telegram_id=telegram_id)
                        created = False
                        # Проверяем нужно ли обновление
                        should_update = False
                        if user_data.get('updated_at'):
                            new_updated_at = user_data['updated_at']
                            existing_updated_at = existing_user.updated_at
                            
                            if existing_updated_at:
                                if timezone.is_naive(existing_updated_at):
                                    existing_updated_at = timezone.make_aware(existing_updated_at, dt_timezone.utc)
                                if new_updated_at and new_updated_at > existing_updated_at:
                                    should_update = True
                            else:
                                should_update = True
                        else:
                            should_update = True
                        
                        if should_update:
                            updated_count += 1
                        else:
                            skipped_count += 1
                    except TelegramUser.DoesNotExist:
                        created = True
                        imported_count += 1
                else:
                    # Проверяем существование пользователя по telegram_id
                    user_exists = TelegramUser.objects.filter(telegram_id=telegram_id).exists()
                    
                    if not user_exists:
                        # Создаем нового пользователя через прямой SQL чтобы избежать создания истории
                        # Используем INSERT напрямую в таблицу core_telegramuser
                        with connection.cursor() as cursor:
                            # Подготавливаем значения для INSERT
                            # Всегда добавляем обязательные поля и поля со значениями по умолчанию
                            fields = ['telegram_id', 'points', 'is_active', 'language', 'privacy_accepted']
                            values = [
                                telegram_id,
                                defaults_data.get('points', 0),
                                defaults_data.get('is_active', True),
                                defaults_data.get('language', 'uz_latin'),
                                defaults_data.get('privacy_accepted', False)
                            ]
                            placeholders = ['%s', '%s', '%s', '%s', '%s']
                            
                            # Добавляем опциональные поля из defaults_data (только если не None)
                            optional_fields = [
                                'username', 'first_name', 'last_name', 'phone_number',
                                'latitude', 'longitude', 'user_type',
                                'last_message_sent_at', 'blocked_bot_at',
                                'district', 'region', 'smartup_id'
                            ]
                            for field in optional_fields:
                                value = defaults_data.get(field)
                                if value is not None:
                                    fields.append(field)
                                    values.append(value)
                                    placeholders.append('%s')
                            
                            # Добавляем created_at и updated_at если они есть
                            if user_data.get('created_at'):
                                fields.append('created_at')
                                values.append(user_data['created_at'])
                                placeholders.append('%s')
                            if user_data.get('updated_at'):
                                fields.append('updated_at')
                                values.append(user_data['updated_at'])
                                placeholders.append('%s')
                            
                            # Выполняем INSERT напрямую в таблицу
                            fields_str = ', '.join(fields)
                            placeholders_str = ', '.join(placeholders)
                            sql = f"INSERT INTO core_telegramuser ({fields_str}) VALUES ({placeholders_str})"
                            cursor.execute(sql, values)
                        
                        imported_count += 1
                    else:
                        # Пользователь существует - проверяем нужно ли обновление
                        should_update = False
                        if user_data.get('updated_at'):
                            existing_user = TelegramUser.objects.get(telegram_id=telegram_id)
                            new_updated_at = user_data['updated_at']
                            existing_updated_at = existing_user.updated_at
                            
                            if existing_updated_at:
                                if timezone.is_naive(existing_updated_at):
                                    existing_updated_at = timezone.make_aware(existing_updated_at, dt_timezone.utc)
                                if new_updated_at and new_updated_at > existing_updated_at:
                                    should_update = True
                            else:
                                should_update = True
                        else:
                            should_update = True
                        
                        if should_update:
                            # Используем QuerySet.update() чтобы избежать создания истории через save()
                            # Обновляем только те поля, которые не None
                            update_fields = {}
                            for field, value in defaults_data.items():
                                if value is not None:
                                    update_fields[field] = value
                            
                            if user_data.get('updated_at'):
                                update_fields['updated_at'] = user_data['updated_at']
                            
                            if update_fields:
                                TelegramUser.objects.filter(telegram_id=telegram_id).update(**update_fields)
                            
                            updated_count += 1
                        else:
                            skipped_count += 1
                        
            except Exception as e:
                error_count += 1
                # Ограничиваем количество сообщений об ошибках
                if error_count <= 10:
                    self.stdout.write(
                        self.style.ERROR(
                            f'Строка {line_num}: Ошибка при обработке telegram_id {telegram_id}: {e}'
                        )
                    )
                elif error_count == 11:
                    self.stdout.write(
                        self.style.WARNING('... (остальные ошибки скрыты для краткости)')
                    )
        
        # Выводим статистику
        self.stdout.write('\n' + '='*60)
        self.stdout.write(
            self.style.SUCCESS(
                f'\nИмпорт завершен:\n'
                f'  Создано новых пользователей: {imported_count}\n'
                f'  Обновлено существующих: {updated_count}\n'
                f'  Пропущено: {skipped_count}\n'
                f'  Ошибок: {error_count}\n'
                f'  Всего обработано: {imported_count + updated_count + skipped_count + error_count}\n'
                f'  Всего пользователей в базе: {TelegramUser.objects.count()}'
            )
        )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('\nЭто был режим проверки (dry-run). Для реального импорта запустите без --dry-run')
            )
