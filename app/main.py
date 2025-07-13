from fastapi import FastAPI, Query, Path, File, UploadFile, Depends, HTTPException
import logging
from enum import Enum
from typing import Union,Annotated, Literal
from pydantic import BaseModel, Field
from app.core.auth import get_current_user, get_optional_user
from app.api.endpoints import auth
# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# 인증 라우터 추가
app.include_router(auth.router, prefix="/auth", tags=["authentication"])

@app.get("/")
def read_root():
    logger.info("루트 엔드포인트 호출됨")
    return {"message": "Hello, FastAPI!"}

from pydantic import BaseModel


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None



fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]


@app.get("/items/")
async def read_items_query(
    q: Union[str, None] = Query(
        default=None,
        alias="item-query",
        title="Query string",
        description="Query string for the items to search in the database that have a good match",
        min_length=3,
        max_length=50,
        pattern="^fixedquery$",
        deprecated=True,
    ),
):
    results: dict[str, list[dict[str, str]]] = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results["items"].append({ "q": q})
    return results

class FilterParams(BaseModel):
    limit: int = Field(100, gt=0, le=100)
    offset: int = Field(0, ge=0)
    order_by: Literal["created_at", "updated_at"] = "created_at"
    tags: list[str] = []


@app.get("/items/")
async def read_items(filter_query: Annotated[FilterParams, Query()]):
    return filter_query

@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item, q: str | None = None):
    result = {"item_id": item_id, **item.dict()}
    if q:
        result.update({"q": q})
    return result

@app.get("/items/{item_id}")
async def read_item(
      item_id: int = Path(title="The ID of the item to get", gt=0, le=1000),
    q: Union[str, None] = Query(default=None, alias="item-query"),
):
    results: dict = {"item_id": item_id}
    if q:
        results["q"] = q
    return results

class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"

@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name is ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}

    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}

    return {"model_name": model_name, "message": "Have some residuals"}

@app.post("/files/")
async def create_file(file: bytes = File()):
    return {"file_size": len(file)}


@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
    return {"filename": file.filename}

# 보호된 엔드포인트 예시들
@app.get("/protected/")
async def read_protected_data(current_user: dict = Depends(get_current_user)):
    """인증이 필요한 엔드포인트"""
    return {"message": "This is protected data", "user_id": current_user["user_id"]}

@app.get("/optional-auth/")
async def read_optional_auth_data(current_user: dict = Depends(get_optional_user)):
    """선택적 인증 엔드포인트 - 토큰이 없어도 접근 가능"""
    if current_user:
        return {"message": "Authenticated user", "user_id": current_user["user_id"]}
    else:
        return {"message": "Anonymous user"}

@app.get("/admin/")
async def admin_only(current_user: dict = Depends(get_current_user)):
    """관리자 전용 엔드포인트 (추가 권한 검사 필요)"""
    # 실제로는 사용자 역할을 확인해야 합니다
    if current_user["user_id"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return {"message": "Admin panel", "user_id": current_user["user_id"]}