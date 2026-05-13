import requests
import json
from mcp.config import API_URL
from mcp.voz.ia.db_heladeria import obtener_catalogo

class CatalogResource:
    """
    📖 CATALOG RESOURCE — EL "MENÚ" SIEMPRE VISIBLE
    ---------------------------------------------
    Este archivo define el catálogo de productos como un RECURSO de MCP en lugar de una HERRAMIENTA (Tool).

    ¿POR QUÉ ES MEJOR UN 'RESOURCE' QUE UNA 'TOOL' PARA EL CATÁLOGO?
    1. CARGA DECLARATIVA (Estar vs. Hacer): 
       - Una TOOL es una acción: La IA debe "decidir" llamarla. Si la IA se confunde o se distrae, 
         puede intentar adivinar un precio sin usar la herramienta.
       - Un RESOURCE es conocimiento: Es como ponerle el menú físicamente en la mesa a la IA. 
         No tiene que pedirlo; ya es parte de lo que "sabe" sobre el entorno en ese instante.
    
    2. REDUCCIÓN DE ALUCINACIONES:
       Al inyectar el catálogo como recurso, forzamos a que el modelo use datos reales como 
       "contexto de base". Es mucho más difícil que la IA invente un sabor o un precio si 
       tiene el bloque de texto del recurso justo delante de sus ojos.

    3. EFICIENCIA EN EL FLUJO:
       Las Tools requieren un ciclo de ida y vuelta (Model -> Tool Call -> Result -> Model).
       Los Resources pueden ser pre-cargados o consultados masivamente, permitiendo que la IA
       tenga toda la información disponible para responder en un solo paso.

    ¿POR QUÉ ES DINÁMICO?
    Aunque se llame "Recurso", no es un archivo de texto estático. Cada vez que el sistema 
    MCP pide este recurso, se ejecuta `get_catalog_text()`, el cual consulta en TIEMPO REAL:
    [API /inventario] -> Si falla -> [DB SQLite Directa].
    
    Esto garantiza que el "menú" que ve la IA siempre refleje el stock real de la heladería.

    ¿CÓMO SABE LA IA QUE DEBE USAR ESTO?
    El cliente MCP (la interfaz de chat o el servidor de voz) "inyecta" este recurso 
    automáticamente en el contexto del modelo. No es que la IA "decida" leerlo como 
    una herramienta; el sistema se lo entrega como información de base obligatoria 
    antes de cada respuesta. Es como darle una hoja con precios a un vendedor justo 
    antes de que atienda a un cliente.
    """
    @staticmethod
    def get_catalog_text() -> str:
        items = []
        # 1. Intentar via API
        try:
            r = requests.get(f"{API_URL}/inventario", timeout=2)
            r.raise_for_status()
            items = r.json().get("inventario", [])
        except Exception:
            # 2. Fallback a DB Directa si la API falla
            items = obtener_catalogo()
            
        if not items:
            return "CATÁLOGO: No hay productos disponibles en este momento."
        
        txt = "═══ CATÁLOGO REAL DE PRODUCTOS ═══\n"
        for p in items:
            stock = p.get("stock", 0)
            if stock > 0:
                txt += f"- {p['sabor']}: {p['precio_unitario']:,} pesos (Stock: {stock})\n"
        txt += "══════════════════════════════════"
        return txt.replace(",", ".")
