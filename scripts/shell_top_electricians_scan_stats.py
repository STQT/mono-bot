"""
Сниппет для Django shell на продакшене: ТОП-10 электриков — верные/неверные попытки QR.

Как использовать:
  1. На сервере: python manage.py shell
  2. Скопировать и вставить весь код ниже (от from до конца блока).
"""

from core.models import TelegramUser, QRCodeScanAttempt

TOP_N = 10
SHOW_FAILED_LIST = True  # поставить False, если нужна только сводка

def mask_qr(code):
    if not code or len(code) <= 5:
        return code or "—"
    return f"{code[:2]}{'*' * (len(code) - 3)}{code[-1]}"

electricians = list(
    TelegramUser.objects.filter(user_type="electrician").order_by("-points")[:TOP_N]
)
print(f"\nТОП-{TOP_N} электриков по рейтингу. Попытки сканирования QR.\n")
for i, user in enumerate(electricians, 1):
    success = QRCodeScanAttempt.objects.filter(user=user, is_successful=True).count()
    fail = QRCodeScanAttempt.objects.filter(user=user, is_successful=False).count()
    name = user.first_name or user.username or "—"
    print(f"{i}. telegram_id={user.telegram_id} | {name} | баллы={user.points}")
    print(f"   Верных попыток: {success} | Неверных попыток: {fail}")
    if SHOW_FAILED_LIST and fail:
        for a in QRCodeScanAttempt.objects.filter(user=user, is_successful=False).select_related("qr_code").order_by("-attempted_at"):
            code_display = mask_qr(a.qr_code.code) if a.qr_code_id else "—"
            print(f"   — {a.attempted_at.strftime('%Y-%m-%d %H:%M:%S')} | QR: {code_display} (id={a.qr_code_id})")
print()
