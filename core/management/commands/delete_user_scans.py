"""
Management команда для очистки истории сканирования QR-кодов конкретного пользователя.

Делает следующее для заданного telegram_id:
- находит TelegramUser;
- удаляет все QRCodeScanAttempt, связанные с этим пользователем;
- «отсканированные» им QRCode помечает как неотсканированные
  (scanned_by = None, is_scanned = False, scanned_at = None);
- пересчитывает баллы пользователя.

Использование:
  python manage.py delete_user_scans <telegram_id> [--dry-run]
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.models import TelegramUser, QRCode, QRCodeScanAttempt


class Command(BaseCommand):
    help = (
        "Очищает историю сканирования QR-кодов пользователя по telegram_id: "
        "удаляет QRCodeScanAttempt и сбрасывает сканы QRCode."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "telegram_id",
            type=int,
            help="Telegram ID пользователя (telegram_id из модели TelegramUser)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Показать, что будет удалено/изменено, но не вносить изменения в БД",
        )

    def handle(self, *args, **options):
        telegram_id = options["telegram_id"]
        dry_run = options["dry_run"]

        try:
            user = TelegramUser.objects.get(telegram_id=telegram_id)
        except TelegramUser.DoesNotExist:
            raise CommandError(f"Пользователь с telegram_id={telegram_id} не найден")

        self.stdout.write(self.style.MIGRATE_HEADING(f"Пользователь: id={user.id}, telegram_id={telegram_id}"))

        attempts_qs = QRCodeScanAttempt.objects.filter(user=user)
        scanned_qr_qs = QRCode.objects.filter(scanned_by=user, is_scanned=True)

        attempts_count = attempts_qs.count()
        scanned_qr_count = scanned_qr_qs.count()

        self.stdout.write(f"Найдено попыток сканирования (QRCodeScanAttempt): {attempts_count}")
        self.stdout.write(f"Найдено отсканированных QR-кодов (QRCode.scanned_by == user): {scanned_qr_count}")

        if dry_run:
            self.stdout.write(self.style.WARNING("Режим dry-run: изменения НЕ будут сохранены"))
            return

        with transaction.atomic():
            # Удаляем попытки сканирования
            deleted_attempts, _ = attempts_qs.delete()

            # Сбрасываем состояние отсканированных QR-кодов
            updated_qr = scanned_qr_qs.update(
                scanned_by=None,
                is_scanned=False,
                scanned_at=None,
            )

            # Пересчитываем баллы пользователя
            user.invalidate_points_cache()
            new_points = user.calculate_points(force=True)

        self.stdout.write(self.style.SUCCESS(f"Удалено QRCodeScanAttempt: {deleted_attempts}"))
        self.stdout.write(self.style.SUCCESS(f"Сброшено отсканированных QR-кодов: {updated_qr}"))
        self.stdout.write(self.style.SUCCESS(f"Новые баллы пользователя: {new_points}"))

