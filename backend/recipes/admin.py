from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import (Favorite, Ingredient, Recipe, RecipeIngredients,
                     RecipeTags, ShoppingCart, Tag)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    '''Админский интерфейс для модели тегов'''

    list_display = ('id', 'name', 'slug')
    list_editable = ('name', 'slug',)
    search_fields = ('name', 'slug')
    list_filter = ('name', 'slug')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    '''Админский интерфейс для модели ингредиентов'''

    list_display = ('id', 'name', 'measurement_unit')
    list_editable = ('name', 'measurement_unit',)
    search_fields = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    '''Админский интерфейс для модели рецептов'''

    list_display = ('id', 'author', 'name',
                    'favorites', 'display_ingredients', 'display_image')
    list_editable = ('author', 'name')
    search_fields = ('author__username', 'name')
    list_filter = ('tags',)

    @admin.display(description='Избранное')
    def favorites(self, obj):
        '''
        Метод, возвращающий количество
        избранных рецептов для данного рецепта
        '''
        return obj.favorite_recipe.count()

    @admin.display(description='Связанные ингредиенты')
    def display_ingredients(self, obj):
        '''
        Метод, возвращающий все
        ингредиенты для данного рецепта
        '''
        return ', '.join(
            [ingredient.ingredient.name
             for ingredient in obj.recipe_ingredients.all()]
        )

    @admin.display(description='Изображение рецепта')
    def display_image(self, obj):
        '''
        Метод, отображающий изображение
        рецепта в админке
        '''
        if obj.image:
            return mark_safe(
                f'<img src="{obj.image.url}" width="100" height="100">')
        return None


@admin.register(RecipeIngredients)
class RecipeIngredientsAdmin(admin.ModelAdmin):
    '''Админский интерфейс для модели игредиентов рецептов'''

    list_display = ('id', 'recipe', 'ingredient')
    list_editable = ('recipe', 'ingredient')


@admin.register(RecipeTags)
class RecipeTagsAdmin(admin.ModelAdmin):
    '''Админский интерфейс для модели тегов рецептов'''

    list_display = ('id', 'recipe', 'tag')
    list_editable = ('recipe', 'tag')


class UserRecipe(admin.ModelAdmin):
    '''Базовый класс для описания полей пользователя и рецепта'''
    list_display = ('id', 'user', 'recipe')
    list_editable = ('user', 'recipe')


@admin.register(Favorite)
class FavoriteAdmin(UserRecipe):
    '''Админский интерфейс для модели избранного'''
    pass


@admin.register(ShoppingCart)
class ShoppingCartAdmin(UserRecipe):
    '''Админский интерфейс для модели списка покупок'''
    pass
