@echo off
title HSRP Ops - Backend + Frontend
cd /d "%~dp0"

echo Installing root dependencies...
call npm install

echo.
echo Starting backend (port 8000) + frontend (port 8080)...
echo   Frontend: http://localhost:8080
echo   Backend:  http://localhost:8000/docs
echo.

npm run dev
