# Gelateria Urban IA

Proyecto educativo para la gestion de una heladeria con frontend en Streamlit, backend en FastAPI, base de datos SQLite y un motor de IA con chat y voz.

## Guias utiles

- [Guia de colaboracion para Windows y Linux](./GUIA_COLABORACION_WINDOWS_LINUX.md)

## Descripcion general

Gelateria Urban IA separa la aplicacion en tres capas principales:

- `app/`: interfaz visual para administrador y cliente.
- `api/`: backend FastAPI para inventario, ventas y flujo de voz.
- `mcp/`: motor IA, prompts, herramientas de negocio y pipeline de voz.
- `db/`: base de datos SQLite y script de inicializacion.
- `imagenes/`: recursos graficos de la aplicacion.

## Funcionalidades por usuario

### Administrador

- Dashboard con metricas generales de stock, alertas, ventas e ingresos.
- Consulta de inventario y alertas de reposicion.
- Registro manual de entradas de inventario.
- Consulta de ventas y movimientos.
- Chat con IA para apoyo operativo.
- Llamada con IA con transcripcion y respuesta de voz.

### Cliente

- Catalogo de productos con busqueda por sabor.
- Flujo de compra manual con carrito.
- Indicacion visual de productos agotados.
- Chat con IA para orientar la compra.
- Llamada con IA para interaccion por voz.
- Seccion "Conocenos" con contenido visual de marca.

## Tecnologias usadas

- Python 3.11 o superior
- Streamlit
- FastAPI
- Uvicorn
- SQLite
- Requests
- Pandas
- Plotly
- Ollama
- Faster-Whisper
- Piper TTS
- SoundDevice
- NumPy
- RapidFuzz
- MCP

## Requisitos del proyecto

Antes de iniciar, confirma lo siguiente:

1. El proyecto debe quedar completo en una sola carpeta, incluyendo:
   - `voz_es.onnx`
   - `voz_es.onnx.json`
   - `db/heladeria.db`
2. Todos los servicios deben correr en la misma Raspberry si mantienes las URLs locales actuales.
3. El modelo de Ollama usado por el proyecto es `llama3.2:1b`.
4. Las dependencias Python se instalan dentro de un entorno virtual con `requirements.txt`.

## Estructura recomendada en Raspberry Pi 4

Ubica el proyecto en una ruta simple, por ejemplo:

```bash
/home/pi/heladeriaIA
```

o

```bash
/home/<tu_usuario>/heladeriaIA
```

## Instalacion completa en Raspberry Pi 4 con Raspberry Pi OS

Estas instrucciones asumen:

- Raspberry Pi 4
- Raspberry Pi OS ya instalado
- Usuario con permisos `sudo`
- Conexion a internet para instalar dependencias y Ollama

### Paso 1. Actualizar el sistema

```bash
sudo apt update
sudo apt full-upgrade -y
```

### Paso 2. Instalar dependencias del sistema

```bash
sudo apt install -y git curl ffmpeg sqlite3 alsa-utils python3 python3-pip python3-venv build-essential portaudio19-dev libportaudio2 libatlas-base-dev libopenblas-dev
```

Estas dependencias cubren:

- entorno Python
- audio
- compilacion basica
- SQLite
- soporte para `sounddevice`
- soporte para librerias numericas

### Paso 3. Llevar la carpeta del proyecto a la Raspberry

#### Opcion A. Con memoria USB

1. Apaga o desmonta correctamente la memoria USB en el computador donde tienes la carpeta.
2. Copia la carpeta completa `heladeriaIA` dentro de la memoria.
3. Inserta la memoria en la Raspberry Pi.
4. Verifica si el sistema la monto automaticamente:

```bash
lsblk
```

5. Si ya aparece montada en `/media` o `/mnt`, entra a esa ruta. Si no aparece montada, montala manualmente:

```bash
sudo mkdir -p /mnt/usb
sudo mount /dev/sda1 /mnt/usb
```

6. Copia el proyecto al home del usuario:

```bash
cp -r /mnt/usb/heladeriaIA ~/heladeriaIA
```

7. Entra al proyecto:

```bash
cd ~/heladeriaIA
```

#### Opcion B. Sin memoria USB

Puedes hacerlo de cualquiera de estas formas:

##### Forma 1. Clonar desde GitHub

```bash
git clone https://github.com/jeanmanrique-prog/heladeriaIA.git
cd heladeriaIA
```

##### Forma 2. Copiar por red con `scp`

Ejecuta esto desde tu computador, no desde la Raspberry:

```bash
scp -r ./heladeriaIA <usuario_raspberry>@<ip_raspberry>:/home/<usuario_raspberry>/
```

Luego, en la Raspberry:

```bash
cd /home/<usuario_raspberry>/heladeriaIA
```

### Paso 4. Crear y activar el entorno virtual

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

## Paso 5. Instalar y preparar Ollama

Instala Ollama:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Verifica que responde:

```bash
ollama --version
```

Descarga el modelo configurado en el proyecto:

```bash
ollama pull llama3.2:1b
```

## Paso 6. Verificar archivos del proyecto

Desde la raiz del proyecto, confirma que existan estos archivos:

```bash
ls
ls db
```

Debes ver, como minimo:

- `voz_es.onnx`
- `voz_es.onnx.json`
- `requirements.txt`
- `iniciar.bat`
- carpeta `app`
- carpeta `api`
- carpeta `mcp`
- carpeta `db`

Y dentro de `db/`:

- `heladeria.db`

Si `db/heladeria.db` no existe, puedes generarla con:

```bash
python db/database.py
```

## Paso 7. Iniciar los servicios

Abre varias terminales dentro de la carpeta del proyecto. En cada terminal ejecuta primero:

```bash
cd ~/heladeriaIA
source .venv/bin/activate
```

### Terminal 1: Ollama

```bash
ollama serve
```

### Terminal 2: API FastAPI

```bash
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload
```

### Terminal 3: Servidor MCP

```bash
python mcp/server.py
```

### Terminal 4: Pipeline local de voz

```bash
python -m mcp.voz.pipeline.pipeline_voz
```

### Terminal 5: Frontend Streamlit

```bash
streamlit run app/main.py
```

## Paso 8. Abrir la aplicacion

Cuando Streamlit inicie, abre en el navegador de la Raspberry:

```text
http://localhost:8501
```

La API quedara en:

```text
http://127.0.0.1:8000
```

## Flujo de uso de la aplicacion

### Flujo del administrador

1. Entra al panel de administracion.
2. Revisa indicadores del dashboard.
3. Consulta alertas de stock.
4. Agrega inventario cuando haga falta.
5. Revisa ventas y movimientos.
6. Usa el chat o la llamada con IA para apoyo operativo.

### Flujo del cliente

1. Entra al modo cliente.
2. Explora el catalogo.
3. Busca por sabor.
4. Agrega productos al carrito.
5. Confirma la compra manual.
6. Usa chat o voz si quieres una experiencia asistida por IA.

## Como funciona internamente

### Frontend

`Streamlit` renderiza la experiencia visual para los dos roles:

- administrador
- cliente

Desde aqui se muestran:

- dashboard
- inventario
- ventas
- movimientos
- catalogo
- chat IA
- llamada IA

### Backend

`FastAPI` expone endpoints para:

- inventario
- productos
- sabores
- ventas
- movimientos
- procesamiento de voz por chunks

### Motor IA

El modulo `mcp/` concentra:

- prompts de sistema
- herramientas de inventario y ventas
- integracion con Ollama
- normalizacion de texto
- STT con Faster-Whisper
- TTS con Piper
- VAD y manejo de turnos

### Base de datos

Se usa `SQLite` para:

- sabores
- productos
- inventario
- ventas
- detalle de ventas
- movimientos de inventario

## Notas importantes para Raspberry Pi 4

- Si la Raspberry tiene pocos recursos, cierra procesos que no uses.
- La transcripcion y sintesis de voz consumen CPU.
- Si solo quieres probar inventario y compras manuales, puedes dejar para despues la optimizacion de voz.
- No uses `python -m mcp.server` para este proyecto. Ese comando entra al modulo local `mcp/server.py` y choca con la libreria externa `mcp`. El punto de entrada correcto es `python mcp/server.py`, el cual ya incluye la logica para evitar este conflicto.
- Si cambias la IP o separas servicios en varias maquinas, debes actualizar las URLs locales definidas en:
  - `mcp/config.py`
  - `app/utils/peticiones.py`
- El archivo `iniciar.bat` es para Windows. En Raspberry Pi el arranque recomendado es manual por terminales.

## Equipo

Trabajo educativo hecho por estudiantes de la Universidad del Valle.

- Jean Phierre Steven Manrique
- ______________________________
- ______________________________
- ______________________________
- ______________________________
- ______________________________

## Creditos

Hecho con mucho amor por el equipo de Gelateria Urban.

Aceptamos comentarios, sugerencias, correcciones y ayudas para seguir mejorando el proyecto.
