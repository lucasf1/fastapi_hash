from typing import Optional

from pydantic import BaseModel


class UsuarioSchema(BaseModel):
    nome: str
    email: str
    senha: str
    ativo: Optional[bool]
    admin: Optional[bool]

    class Config:
        from_attributes = True


class PedidoSchema(BaseModel):
    id_usuario: int

    class Config:
        from_attributes = True
