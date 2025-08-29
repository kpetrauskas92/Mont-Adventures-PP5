web: python manage.py migrate --noinput && \
     if [ "$CREATE_SUPERUSER" = "true" ]; then \
         python manage.py createsuperuser --no-input || echo "Superuser already exists"; \
     fi && \
     gunicorn mont_adventures.wsgi
