from typing import Annotated
from fastapi import Path, APIRouter

router = APIRouter(prefix="/items", tags=["items"])


@router.get("/")
async def list_items():
    return {
        "item 1",
        "item 2",
    }


@router.get("/latest/")
async def get_latest_item():
    return {"item": {"id": 0, "name": "latest"}}


@router.get("/{item_id}/")
async def get_item_by_id(item_id: Annotated[int, Path(ge=1, lt=1_000_000)]):
    return {"item": {"id": item_id}}
