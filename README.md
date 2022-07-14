Expenses journal

For start:
sudo docker-compose up -d
./entrypoint.sh
for start celery:
celery -A solb_expenses_journal worker -l info