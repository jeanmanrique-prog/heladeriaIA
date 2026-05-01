# Guia de Colaboracion en Windows y Linux

Esta guia sirve para que cualquier integrante del equipo pueda:

- clonar el repositorio
- instalar el entorno de desarrollo
- levantar la aplicacion localmente
- empezar a programar sin romper la configuracion base

Aplica a:

- Windows 10 o Windows 11
- Linux basado en Debian o Ubuntu

Si alguien usa otra distribucion Linux, debe adaptar los paquetes del sistema.

## Antes de empezar

Cada compañero debe tener instalado:

- Git
- Python 3.11 o superior
- Ollama

Ademas, el repositorio ya incluye estos archivos importantes:

- `db/heladeria.db`
- `voz_es.onnx`
- `voz_es.onnx.json`

No deben borrarlos.

## Estructura importante del proyecto

- `app/main.py`: frontend principal en Streamlit
- `api/main.py`: backend en FastAPI
- `mcp/server.py`: punto de entrada correcto para el servidor MCP
- `mcp/`: logica de IA, voz, prompts y tools
- `db/database.py`: inicializacion de base de datos
- `iniciar.bat`: arranque rapido para Windows

Importante:

- No usar `python -m mcp.server`
- En este repo el comando correcto es `python mcp/server.py`
- `app/main.py.bak` es un backup, no es el archivo de arranque

## Clonar el repositorio

```bash
git clone https://github.com/jeanmanrique-prog/heladeriaIA.git
cd heladeriaIA
```

## Flujo recomendado para colaborar

Cada vez que alguien vaya a trabajar:

1. Entrar a la rama principal y traer cambios:

```bash
git checkout main
git pull origin main
```

2. Crear una rama nueva para su trabajo:

```bash
git checkout -b nombre-de-tu-rama
```

Ejemplos:

- `git checkout -b fix-chat-voz`
- `git checkout -b feat-dashboard-admin`
- `git checkout -b refactor-api-ventas`

3. Cuando termine cambios:

```bash
git add .
git commit -m "feat: descripcion corta"
git push origin nombre-de-tu-rama
```

## Windows

## Paso 1. Abrir el proyecto

Se recomienda abrir una terminal en la carpeta del repo o usar VS Code:

```powershell
cd C:\ruta\hacia\heladeriaIA
```

## Paso 2. Crear el entorno virtual

En PowerShell:

```powershell
python -m venv .venv
```

Si `python` no funciona, probar:

```powershell
py -3.11 -m venv .venv
```

## Paso 3. Activar el entorno virtual

```powershell
.\.venv\Scripts\Activate.ps1
```

Si PowerShell bloquea la activacion, ejecutar una sola vez:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Luego volver a activar:

```powershell
.\.venv\Scripts\Activate.ps1
```

## Paso 4. Instalar dependencias Python

```powershell
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

## Paso 5. Preparar Ollama

1. Instalar Ollama desde su pagina oficial.
2. Abrir Ollama o asegurarse de que el servicio este corriendo.
3. Descargar el modelo usado por el proyecto:

```powershell
ollama pull llama3.2:1b
```

4. Verificar que el modelo exista:

```powershell
ollama list
```

## Paso 6. Verificar que existe la base de datos

```powershell
dir db
```

Debe aparecer `heladeria.db`.

Si no existe, crearla con:

```powershell
python db\database.py
```

## Paso 7. Iniciar la aplicacion en Windows

### Opcion rapida

Abrir primero Ollama en una terminal:

```powershell
ollama serve
```

Luego, en otra terminal dentro del proyecto:

```powershell
.\iniciar.bat
```

Eso abre:

- API
- servidor MCP
- pipeline de voz
- Streamlit

### Opcion manual

Abrir 5 terminales en la carpeta del proyecto. En cada una ejecutar primero:

```powershell
cd C:\ruta\hacia\heladeriaIA
.\.venv\Scripts\Activate.ps1
```

Terminal 1:

```powershell
ollama serve
```

Terminal 2:

```powershell
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload
```

Terminal 3:

```powershell
python mcp/server.py
```

Terminal 4:

```powershell
python -m mcp.voz.pipeline.pipeline_voz
```

Terminal 5:

```powershell
streamlit run app/main.py
```

## Paso 8. Abrir la app

Frontend:

```text
http://localhost:8501
```

API:

```text
http://127.0.0.1:8000
```

## Linux

Estas instrucciones estan pensadas para Ubuntu o Debian.

## Paso 1. Entrar al proyecto

```bash
cd ~/heladeriaIA
```

## Paso 2. Instalar dependencias del sistema

```bash
sudo apt update
sudo apt install -y git curl ffmpeg sqlite3 python3 python3-pip python3-venv build-essential portaudio19-dev libportaudio2 libatlas-base-dev libopenblas-dev
```

## Paso 3. Crear el entorno virtual

```bash
python3 -m venv .venv
```

## Paso 4. Activar el entorno virtual

```bash
source .venv/bin/activate
```

## Paso 5. Instalar dependencias Python

```bash
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

## Paso 6. Instalar y preparar Ollama

Instalar Ollama desde su pagina oficial o con:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Descargar el modelo:

```bash
ollama pull llama3.2:1b
```

Verificar:

```bash
ollama list
```

## Paso 7. Verificar base de datos

```bash
ls db
```

Debe existir `heladeria.db`.

Si no existe:

```bash
python db/database.py
```

## Paso 8. Iniciar la aplicacion en Linux

Abrir 5 terminales dentro de la carpeta del proyecto. En cada una ejecutar primero:

```bash
cd ~/heladeriaIA
source .venv/bin/activate
```

Terminal 1:

```bash
ollama serve
```

Terminal 2:

```bash
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload
```

Terminal 3:

```bash
python mcp/server.py
```

Terminal 4:

```bash
python -m mcp.voz.pipeline.pipeline_voz
```

Terminal 5:

```bash
streamlit run app/main.py
```

## Paso 9. Abrir la app

Frontend:

```text
http://localhost:8501
```

API:

```text
http://127.0.0.1:8000
```

## Si solo van a programar una parte

No siempre hace falta levantar todo.

### Si van a tocar solo frontend

Levantar al menos:

- API
- Streamlit

### Si van a tocar chat o voz

Levantar:

- Ollama
- API
- servidor MCP
- pipeline de voz
- Streamlit

### Si van a tocar solo base de datos o endpoints

Levantar:

- API

Y probar endpoints desde navegador, Postman o `curl`.

## Errores comunes

### Error: `No module named ...`

Causa:

- no activaron el entorno virtual
- no instalaron `requirements.txt`

Solucion:

```bash
pip install -r requirements.txt
```

### Error con `mcp.server`

Causa:

- ejecutaron el comando incorrecto

Solucion:

```bash
python mcp/server.py
```

### Error con Ollama

Revisar:

- que Ollama este abierto o corriendo
- que el modelo exista

Comandos utiles:

```bash
ollama list
ollama pull llama3.2:1b
```

### Error con base de datos

Si falta la base:

```bash
python db/database.py
```

## Recomendaciones para programar en equipo

- No trabajar directamente sobre `main`
- Hacer `git pull origin main` antes de empezar
- Crear una rama por tarea
- Escribir commits cortos y claros
- Probar localmente antes de subir cambios
- Avisar al equipo si alguien modifica estructura base, rutas o dependencias

## Archivos que mas probablemente van a tocar

- frontend: `app/`
- backend: `api/`
- IA y voz: `mcp/`
- inicio del frontend: `app/main.py`
- servidor MCP: `mcp/server.py`

## Nota final

Si un compañero logra clonar, instalar el entorno, descargar el modelo de Ollama y levantar las 5 terminales, ya queda listo para ayudar a programar y probar cambios sin depender de otra maquina.
