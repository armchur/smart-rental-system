@echo off
echo Starting Smart Rental System Engines...

start "Engine 1 - AI Recognition (Flask)" cmd /k "cd /d C:\SmartRental && venv\Scripts\activate && python app\recognition_service.py"

timeout /t 3 /nobreak >nul

start "Engine 2 - Web Server (Django)" cmd /k "cd /d C:\SmartRental && venv\Scripts\activate && python manage.py runserver"

timeout /t 2 /nobreak >nul

start http://127.0.0.1:8000/
