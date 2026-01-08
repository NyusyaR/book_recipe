from fastapi import HTTPException
from typing import Optional, Sequence

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from recipe_app.database import new_session, RecipesOrm
from recipe_app.schemas import RecipeAdd, RecipeID


class RecipesRepository:
    @classmethod
    async def find_one(cls, id_recipe) -> Optional[RecipeID]:
        """Получение детальной информации по заданному ID рецепта"""
        try:
            if id_recipe <= 0 or not isinstance(id_recipe, int):
                raise HTTPException(
                    status_code=422,
                    detail="Ошибка, id_recipe должен быть целым числом.",
                )
            async with new_session() as session:
                query = select(RecipesOrm).where(
                    RecipesOrm.id_recipe == id_recipe
                )
                result = await session.execute(query)
                recipe_orm = result.scalar_one_or_none()

                if recipe_orm is None:
                    raise HTTPException(
                        status_code=404, detail="Рецепт не найден"
                    )

                await session.execute(
                    update(RecipesOrm)
                    .where(RecipesOrm.id_recipe == id_recipe)
                    .values(views_count=RecipesOrm.views_count + 1)
                )
                await session.commit()
                return RecipeID.model_validate(recipe_orm)
        except HTTPException:
            raise
        except Exception:
            raise HTTPException(
                status_code=500, detail="Internal server error"
            )

    @classmethod
    async def find_all(cls) -> Sequence[RecipesOrm]:
        """Получение всех рецептов"""
        async with new_session() as session:
            try:
                query = select(RecipesOrm).order_by(
                    RecipesOrm.views_count.desc(), 
                    RecipesOrm.cooking_time.asc()
                )
                result = await session.execute(query)
                recipe_model = result.scalars().all()
                return recipe_model
            except Exception:
                raise HTTPException(
                    status_code=500, 
                    detail="Ошибка сервера при обработке запроса."
                )

    @classmethod
    async def find_by_name(cls, name: str) -> Optional[RecipesOrm]:
        """Проверка наличия рецепта с указанным названием"""
        async with new_session() as session:
            query = select(RecipesOrm).filter(RecipesOrm.name == name)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def add_one(cls, name: RecipeAdd) -> RecipeID:
        """Создание нового рецепта"""
        async with new_session() as session:
            existing_recipe = await cls.find_by_name(name.name)
            if existing_recipe:
                raise HTTPException(
                    status_code=500, 
                    detail="Рецепт с таким названием уже существует"
                )

            recipe_dict = name.model_dump(exclude_unset=True)
            new_recipe = RecipesOrm(**recipe_dict)
            try:
                session.add(new_recipe)
                await session.flush()
                await session.commit()
                return RecipeID.model_validate(new_recipe)
            except IntegrityError as err:
                await session.rollback()
                raise HTTPException(
                    status_code=400,
                    detail=f"Ошибка при создании рецепта: "
                    f"дублирование записей: {err}",
                )
            except SQLAlchemyError as err:
                await session.rollback()
                raise HTTPException(
                    status_code=500, 
                    detail=f"Ошибка при сохранении рецепта: {err}"
                )
