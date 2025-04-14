echo "Building backend..."
echo "Installing dependencies..."
pip3 install -r requirements.txt
echo "Making migrations..."
python3 manage.py makemigrations
echo "Migrating database..."
python3 manage.py migrate
echo "Collecting static files..."
python3 manage.py collectstatic --noinput --clear
echo "Build completed."
echo "Starting backend server..."
