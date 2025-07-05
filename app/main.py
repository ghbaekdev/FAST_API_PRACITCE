from fastapi import FastAPI
from typing import Union
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.get("/")
def read_root():
    logger.info("루트 엔드포인트 호출됨")
    return {"message": "Hello, FastAPI!"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    logger.info(f"아이템 조회: item_id={item_id}, q={q}")
    return {"item_id": item_id, "q": q}