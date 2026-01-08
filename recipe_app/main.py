from fastapi import FastAPI
from contextlib import asynccontextmanager

from recipe_app.database import create_tables
from recipe_app.router import routers as tasks_router


@asynccontextmanager
async def lifespan(app: FastAPI):  # контекстный менеджер
    await create_tables()
    print("База готова")
    yield
    print("Выключение")


app = FastAPI(lifespan=lifespan)

app.include_router(tasks_router)
