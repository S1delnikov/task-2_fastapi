from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import schemas
from typing import Annotated
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import jwthandler
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta


app = FastAPI()
router = APIRouter()

app.middleware


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

pwd_context = CryptContext(schemes=['bcrypt'], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/login')

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(username: str, db: db_dependency):
    user = db.query(models.Users).filter(models.Users.username==username).first()
    if user:
        return user
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: db_dependency):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, jwthandler.SECRET_KEY, algorithms=[jwthandler.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = jwthandler.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(username=token_data.username, db=db)
    if user is None:
        raise credentials_exception
    return user


def authenticate_user(username, password: str, db: db_dependency):
    user = get_user(username, db)
    if user:
        if verify_password(password, user.password):
            return user


@router.get('/token_relevance')
async def qwerty(current_user: Annotated[schemas.UserOutSchema, Depends(get_current_user)]):
    return HTTPException(status.HTTP_200_OK, detail='Token is relevant')

@app.post('/registration')
async def create_user(data: schemas.UserRegSchema, db: db_dependency):
    new_user = models.Users(
        username = data.username,
        email = data.email,
        password = get_password_hash(data.password),
        date_of_registration = data.date_of_registration
    )
    try: 
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except:
        raise HTTPException(status_code=400, detail='This login is occupied by another person')
    return data


@app.post('/login')
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: db_dependency
) -> jwthandler.Token:
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=jwthandler.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = jwthandler.create_access_token(
        data={ "sub": user.username }, expires_delta=access_token_expires
    )
    return jwthandler.Token(access_token=access_token, token_type="bearer")


@app.get('/posts')
async def get_posts(
    db: db_dependency,
    current_user: Annotated[schemas.UserOutSchema, Depends(get_current_user)]
):
    all_posts = db.query(models.Posts).filter(models.Posts.id_user==current_user.id).all()
    return all_posts


@app.post('/create_post', response_model=schemas.PostSchema)
async def create_post(
    data: schemas.PostSchema,
    db: db_dependency,
    current_user: Annotated[schemas.UserOutSchema, Depends(get_current_user)]
):
    new_post = models.Posts(
        title = data.title,
        text = data.text,
        date_added = data.date_added,
        id_user = current_user.id
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@app.get('/post/{id}', response_model=schemas.PostSchema)
async def get_post(
    id,
    db: db_dependency,
    current_user: Annotated[schemas.UserOutSchema, Depends(get_current_user)]
):
    if not id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Id doesn't specified")
    post = db.query(models.Posts).filter(models.Posts.id==id, models.Posts.id_user==current_user.id).first()
    if not post:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Post doesn't exists")
    return post


@app.post('/delete_post/{id_post}')
async def delete_post(
    id_post,
    db: db_dependency,
    current_user: Annotated[schemas.UserOutSchema, Depends(get_current_user)]
):
    post_on_delete = db.query(models.Posts).filter(models.Posts.id==id_post, models.Posts.id_user==current_user.id).first()
    if not post_on_delete:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Post doesn't exists")
    db.delete(post_on_delete)
    db.commit()
    raise HTTPException(status.HTTP_200_OK, detail="Success")


@app.post('/update_post/{id_post}')
async def update_post(
    id_post,
    data: schemas.PostSchema,
    db: db_dependency,
    current_user: Annotated[schemas.UserOutSchema, Depends(get_current_user)]
):
    post_on_update = db.query(models.Posts).filter(models.Posts.id==id_post, models.Posts.id_user==current_user.id).first()
    if not post_on_update:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Post doesn't exists")
    post_on_update.title = data.title
    post_on_update.text = data.text
    db.commit()
    raise HTTPException(status.HTTP_200_OK, detail="Success")


@router.post('/registration')
async def create_user(data: schemas.UserRegSchema, db: db_dependency):
    new_user = models.Users(
        username = data.username,
        email = data.email,
        password = get_password_hash(data.password),
        date_of_registration = data.date_of_registration
    )
    try: 
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except:
        raise HTTPException(status_code=400, detail='This login is occupied by another person')
    return data


@router.post('/login')
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: db_dependency
) -> jwthandler.Token:
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=jwthandler.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = jwthandler.create_access_token(
        data={ "sub": user.username }, expires_delta=access_token_expires
    )
    return jwthandler.Token(access_token=access_token, token_type="bearer")


@router.get('/posts')
async def get_posts(
    db: db_dependency,
    current_user: Annotated[schemas.UserOutSchema, Depends(get_current_user)]
):
    all_posts = db.query(models.Posts).filter(models.Posts.id_user==current_user.id).all()
    return all_posts


@router.post('/create_post', response_model=schemas.PostSchema)
async def create_post(
    data: schemas.PostSchema,
    db: db_dependency,
    current_user: Annotated[schemas.UserOutSchema, Depends(get_current_user)]
):
    new_post = models.Posts(
        title = data.title,
        text = data.text,
        date_added = data.date_added,
        id_user = current_user.id
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@router.get('/post/{id}', response_model=schemas.PostSchema)
async def get_post(
    id,
    db: db_dependency,
    current_user: Annotated[schemas.UserOutSchema, Depends(get_current_user)]
):
    if not id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Id doesn't specified")
    post = db.query(models.Posts).filter(models.Posts.id==id, models.Posts.id_user==current_user.id).first()
    if not post:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Post doesn't exists")
    return post


@router.post('/delete_post/{id_post}')
async def delete_post(
    id_post,
    db: db_dependency,
    current_user: Annotated[schemas.UserOutSchema, Depends(get_current_user)]
):
    post_on_delete = db.query(models.Posts).filter(models.Posts.id==id_post, models.Posts.id_user==current_user.id).first()
    if not post_on_delete:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Post doesn't exists")
    db.delete(post_on_delete)
    db.commit()
    raise HTTPException(status.HTTP_200_OK, detail="Success")


@router.post('/update_post/{id_post}')
async def update_post(
    id_post,
    data: schemas.PostSchema,
    db: db_dependency,
    current_user: Annotated[schemas.UserOutSchema, Depends(get_current_user)]
):
    post_on_update = db.query(models.Posts).filter(models.Posts.id==id_post, models.Posts.id_user==current_user.id).first()
    if not post_on_update:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Post doesn't exists")
    post_on_update.title = data.title
    post_on_update.text = data.text
    db.commit()
    raise HTTPException(status.HTTP_200_OK, detail="Success")