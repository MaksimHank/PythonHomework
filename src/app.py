from typing import Optional

from fastapi import FastAPI, Query

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}


@app.get("/fibbonachi/{n}")
def fibbonachi(n: int):
    #  """Рекурсия"""
    if n in {0, 1}:
        return n
    result = fibbonachi(n - 1) + fibbonachi(n - 2)
    return result


