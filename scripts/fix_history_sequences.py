"""
Исправляет sequence для всех таблиц django-simple-history (history_id).
Запуск: docker compose run --rm web python scripts/fix_history_sequences.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mona.settings')
django.setup()

from django.db import connection

# Таблицы истории (core_historical<modelname>) — все модели с HistoricalRecords() в core
HISTORY_TABLES = [
    'core_historicaltelegramuser',
    'core_historicalqrcode',
    'core_historicalgift',
    'core_historicalgiftredemption',
    'core_historicalbroadcastmessage',
    'core_historicalpromotion',
    'core_historicalprivacypolicy',
    'core_historicalqrcodegeneration',
    'core_historicaladmincontactsettings',
    'core_historicalvideoinstruction',
]

def main():
    with connection.cursor() as cur:
        for table in HISTORY_TABLES:
            try:
                cur.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables
                        WHERE table_schema = 'public' AND table_name = %s
                    )
                """, [table])
                if not cur.fetchone()[0]:
                    print(f"  [skip] {table} (table does not exist)")
                    continue
                quoted = connection.ops.quote_name(table)
                cur.execute(
                    "SELECT setval(pg_get_serial_sequence(%s, 'history_id'), "
                    "COALESCE((SELECT MAX(history_id) FROM " + quoted + "), 1))",
                    [table]
                )
                val = cur.fetchone()[0]
                print(f"  [ok] {table} -> next history_id will be > {val}")
            except Exception as e:
                print(f"  [error] {table}: {e}")
    print("Done.")

if __name__ == '__main__':
    main()
