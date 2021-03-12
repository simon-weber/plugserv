#!/usr/bin/env bash

set -e

db_path=$(echo "from django.conf import settings
print(settings.DATABASES['default']['NAME'])" \
  | python manage.py shell)
db_name=$(basename "${db_path}")
s3_path="plugserv/$(date +'%Y-%m-%d_%X')_${db_name}"

s3cmd --bucket-location=fr-par --host=https://s3.fr-par.scw.cloud --host-bucket=https://s3.fr-par.scw.cloud \
  put "${db_path}" "s3://simoncodes-sqlite/${s3_path}"
