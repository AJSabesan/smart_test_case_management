Backend

./venv/Scripts/activate
cd backend
py manage.py runserver

pip freeze > requirements.txt

pip install -r requirements.txt

frontend
cd frontend
npm run dev

