import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock
import httpx

from recipe_app.main import app
from recipe_app.schemas import RecipeID
from recipe_app.repository import RecipesRepository


client = TestClient(app)


@pytest.mark.asyncio
class TestGetRecipes:
    """Тесты для эндпоинта GET /recipes/"""

    async def test_get_recipes_success(self):
        """Тест - get запрос рецептов с проверкой валидации - ожидаем 200 OK и список RecipeID"""
        mock_recipes_orm = [
            {"id_recipe": 1, "name": "Борщ", "cooking_time": 60, "ingredients": "Свекла, картофель", "description": "Традиционный суп", "views_count": 0},
            {"id_recipe": 2, "name": "Оладьи", "cooking_time": 20, "ingredients": "Мука, молоко", "description": "На завтрак", "views_count": 0},
        ]
        RecipesRepository.find_all = AsyncMock(return_value=mock_recipes_orm)
        response = client.get("/recipes/")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

        # Проверка рецептов
        assert data[0]["id_recipe"] == 1
        assert data[0]["name"] == "Борщ"
        assert data[0]["cooking_time"] == 60
        assert data[0]["ingredients"] == "Свекла, картофель"
        assert data[0]["description"] == "Традиционный суп"
        assert data[0]["views_count"] == 0
        assert data[1]["id_recipe"] == 2
        assert data[1]["name"] == "Оладьи"
        assert data[1]["cooking_time"] == 20
        assert data[1]["ingredients"] == "Мука, молоко"
        assert data[1]["description"] == "На завтрак"
        assert data[1]["views_count"] == 0

        assert RecipesRepository.find_all.call_count == 1
        for item in data:
            RecipeID.model_validate(item)

    async def test_get_recipes_empty(self):
        """Тест - рецептов в БД нет — ожидаем 200 OK и пустой список"""
        RecipesRepository.find_all = AsyncMock(return_value=[])
        response = client.get("/recipes/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
        assert RecipesRepository.find_all.call_count == 1


@pytest.mark.asyncio
class TestGetOneRecipe:
    """Тесты для эндпоинта GET /recipes/{id}"""

    async def test_get_one_recipe_found(self):
        """ Тест - рецепт есть в БД → 200 OK с данными """

        mock_recipe = RecipeID(
            id_recipe=1,
            name="Борщ",
            cooking_time=60,
            ingredients="Свекла, картофель",
            description="Традиционный суп",
            views_count=0
        )
        RecipesRepository.find_one = AsyncMock(return_value=mock_recipe)
        response = client.get("/recipes/1")
        assert response.status_code == 200
        data = response.json()

        assert data["id_recipe"] == 1
        assert data["name"] == "Борщ"
        assert data["cooking_time"] == 60
        assert data["ingredients"] == "Свекла, картофель"
        assert data["description"] == "Традиционный суп"
        assert data["views_count"] == 0
        assert RecipesRepository.find_one.call_count == 1
        assert RecipesRepository.find_one.call_args[0][0] == 1

    async def test_get_one_recipe_not_found(self):
        """Тест - рецепта нет в БД → 404 Not Found"""
        RecipesRepository.find_one = AsyncMock(return_value=None)
        response = client.get("/recipes/999")
        assert response.status_code == 404
        data = response.json()
        assert data == {"detail": "Not Found"}
        assert RecipesRepository.find_one.call_count == 1
        assert RecipesRepository.find_one.call_args[0][0] == 999

    async def test_get_one_recipe_invalid_id_format(self):
        """Тест - id строка → 422 Unprocessable Entity"""
        response = client.get("/recipes/abc")
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
        error = next(
            (err for err in data["detail"] if "id_recipe" in str(err["loc"])),
            None
        )
        assert error is not None
        assert 'Input should be a valid integer, unable to parse string as an ' in error["msg"]

    async def test_get_one_recipe_negative_id(self):
        """Тест: отрицательный id → 422 (валидация Pydantic)"""
        response = client.get("/recipes/-1")

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
        assert data["detail"] == "Ошибка, id_recipe должен быть целым числом."

    async def test_get_one_recipe_repository_exception(self):
        """Тест: исключение в репозитории → 500 Internal Server Error"""
        RecipesRepository.find_one = AsyncMock(side_effect=Exception("DB error"))
        response = client.get("/recipes/.")
        assert response.status_code == 500
        data = response.json()

        assert "detail" in data
        assert 'Ошибка сервера при обработке запроса.' in data["detail"]
