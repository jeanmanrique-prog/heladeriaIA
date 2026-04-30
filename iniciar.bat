@echo off
setlocal enabledelayedexpansion

echo ==========================================
echo    INICIANDO SISTEMA HELADERIA
echo ==========================================

echo [1/5] Activando entorno virtual...
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
) else (
    echo [ADVERTENCIA] No se encontro entorno virtual (venv o .venv)
    echo Asegurate de tener instaladas las dependencias globalmente.
)

echo [2/5] Iniciando API (FastAPI)...
start "API Backend" cmd /c "python -m uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload"
timeout /t 3 /nobreak > nul

echo [3/5] Iniciando Servidor MCP...
start "Servidor MCP" cmd /c "python servidor_mcp.py"
timeout /t 2 /nobreak > nul

echo [4/5] Iniciando Agente IA (Local)...
start "Agente IA" cmd /c "python -m mcp.voz.pipeline.pipeline_voz"
timeout /t 2 /nobreak > nul

echo [5/5] Iniciando Streamlit (Frontend)...
start "Streamlit Frontend" cmd /c "streamlit run app/main.py"

echo ==========================================
echo Sistema iniciado correctamente.
echo API: http://127.0.0.1:8000
echo Streamlit abrira en tu navegador predeterminado.
echo ==========================================
pause
