from typing import Optional

from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel, Field


class UserData(BaseModel):
    user_name: str
    password: str


class FibbonachiParams(BaseModel):
    num: int
    user: Optional[UserData]


class Calculyator(BaseModel):
    number: int = Field(..., gt=0, description="Number should be more than 0")
    stepen: Optional[int] = Field(2, gt=0, description="Number should be more than 0")


app = FastAPI()


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
    return result


@app.post("/fibbonachi")
def fibbonachi(n: FibbonachiParams):
    #  """Рекурсия"""
    result = fibbonachi_calculate(n.num)
    return result

