from dataclasses import dataclass

@dataclass
class Cliente:
    """
    Representación de la entidad Cliente (POO) con tipado estricto.
    """
    id: int
    nombre: str
    email: str
    ciudad: str
    edad: int