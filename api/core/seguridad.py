import hashlib

def verificar_password(password: str) -> bool:
    """Verifica si la contraseña es correcta (admin)."""
    # En un entorno real, usar hashing y BD.
    return password == "admin"
