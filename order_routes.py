from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from dependencies import pegar_sessao
from models import Pedido
from schemas import PedidoSchema

order_router = APIRouter(prefix='/pedidos', tags=['pedidos'])


@order_router.get('/')
async def pedidos():
    """
    Essa é a rota padrão de pedidos do nosso sistema.
    Todas as rotas dos pedidos precisam de autenticação.
    """
    return {'mensagem': 'Você acessou a rota de pedidos'}


@order_router.post('/pedido')
async def criar_pedido(
    pedido_schema: PedidoSchema,
    session: Session = Depends(pegar_sessao)
):
    """
    Essa rota cria um novo pedido.
    """
    novo_pedido = Pedido(usuario=pedido_schema.id_usuario)
    session.add(novo_pedido)
    session.commit()
    session.refresh(novo_pedido)

    return {
        'mensagem':
            f'Pedido criado com sucesso. ID do pedido: {novo_pedido.id}'
    }
