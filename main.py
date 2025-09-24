from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import create_engine, Column, Integer, Date, Boolean, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import jwt, JWTError
import config

app = FastAPI(title="Todo-App")

# Database setup
engine = create_engine(config.SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

#  Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Database models
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True,  nullable=False)
    hashed_password = Column(String, nullable=False)

    todos = relationship("Todo", back_populates="owner")


class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="todos")


Base.metadata.create_all(bind=engine)

# Pydantic models
class UserCreate(BaseModel):
    name: str
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class TodoBase(BaseModel):
    title: str

class TodoCreate(TodoBase):
    pass

class TodoRead(BaseModel):
    id: int
    owner_id: int
    title: str

    class Config:
        from_attributes = True

class TododeleteMultiple(BaseModel):
    ids: list[int]

  
# Auth Setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_pwd(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_pwd_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)
    return encoded_jwt

def get_user_by_email(db: Session, email: str, password: str ):
    return db.query(User).filter(User.email == email).first()

def verify_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not verify credentials",
                headers={"www-Authenticate": "Bearer"}
            )
        return TokenData(email=email)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not verify credentials",
            headers={"www-Authenticate": "Bearer"}
        )
    
def get_current_user(token: str = Depends(oauth2_scheme), db:  Session = Depends(get_db)):
    token_data = verify_token(token)
    user = db.query(User).filter(User.email == token_data.email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User does not exist",
            headers={"www-Authenticate": "Bearer"}
        )
    return user


# Auth Endpoints (register_user)
@app.post("/register", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(
            status_code=404,
            detail="User already created!"
        )

    hashed_password = get_pwd_hash(user.password)
    db_user = User(
         name = user.name,
         email = user.email,
         hashed_password = hashed_password
    )   
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Auth Endpoints (login users)
@app.post("/token", response_model= Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session= Depends(get_db)):  #test 1 Test endpoint again
    user = db.query(User).filter(User.email == form_data.username).first()

    if not user or not verify_pwd(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password!",
        )
    access_token_expires = timedelta(minutes=config.TOKEN_EXPIRE)
    access_token = create_access_token(
        data={"sub":user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# API endpoints (CRUD operations)

@app.get("/")
def root():
    return {"message": "Hello world"}

@app.post("/create-todo", response_model= TodoRead)
def create_todo(todo: TodoCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_todo = Todo(**todo.dict(), owner_id= current_user.id)
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

@app.get("/get-todos", response_model=list[TodoRead])
def get_todos(db: Session = Depends(get_db), current_user: User =Depends(get_current_user)):
    return db.query(Todo).filter(Todo.owner_id == current_user.id).all()

@app.get("/get-todo/{todo_id}", response_model=TodoRead)
def get_todo(todo_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    todo = db.query(Todo).filter(Todo.id == todo_id, Todo.owner_id == current_user.id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo

@app.put("/update-todo/{todo_id}", response_model=TodoRead)
def update_todo(todo_id: int, todo: TodoCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    todo = db.query(Todo).filter(Todo.id == todo_id, Todo.owner_id == current_user.id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    todo.title = todo.title
    todo.title = todo.title
    db.commit()
    db.refresh(todo)
    return todo

@app.delete("/delete-todo/{todo_id}")
def delete_todo(todo_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    todo = db.query(Todo).filter(Todo.id == todo_id, Todo.owner_id == current_user.id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(todo)
    db.commit()
    return {"message": "Todo deleted"}

@app.delete("/delete-todos")    
def delete_multiple_todos(payload: TododeleteMultiple, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    todos = db.query(Todo).filter(Todo.owner_id == current_user.id, Todo.id.in_(payload.ids)).all()
    if not todos:
        raise HTTPException(status_code=404, detail= "No todos found")
    for t in todos:
        db.delete(t)
        db.commit()
    return{"detail": f"Deleted {len(todos)} todos"}