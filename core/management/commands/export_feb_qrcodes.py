"""
Management команда для экспорта сканированных промокодов за указанный месяц
в два CSV файла: для электриков и для продавцов.

Использование (из корня проекта):
    python manage.py export_feb_qrcodes              # февраль текущего года
    python manage.py export_feb_qrcodes --year 2025  # февраль 2025
    python manage.py export_feb_qrcodes --year 2025 --month 2 --output-dir exports
"""
import csv
import os
from datetime import datetime, timezone as dt_timezone

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings

from core.models import QRCode


class Command(BaseCommand):
    help = (
        "Экспортирует сканированные промокоды в CSV за указанный месяц: "
        "отдельно для электриков (code_type='electrician') и продавцов (code_type='seller')."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--year",
            type=int,
            default=None,
            help="Год (по умолчанию — текущий год).",
        )
        parser.add_argument(
            "--month",
            type=int,
            default=2,
            help="Месяц (1-12). По умолчанию — 2 (февраль).",
        )
        parser.add_argument(
            "--output-dir",
            type=str,
            default="exports",
            help="Каталог для сохранения CSV файлов (по умолчанию: ./exports).",
        )

    def handle(self, *args, **options):
        year = options.get("year")
        month = options.get("month") or 2
        output_dir = options.get("output_dir") or "exports"

        now = timezone.now()
        if year is None:
            year = now.year

        # Нормализуем месяц
        if not (1 <= int(month) <= 12):
            raise SystemExit(self.style.ERROR("month должен быть в диапазоне 1–12"))

        # Даты начала/конца интервала в таймзоне проекта (Asia/Tashkent)
        local_tz = timezone.get_current_timezone()
        start_naive = datetime(year=int(year), month=int(month), day=1)
        start = timezone.make_aware(start_naive, local_tz)
        if int(month) == 12:
            end_naive = datetime(year=int(year) + 1, month=1, day=1)
        else:
            end_naive = datetime(year=int(year), month=int(month) + 1, day=1)
        end = timezone.make_aware(end_naive, local_tz)

        os.makedirs(output_dir, exist_ok=True)

        self.stdout.write(
            self.style.NOTICE(
                f"Экспорт сканов промокодов за {year}-{month:02d} "
                f"(временная зона: {settings.TIME_ZONE}) в каталог {output_dir}"
            )
        )

        def export_for_type(code_type: str, filename: str):
            qs = (
                QRCode.objects.select_related("scanned_by")
                .filter(
                    is_scanned=True,
                    code_type=code_type,
                    scanned_at__gte=start,
                    scanned_at__lt=end,
                    scanned_by__isnull=False,
                )
                .order_by("scanned_at")
            )

            path = os.path.join(output_dir, filename)
            count = qs.count()
            if count == 0:
                self.stdout.write(
                    self.style.WARNING(
                        f"Для типа {code_type!r} нет сканов в заданном периоде. "
                        f"Файл всё равно будет создан: {path}"
                    )
                )

            with open(path, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(
                    [
                        "user_id",
                        "telegram_id",
                        "username",
                        "first_name",
                        "last_name",
                        "phone_number",
                        "user_type",
                        "region",
                        "district",
                        "qrcode_id",
                        "code",
                        "hash_code",
                        "points",
                        "scanned_at_utc",
                        "scanned_at_local",
                    ]
                )

                for qr in qs.iterator():
                    user = qr.scanned_by
                    scanned_at_utc = (
                        qr.scanned_at.astimezone(dt_timezone.utc) if qr.scanned_at else None
                    )
                    scanned_at_local = (
                        qr.scanned_at.astimezone(local_tz) if qr.scanned_at else None
                    )
                    writer.writerow(
                        [
                            user.id if user else None,
                            user.telegram_id if user else None,
                            user.username if user else None,
                            user.first_name if user else None,
                            user.last_name if user else None,
                            user.phone_number if user else None,
                            user.user_type if user else None,
                            user.region if user else None,
                            user.district if user else None,
                            qr.id,
                            qr.code,
                            qr.hash_code,
                            qr.points,
                            scanned_at_utc.isoformat() if scanned_at_utc else "",
                            scanned_at_local.isoformat() if scanned_at_local else "",
                        ]
                    )

            self.stdout.write(
                self.style.SUCCESS(
                    f"Сохранено {count} записей для типа {code_type!r} в {path}"
                )
            )

        # Электрики
        electricians_filename = f"electricians_{year}_{int(month):02d}.csv"
        export_for_type("electrician", electricians_filename)

        # Продавцы
        sellers_filename = f"sellers_{year}_{int(month):02d}.csv"
        export_for_type("seller", sellers_filename)

        self.stdout.write(self.style.SUCCESS("Экспорт завершён."))

