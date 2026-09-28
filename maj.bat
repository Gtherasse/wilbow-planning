@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Mise a jour des plannings WILBOW...
git pull --ff-only
if errorlevel 1 (
  echo.
  echo *** La mise a jour a echoue. Previens Claude avec le message ci-dessus. ***
  pause
  exit /b 1
)
echo.
echo Plannings a jour.
timeout /t 3 >nul
