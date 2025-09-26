@echo off
REM Script Windows pour exécuter les tests du projet Cats vs Dogs Classifier

echo ========================================
echo    Tests Cats vs Dogs Classifier
echo ========================================
echo.

REM Vérifier si on est dans le bon répertoire
if not exist "src\api\main.py" (
    echo Erreur: Ce script doit être exécuté depuis la racine du projet
    echo Répertoire actuel: %CD%
    pause
    exit /b 1
)

echo Tests disponibles:
echo 1. Tests API complets
echo 2. Tests API simples
echo 3. Tests metriques
echo 4. Tests feedback UI
echo 5. Tests feedback messages
echo 6. Tests feedback base de donnees
echo 7. Tous les tests
echo 8. Diagnostic base de donnees
echo 9. Quitter
echo.

set /p choice="Choisissez une option (1-9): "

if "%choice%"=="1" (
    echo.
    echo Exécution des tests API complets...
    python -m pytest tests/test_api.py -v -s
) else if "%choice%"=="2" (
    echo.
    echo Exécution des tests API simples...
    python -m pytest tests/test_api_simple.py -v -s
) else if "%choice%"=="3" (
    echo.
    echo Exécution des tests métriques...
    python -m pytest tests/test_metrics_api.py -v -s
) else if "%choice%"=="4" (
    echo.
    echo Exécution des tests feedback UI...
    python -m pytest tests/test_feedback_ui.py -v -s
) else if "%choice%"=="5" (
    echo.
    echo Exécution des tests feedback messages...
    python -m pytest tests/test_feedback_ui_message.py -v -s
) else if "%choice%"=="6" (
    echo.
    echo Exécution des tests feedback base de donnees...
    python -m pytest tests/test_feedback_db.py -v -s
) else if "%choice%"=="7" (
    echo.
    echo Exécution de tous les tests...
    python -m pytest tests/ -v -s
) else if "%choice%"=="8" (
    echo.
    echo Diagnostic de la base de donnees...
    python scripts/check_feedback_table.py
) else if "%choice%"=="9" (
    echo.
    echo Au revoir!
    exit /b 0
) else (
    echo.
    echo Option invalide!
    pause
    goto :eof
)

echo.
echo ========================================
echo Tests termines!
echo ========================================
pause
