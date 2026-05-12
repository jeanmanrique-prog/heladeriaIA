"""
🛠️ TOOLS — "LAS MANOS" DE LA IA
---------------------------------
Representan ACCIONES que la IA puede ejecutar para CAMBIAR el mundo real (Escribir).
A diferencia de los Resources (que son de solo lectura), las Tools permiten realizar cambios.

¿POR QUÉ SON NECESARIAS SI EXISTEN LOS RESOURCES?
1. ACCIÓN vs LECTURA: Un Resource te permite VER el catálogo, pero una Tool te permite REGISTRAR la venta. 
   No puedes "leer" una venta para que ocurra; tienes que ejecutarla (hacer que pase).

2. ESCRITURA: Las Tools son las únicas que pueden modificar la base de datos (restar stock, crear facturas).

3. VOLUMEN: No puedes meter TODO el historial de la empresa en un Resource (sería demasiada info). 
   Usas una Tool para buscar algo específico ("Busca la venta #502").

EJEMPLOS:
1. registrar_venta: Ejecuta el proceso de cobro y descarga de inventario.
2. agregar_stock: Modifica los niveles de producto.
3. consultar_ventas: Busca en el historial profundo.

Uso: Se activan cuando la IA necesita MODIFICAR datos o realizar una búsqueda profunda.
"""
