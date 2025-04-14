echo "Building backend..."

echo "Installing dependencies..."
pip3 install -r requirements.txt

echo "Collecting static files..."
python3 manage.py collectstatic --noinput --clear

echo "Making static directories..."
mkdir -p staticfiles_build

echo "Copying static files to build directory..."
cp -r templates/*  staticfiles_build/

echo "Making migrations..."
python3 manage.py makemigrations

echo "Migrating database..."
python3 manage.py migrate

echo "Build completed."

echo "Starting backend server..."
