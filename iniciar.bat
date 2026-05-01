@echo off
setlocal enabledelayedexpansion

echo ==========================================
echo    INICIANDO SISTEMA HELADERIA URBAN
echo ==========================================

echo [1/5] Verificando Entorno...
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

echo [2/5] Iniciando API Backend...
start "API_Backend" cmd /k "python -m uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload"
timeout /t 3 /nobreak > nul

echo [3/5] Iniciando Servidor MCP...
start "Servidor_MCP" cmd /k "python servidor_mcp.py"
timeout /t 2 /nobreak > nul

echo [4/5] Iniciando Orquestador de Voz...
start "Agente_Voz" cmd /k "python -m mcp.voz.pipeline.pipeline_voz"
timeout /t 2 /nobreak > nul

echo [5/5] Iniciando Frontend Streamlit...
start "Frontend" cmd /k "streamlit run app/main.py"

echo ==========================================
echo Sistema en marcha. 
echo Si la IA no responde, asegúrate de que Ollama esté abierto.
echo ==========================================
pause
