#!/usr/bin/env bash

set -e

db_path=$(echo "from django.conf import settings
print(settings.DATABASES['default']['NAME'])" \
  | python manage.py shell)

echo "bytes before: $(stat --printf="%s" "${db_path}")"

python manage.py clearsessions -v 2

echo "from django.db import connection, transaction
c = connection.cursor()
c.execute('vacuum')
transaction.commit()" \
  | python manage.py shell

echo "bytes after: $(stat --printf="%s" "${db_path}")"
