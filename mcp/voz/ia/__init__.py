"""
🧠 IA — EL ENTENDIMIENTO Y LA ACCIÓN
------------------------------------
Esta carpeta contiene la inteligencia del sistema. Aquí es donde los datos 
se convierten en decisiones de negocio.

¿CÓMO SE ORQUESTA TODO?
1. EL CEREBRO (agente.py): Es el que manda. Recibe el texto y decide si usa 
   una "Tool" (para actuar) o un "Prompt" (para hablar).
2. EL TRADUCTOR (intencion.py): Le dice al agente qué es lo que el usuario 
   quiere hacer realmente.
3. LA MEMORIA (db_heladeria.py): Le da al agente los datos reales para que 
   no tome decisiones basadas en suposiciones.

RELACIÓN CLAVE:
- Los PROMPTS le dan el "Estilo".
- Los RESOURCES le dan el "Contexto".
- Las TOOLS le dan el "Poder" de cambiar la base de datos.
"""
