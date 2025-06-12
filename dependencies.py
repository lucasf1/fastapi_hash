from fastapi import Depends, HTTPException
from jose import jwt, JWTError
from sqlalchemy.orm import Session, sessionmaker

from main import SECRET_KEY, ALGORITHM, oauth2_schema
from models import Usuario, db


def pegar_sessao():
    try:
        Session = sessionmaker(bind=db)
        session = Session()

        yield session
    finally:
        session.close()


def verificar_token(
        token: str = Depends(oauth2_schema),
        session: Session = Depends(pegar_sessao)
) -> Usuario:
    try:
        dic_info = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id_usuario = int(dic_info.get('sub'))
    except JWTError as erro:
        raise HTTPException(
            status_code=401,
            detail='Acesso negado, verifique a data de expiração do token'
        )
    # verificar se o token é válido
    # extrair o id do usuário do token
    usuario = session.query(Usuario).filter(Usuario.id == id_usuario).first()
    if not usuario:
        raise HTTPException(
            status_code=401,
            detail='Usuário não encontrado'
        )

    return usuario
