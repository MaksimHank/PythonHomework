from typing import Optional
from setuptools import depends
from functools import wraps
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String

from fastapi import FastAPI, Depends, Request, Query, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import BaseModel, Field, EmailStr
import redis
import logging

r = redis.StrictRedis(host='localhost', port=6379, db=0, charset="utf-8", decode_responses=True)
logging.basicConfig(level=logging.DEBUG)

SQLALCHEMY_DATABASE_URL = "postgresql://max:pass@127.0.0.1:5432/fibdata"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class UserData(BaseModel):
    user_name: str
    password: str
    email: str
    full_name: str


class UserInDB(BaseModel):
    hashed_password: str


class FibbonachiParams(BaseModel):
    num: int
    user: Optional[UserData]


class Calculyator(BaseModel):
    number: int = Field(..., gt=0, description="Number should be more than 0")
    stepen: int = Field(2, gt=0, description="Number should be more than 0")


class CalculyatorPg(Base):
    __tablename__ = "Calc"

    id = Column(Integer, primary_key=True, index=True)
    number = Column(Integer)
    stepen = Column(Integer)
    result = Column(Integer)

    class Config:
        orm_mode = True


app = FastAPI()

Base.metadata.create_all(bind=engine)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}


@app.post('/token')
async def token(form_data: OAuth2PasswordRequestForm = Depends()):
    return {'access_token': form_data.username}


def value_in_sql(func):
    @wraps(func)
    def check_in_sql(db: SessionLocal, stepen: Calculyator):
        degree_of = db.query(CalculyatorPg).filter(
            CalculyatorPg.stepen == stepen.stepen,
            CalculyatorPg.number == stepen.number
        ).first()
        if degree_of:
            return degree_of
        else:
            result = calc(stepen.number, stepen.stepen)
            db_stepen = CalculyatorPg(number=stepen.number, stepen=stepen.stepen, result=result)
            print("DB_STEPEN: ", db_stepen)
            db.add(db_stepen)
            db.commit()
            db.refresh(db_stepen)
            print("db_stepen = ", db_stepen)
            return db_stepen
    return check_in_sql


def cal_sql(db: SessionLocal, stepen: Calculyator):
    result = calc(stepen.number, stepen.stepen)
    db.query(CalculyatorPg).set(stepen.stepen)
    return result


@app.post("/sqlRequest")
@value_in_sql
def get_user_by_stepen(stepen: Calculyator, db: Session = Depends(get_db)):
    result = db.query(CalculyatorPg).filter(CalculyatorPg.stepen == stepen.stepen).first()
    print("Result: ", result)
    return {}


def get_user_by_number(db: SessionLocal, number: int):
    return db.query(CalculyatorPg).filter(CalculyatorPg.number == number).first()


def calc(a, b):
    return a**b


@app.post("/calc")
def calculate(payload: Calculyator):
    # if payload.number > 0 and payload.stepen > 0:
    res = calc(payload.number, payload.stepen)
    return {"result": res}
    # else:
    #     raise HTTPException(status_code=400, detail="Number must be > 0")


def fibbonachi_calculate(n):
    if n in {0, 1}:
        return n
    result = fibbonachi_calculate(n - 1) + fibbonachi_calculate(n - 2)
    # r.set(n, result)
    return result


def value_in_redis(func):
    @wraps(func)
    async def check_in_redis(n: FibbonachiParams):
        number = r.get(n.num)
        if number:
            return number
        else:
            return await func(n)
    return check_in_redis


@value_in_redis
async def fib_redis(n: FibbonachiParams):
    result = fibbonachi_calculate(n.num)
    r.set(n.num, result)
    return result


@app.post("/fibbonachi")
async def fibbonachi(n: FibbonachiParams) -> FibbonachiParams:
    result = await fib_redis(n)
    return result


@app.get("/fibbonachi/{number}")
async def get_fibbonachi(number: int, token: str = Depends(oauth2_scheme)):
    result = fibbonachi_calculate(number)
    r.set(result, token)
    return {"result":  result, "token": token}


@app.post("/login")
def user_info(us_info: UserData):
    return us_info



