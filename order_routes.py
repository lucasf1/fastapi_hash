from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from dependencies import pegar_sessao, verificar_token
from models import Pedido, Usuario, ItemPedido
from schemas import PedidoSchema, ItemPedidoSchema

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


@order_router.get('/listar')
async def listar_pedidos(
    session: Session = Depends(pegar_sessao),
    usuario: Usuario = Depends(verificar_token)
):
    if not usuario.admin:
        raise HTTPException(
            status_code=401,
            detail='Você não tem permissão para fazer essa operação'
        )
    else:
        pedidos = session.query(Pedido).all()
        return {
            'pedidos': pedidos
        }


@order_router.post('/pedido/adicionar-item/{id_pedido}')
async def adicionar_item_pedido(
    id_pedido: int,
    item_pedido_schema: ItemPedidoSchema,
    session: Session = Depends(pegar_sessao),
    usuario: Usuario = Depends(verificar_token)
):
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()
    if not pedido:
        raise HTTPException(
            status_code=404,
            detail='Pedido não encontrado'
        )
    if not usuario.admin and usuario.id != pedido.usuario:
        raise HTTPException(
            status_code=401,
            detail='Você não tem permissão para fazer essa operação'
        )
    item_pedido = ItemPedido(item_pedido_schema.quantidade, item_pedido_schema.sabor,
                             item_pedido_schema.tamanho, item_pedido_schema.preco_unitario, id_pedido)
    session.add(item_pedido)
    pedido.calcular_preco()
    session.commit()
    return {
        'mensagem': 'Item criado com sucesso',
        'item_id': item_pedido.id,
        'preco_pedido': pedido.preco
    }