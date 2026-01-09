from pydantic import BaseModel, ConfigDict, Field


class RecipesBase(BaseModel):
    name: str = Field(description="Название блюда")
    cooking_time: int = Field(gt=0, description="Время приготовления блюда")
    ingredients: str = Field(description="Ингридиенты блюда")
    description: str = Field(description="Описание и этапы приготовления блюда")
    views_count: int = Field(default=0, description="Количнство просмотров")


class RecipeAdd(RecipesBase):
    """Что приходит от клиента при создании"""


class RecipeID(RecipesBase):
    """Что отдаем клиенту"""

    id_recipe: int = Field(description="Идентификатор рецепта")
    
    model_config = ConfigDict(from_attributes=True)
