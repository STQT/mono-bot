# Вставить в Django shell (python manage.py shell).
# Для каждого промокода: 2 неуспешные попытки + 1 успешная; QR помечается использованным.

from django.db import transaction
from django.utils import timezone
from core.models import QRCode, QRCodeScanAttempt, TelegramUser

user_success, user_fail = TelegramUser.objects.order_by("id")[:2]
qrcodes = list(QRCode.objects.all())
to_create = []
to_update_qr = []
now = timezone.now()

for qr in qrcodes:
    to_create.append(QRCodeScanAttempt(qr_code=qr, user=user_fail, is_successful=False))
    to_create.append(QRCodeScanAttempt(qr_code=qr, user=user_success, is_successful=False))
    to_create.append(QRCodeScanAttempt(qr_code=qr, user=user_success, is_successful=True))
    qr.scanned_by = user_success
    qr.scanned_at = now
    qr.is_scanned = True
    to_update_qr.append(qr)

with transaction.atomic():
    QRCodeScanAttempt.objects.bulk_create(to_create)
    QRCode.objects.bulk_update(to_update_qr, ["scanned_by", "scanned_at", "is_scanned"])
    user_success.invalidate_points_cache()

print(f"Создано попыток: {len(to_create)}, обновлено QR: {len(to_update_qr)}")
