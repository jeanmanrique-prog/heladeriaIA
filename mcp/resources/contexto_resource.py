from api.ia.estado import GestorEstado

class ContextoResource:
    """
    🧠 CONTEXT RESOURCE — LA MEMORIA DE TRABAJO DE LA IA
    --------------------------------------------------
    ¿QUÉ ES UN 'RESOURCE' EN MCP?
    Un recurso es una fuente de información pasiva que la IA utiliza para entender su 
    entorno. A diferencia de otros componentes, un recurso no realiza acciones, sino 
    que proporciona "datos vivos" que sirven como base de conocimiento para el modelo.

    ¿POR QUÉ EL CONTEXTO ES UN RECURSO?
    El contexto es el "Estado del Mundo" en un momento dado. Tratamos el contexto como 
    un recurso porque es la información fundamental que ancla la conversación a la 
    realidad. Proporciona a la IA una visión clara de lo que ya ha ocurrido en la 
    transacción actual.

    ¿PARA QUÉ SIRVE ESTE ARCHIVO EN LA APP?
    Este archivo es el puente entre el 'GestorEstado' (donde guardamos los datos en la 
    base de datos/memoria) y el razonamiento de la IA. Su propósito es:
    1. Garantizar la consistencia: Que lo que la IA diga coincida con lo que el sistema tiene guardado.
    2. Evitar redundancias: Que la IA no vuelva a preguntar algo que el cliente ya respondió.
    3. Guía de flujo: Indica a la IA si faltan datos (como el precio o el método de pago).

    EJEMPLO EN UNA LLAMADA CON IA:
    ------------------------------
    Escenario: Un cliente está pidiendo un helado pero se distrae hablando de otra cosa.
    
    1. Cliente: "Quiero uno de vainilla... ah, por cierto, ¿ustedes abren los domingos?"
    2. IA: "Sí, abrimos todos los días. Volviendo a tu pedido, veo que quieres uno de VAINILLA." 
       <-- Aquí la IA usó el CONTEXTO para no olvidar el sabor mientras respondía la duda.
    
    4. IA (Consulta este Recurso): "El de vainilla cuesta 4.500 pesos." 
       <-- Sin este recurso, la IA podría preguntar "¿Qué sabor querías?" o inventar un precio.

    ¿CÓMO SABE LA IA QUE DEBE USAR ESTO?
    El servidor MCP está configurado para "suscribir" al modelo a estos recursos. 
    Cada vez que el usuario envía un mensaje, el sistema refresca el texto del recurso 
    y lo coloca en una sección especial del prompt (usualmente llamada "Contexto de Usuario" 
    o "Documentos de Referencia"). La IA está entrenada para dar prioridad a la 
    información que aparece en estas secciones sobre su conocimiento general, lo que 
    garantiza que siempre hable basándose en el estado real del pedido.
    """
    @staticmethod
    def get_context_text(session_id: str) -> str:
        estado = GestorEstado.obtener_estado(session_id)
        producto = estado.get("producto")
        pago = estado.get("pago")
        precio = estado.get("precio")
        
        if not producto and not pago:
            return ""

        txt = "\n═══ CONTEXTO DE LA VENTA ACTUAL ═══\n"
        if producto:
            txt += f"PRODUCTO: {producto.upper()}\n"
            if precio:
                txt += f"PRECIO: {precio:,} pesos\n".replace(",", ".")
        if pago:
            txt += f"PAGO: {pago.upper()}\n"
        
        # Lógica de sugerencia de acción para el backend/modelo
        if producto and pago:
            txt += "ESTADO: COMPLETO. Proceder a cerrar la venta.\n"
        elif producto:
            txt += "ESTADO: PENDIENTE PAGO. Preguntar método de pago.\n"
            
        txt += "═══════════════════════════════════\n"
        return txt
