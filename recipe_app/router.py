from fastapi import APIRouter, HTTPException, Path

from recipe_app.schemas import RecipeAdd, RecipeID
from recipe_app.repository import RecipesRepository


routers = APIRouter(
    tags=["Рецепты"],
)


@routers.get("/recipes/", response_model=list[RecipeID])
async def get_recipes():
    """Получение всех рецептов"""
    recipes_orm = await RecipesRepository.find_all()
    return [RecipeID.model_validate(r) for r in recipes_orm]


@routers.get("/recipes/{id_recipe}", response_model=RecipeID)
async def get_one_recipe(
    id_recipe: int = Path(..., gt=0, description="ID рецепта должен быть больше 0")
):  # noqa: B008
    """Получение рецепта по ID
    Возращает экземпляр RecipeID или None, если рецепт не найден"""
    recipe = await RecipesRepository.find_one(id_recipe)
    if recipe is None:
        raise HTTPException(status_code=404, detail="Not Found")

    return RecipeID.model_validate(recipe.__dict__)


@routers.post("/recipes/", response_model=RecipeID)
async def add_recipe(recipe: RecipeAdd):
    """Добавление рецепта в БД
    Возвращает ID добавленного рецепта"""
    try:
        return await RecipesRepository.add_one(recipe)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
