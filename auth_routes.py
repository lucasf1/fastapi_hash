from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from dependencies import pegar_sessao
from main import bcrypt_context, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY
from models import Usuario
from schemas import LoginSchema, UsuarioSchema


auth_router = APIRouter(prefix='/auth', tags=['auth'])


def criar_token(id_usuario, duracao_token = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    data_expiracao = datetime.now(timezone.utc) + duracao_token
    dict_info = {"sub": id_usuario, "exp": data_expiracao}
    jwt_codificado = jwt.encode(dict_info, SECRET_KEY, ALGORITHM)

    return jwt_codificado

def verificar_token(token: str, session: Session = Depends(pegar_sessao)) -> Usuario:
    # verificar se o token é válido
    # extrair o id do usuário do token
    usuario = session.query(Usuario).filter(Usuario.id == 1).first()
    return usuario

def autenticar_usuario(email: str, senha:str, session: Session):
    usuario = session.query(Usuario).filter(Usuario.email == email).first()
    if not usuario:
        return False
    elif not bcrypt_context.verify(senha, usuario.senha):
        return False
    
    return usuario


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
        return {
            'mensagem': f'usuário cadastrado com sucesso - {usuarioSchema.email}'
        }


@auth_router.post('/login')
async def login(
    login_schema: LoginSchema,
    session: Session = Depends(pegar_sessao)
):
    """
    Essa rota faz o login do usuário.
    """
    usuario = autenticar_usuario(login_schema.email, login_schema.senha, session)
    if not usuario:
        raise HTTPException(status_code=404, detail='Usuário não encontrado ou credenciais inválidas')
    else:
        access_token = criar_token(usuario.id)
        refresh_token = criar_token(usuario.id, duracao_token=timedelta(days=7))
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'Bearer',
        }
    

@auth_router.get('/refresh')
async def use_refresh_token(token):
    # verifica o token
    usuario = verificar_token(token)

    access_token = criar_token(usuario.id)
    return {
        'access_token': access_token,
        'token_type': 'Bearer',
    }

