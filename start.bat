@echo off
REM NTI Node - Script de inicio para Windows
REM Este script verifica Python, instala dependencias y ejecuta el Node

echo ========================================
echo NTI Node - Iniciando...
echo ========================================
echo.

REM Verificar si Python esta instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no esta instalado o no esta en PATH
    echo.
    echo Por favor instala Python 3.9 o superior desde:
    echo https://www.python.org/downloads/
    echo.
    echo Asegurate de marcar "Add Python to PATH" durante la instalacion
    pause
    exit /b 1
)

echo [OK] Python encontrado:
python --version
echo.

REM Verificar si config.yaml existe
if not exist "config.yaml" (
    echo [ADVERTENCIA] config.yaml no encontrado
    echo.
    echo Creando config.yaml con valores por defecto...
    echo gateway: > config.yaml
    echo   url: "ws://localhost:8000/ws/node" >> config.yaml
    echo   reconnect_interval: 5 >> config.yaml
    echo   max_reconnect_attempts: 0 >> config.yaml
    echo. >> config.yaml
    echo execution: >> config.yaml
    echo   timeout: 120 >> config.yaml
    echo. >> config.yaml
    echo node: >> config.yaml
    echo   hostname: null >> config.yaml
    echo.
    echo [OK] config.yaml creado
    echo.
    echo IMPORTANTE: Edita config.yaml y cambia la URL del Gateway
    echo Ejemplo: url: "ws://tu-servidor-gateway:8000/ws/node"
    echo.
    pause
)

REM Verificar si requirements.txt existe
if not exist "requirements.txt" (
    echo [ERROR] requirements.txt no encontrado
    echo.
    echo Asegurate de estar en el directorio correcto de NTI-node
    pause
    exit /b 1
)

REM Instalar dependencias
echo Instalando/actualizando dependencias...
python -m pip install --upgrade pip >nul 2>&1
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Fallo la instalacion de dependencias
    pause
    exit /b 1
)
echo [OK] Dependencias instaladas
echo.

REM Crear directorio temp si no existe
if not exist "temp" mkdir temp

echo ========================================
echo Iniciando NTI Node...
echo ========================================
echo.
echo NOTA: En el primer inicio, el Node creara un entorno virtual
echo para ejecutar scripts. Esto puede tardar 1-2 minutos.
echo.
echo Presiona Ctrl+C para detener el Node
echo.

REM Ejecutar el Node
python main.py

REM Si el script termina, pausar para ver errores
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] El Node termino con errores
    pause
)
