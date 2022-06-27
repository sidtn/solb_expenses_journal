source .env

ADMIN_USERNAME=${ADMIN_USERNAME}
ADMIN_EMAIL=${ADMIN_EMAIL}
ADMIN_PASSWORD=${ADMIN_PASSWORD}

./manage.py migrate
./manage.py loaddata categories.json
./manage.py loaddata currencies.json

echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser(username='$ADMIN_USERNAME', email='$ADMIN_EMAIL', password='$ADMIN_PASSWORD')" | ./manage.py shell

./manage.py runserver 0.0.0.0:8000