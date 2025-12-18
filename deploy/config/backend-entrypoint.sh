#!/bin/bash

cd /srv/server

if [ ! -s /srv/server/secret.key ]; then
    echo $(python3 -c "from django.core.management import utils;print(utils.get_random_secret_key())") >secret.key
    export DJANGO_SUPERUSER_USERNAME=$SUPERUSER_USERNAME
    export DJANGO_SUPERUSER_PASSWORD=$SUPERUSER_PASSWORD
    export DJANGO_SUPERUSER_EMAIL=$SUPERUSER_EMAIL
    python3 manage.py createsuperuser --no-input
fi

n=0
while [ $n -lt 5 ]; do
    python3 manage.py makemigrations oj_user
    python3 manage.py migrate
    python3 manage.py makemigrations oj_problem oj_submission oj_contest oj_discussion
    python3 manage.py migrate
    python3 manage.py collectstatic --noinput
    break
    n=$(($n + 1))
    echo "Failed to migrate, going to retry..."
    sleep 8s
done

exec supervisord -c /srv/supervisord.conf
