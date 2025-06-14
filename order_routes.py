from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from dependencies import pegar_sessao, verificar_token
from models import Pedido, Usuario
from schemas import PedidoSchema

order_router = APIRouter(prefix='/pedidos', tags=['pedidos'], dependencies=[Depends(verificar_token)])


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


@order_router.post('/pedido/cancelar/{id_pedido}')
async def cancelar_pedido(
    id_pedido: int, 
    session: Session = Depends(pegar_sessao),
    usuario: Usuario = Depends(verificar_token)
):
    # usuario.admin = True
    # usuario.id = pedido.usuario.id

    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()
    if not pedido:
        raise HTTPException(
            status_code=404,
            detail='Pedido não encontrado'
        )
    if not usuario.admin and usuario.id != pedido.usuario:
        raise HTTPException(
            status_code=401,
            detail='Você não tem permissão para cancelar este pedido'
        )

    pedido.status = 'CANCELADO'
    session.commit()


    return{
        'mensagem': f'Pedido número: {pedido.id} cancelado com sucesso',
        'pedido': pedido
    }