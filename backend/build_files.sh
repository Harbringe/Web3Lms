echo "Building backend..."
echo "Installing dependencies..."
pip3 install -r requirements.txt
echo "Collecting static files..."
python3 manage.py collectstatic --noinput --clear
echo "Making build directory..."
mkdir -p staticfiles_build
echo "Making migrations..."
python3 manage.py makemigrations
echo "Migrating database..."
python3 manage.py migrate
echo "Build completed."
echo "Starting backend server..."
