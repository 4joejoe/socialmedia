echo "Installing requirements..."

pip install -r requirements.txt

echo "Making migrations..."
python3 manage.py makemigrations
python3 manage.py makemigrations authapp

echo "Applying migrations..."
python3 manage.py migrate