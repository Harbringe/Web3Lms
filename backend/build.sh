echo "Installing Dependencies..."
pip install -r requirements.txt 

echo "Collecting Static Files..."
python manage.py collectstatic --no-input 

echo "Making migrations..."
python manage.py makemigrations

echo "Migrating..." 
python manage.py migrate

if [[ $CREATE_SUPERUSER ]]; 
echo "Creating superuser..."
then python manage.py createsuperuser --no-input; 
fi

echo "Build Complete!"