from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from core.config import settings
from api_v1 import router as router_v1
from items_views import router as items_router
from users.views import router as users_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(router=router_v1, prefix=settings.api_v1_prefix)
app.include_router(items_router)
app.include_router(users_router)


@app.get("/")
async def root():
    return {"message": "Hello World!!!"}


@app.get("/hello/")
async def hello(name: str = "World"):
    name = name.strip().title()
    return {"message": f"Hello {name}"}


@app.post("/calc/add/")
async def add(a: int, b: int):
    return {"a": a, "b": b, "result": a + b}


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
