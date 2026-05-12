#!/bin/bash

# ==========================================
#    INICIANDO SISTEMA HELADERIA URBAN (RPi)
# ==========================================

echo "=========================================="
echo "   INICIANDO SISTEMA HELADERIA URBAN"
echo "=========================================="

# [1/5] Verificando Entorno...
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "[1/5] Entorno virtual 'venv' activado."
elif [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
    echo "[1/5] Entorno virtual '.venv' activado."
else
    echo "⚠️  ADVERTENCIA: No se encontró entorno virtual. Usando Python del sistema."
fi

# Función para limpiar procesos al salir
trap "kill 0" EXIT

echo "[2/5] Iniciando API Backend..."
python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8000 &
sleep 5

echo "[3/5] Iniciando Servidor MCP..."
python3 mcp/server.py &
sleep 3

echo "[4/5] Iniciando Orquestador de Voz..."
# En Raspberry Pi usamos python3 directamente
python3 -m mcp.voz.pipeline.pipeline_voz &
sleep 3

echo "[5/5] Iniciando Frontend Streamlit..."
streamlit run app/main.py --server.address 0.0.0.0 &
sleep 5

# Intentar abrir el navegador automáticamente (compatible con RPi y Linux)
if command -v xdg-open > /dev/null; then
    xdg-open http://localhost:8501 &
elif command -v chromium-browser > /dev/null; then
    chromium-browser http://localhost:8501 &
fi

echo "=========================================="
echo "Sistema en marcha en tu Raspberry Pi."
echo "Pulsa [Ctrl+C] para detener todos los procesos."
echo "Si la IA no responde, verifica que 'ollama serve' esté activo."
echo "=========================================="

# Mantener el script vivo para que el trap capture el Ctrl+C
wait
