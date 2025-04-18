echo "Installing Dependencies..."
pip install -r requirements.txt 

echo "Collecting Static Files..."
mkdir static 
python manage.py collectstatic --no-input 

if [[ $CREATE_SUPERUSER ]]; 
echo "Creating superuser..."
then python manage.py createsuperuser --no-input; 
fi

echo "Build Complete!"