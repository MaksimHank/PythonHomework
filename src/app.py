from typing import Optional

from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel, Field
import redis
import logging

r = redis.StrictRedis(host='localhost', port=6379, db=0, charset="utf-8", decode_responses=True)
logger = logging.getLogger(__name__)


class UserData(BaseModel):
    user_name: str
    password: str


class FibbonachiParams(BaseModel):
    num: int
    user: Optional[UserData]


class Calculyator(BaseModel):
    number: int = Field(..., gt=0, description="Number should be more than 0")
    stepen: Optional[int] = Field(2, gt=0, description="Number should be more than 0")


app = FastAPI(debug=True)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}


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
    r.set(n, result)
    return result


@app.post("/fibbonachi")
def fibbonachi(n: FibbonachiParams):
    number = r.get(n.num)
    logger.debug(f"Recive number {number}")
    if number is not None:
        return number
    result = fibbonachi_calculate(n.num)
    r.set(n.num, result)
    return result


@app.get("/fibbonachi/{number}")
def get_fibbonachi(number):
    result = r.get(number)
    return result


@app.post("/login")
def user_info(us_info: UserData):
    return us_info
