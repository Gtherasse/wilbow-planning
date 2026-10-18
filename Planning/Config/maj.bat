@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Mise a jour des plannings WILBOW...
git pull --ff-only
if errorlevel 1 (
  echo.
  echo *** La mise a jour a echoue. Previens Claude avec le message ci-dessus. ***
  rem Avec le parametre "auto", on ne bloque jamais sur une pause : la tache
  rem planifiee tourne sans personne devant l ecran.
  if /i not "%~1"=="auto" pause
  exit /b 1
)
echo.
echo Plannings a jour.
if /i not "%~1"=="auto" timeout /t 3 >nul
