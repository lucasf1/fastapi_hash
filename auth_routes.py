from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from dependencies import pegar_sessao
from main import bcrypt_context
from models import Usuario
from schemas import UsuarioSchema

auth_router = APIRouter(prefix='/auth', tags=['auth'])


@auth_router.get('/')
async def home():
    """
    Essa é a rota padrão de autenticação do nosso sistema
    """
    return {
        'mensagem': 'Você acessou a rota padrão de autenticacao',
        'autenticado': False,
    }


@auth_router.post('/criar_conta')
async def criar_conta(
    usuarioSchema: UsuarioSchema, session: Session = Depends(pegar_sessao)
):
    usuario = session.query(Usuario).filter(Usuario.email == usuarioSchema.email).first()
    if usuario:
        # Já existe um usuário com esse email
        raise HTTPException(status_code=400, detail='E-mail do usuário já cadastrado')
    else:
        senha_criptografada = bcrypt_context.hash(usuarioSchema.senha)

        # Criar um novo usuário
        novo_usuario = Usuario(usuarioSchema.nome, usuarioSchema.email, senha_criptografada,
                               usuarioSchema.ativo, usuarioSchema.admin)
        session.add(novo_usuario)
        session.commit()
        return {'mensagem': f'usuário cadastrado com sucesso - {usuarioSchema.email}'}
