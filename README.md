Expenses journal  
  
For start:  
sudo docker-compose up -d  
./entrypoint.sh  
for start celery and beat:  
celery -A solb_expenses_journal worker -l info  
celery -A solb_expenses_journal beat -l info