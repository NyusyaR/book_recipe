from typing import Optional

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


engine = create_async_engine("sqlite+aiosqlite:///recipes.db")

new_session = async_sessionmaker(engine, expire_on_commit=False)


class Model(DeclarativeBase):
    pass


class RecipesOrm(Model):
    __tablename__ = "receipt"

    id_recipe: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True
    )
    name: Mapped[str]
    cooking_time: Mapped[int]
    ingredients: Mapped[str]
    description: Mapped[str]
    views_count: Mapped[Optional[int]]


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)
