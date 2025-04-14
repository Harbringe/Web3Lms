echo "Building backend..."
echo "Installing dependencies..."
pip install -r requirements.txt
echo "Making migrations..."
python manage.py makemigrations
echo "Migrating database..."
python manage.py migrate
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear
echo "Build completed."
echo "Starting backend server..."
