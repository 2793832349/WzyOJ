#!/bin/bash

cd /srv/server

NEW_SECRET_KEY=0

if [ ! -s /srv/server/secret.key ]; then
    echo $(python3 -c "from django.core.management import utils;print(utils.get_random_secret_key())") >secret.key
    export DJANGO_SUPERUSER_USERNAME=$SUPERUSER_USERNAME
    export DJANGO_SUPERUSER_PASSWORD=$SUPERUSER_PASSWORD
    export DJANGO_SUPERUSER_EMAIL=$SUPERUSER_EMAIL
    NEW_SECRET_KEY=1
fi

n=0
while [ $n -lt 5 ]; do
    python3 manage.py migrate
    if [ "$NEW_SECRET_KEY" = "1" ]; then
        python3 manage.py createsuperuser --no-input
    fi
    python3 manage.py collectstatic --noinput
    break
    n=$(($n + 1))
    echo "Failed to migrate, going to retry..."
    sleep 8s
done

exec supervisord -c /srv/supervisord.conf
