pip install -r requirements.txt
py manage.py collectstatic 
py manage.py makemigrations
py manage.py migrate