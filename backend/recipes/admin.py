from django.contrib import admin

from .models import (Favorite, Ingredient, Recipe, RecipeIngredients,
                     RecipeTags, ShoppingCart, Tag)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    list_editable = ('name', 'slug',)
    search_fields = ('name', 'slug')
    list_filter = ('name', 'slug')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    list_editable = ('name', 'measurement_unit',)
    search_fields = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'name', 'favorites')
    list_editable = ('author', 'name')
    search_fields = ('author__username', 'name')
    list_filter = ('tags',)

    @admin.display(description='Избранное')
    def favorites(self, obj):
        return obj.favorite_recipe.count()


@admin.register(RecipeIngredients)
class RecipeIngredientsAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'ingredient')
    list_editable = ('recipe', 'ingredient')


@admin.register(RecipeTags)
class RecipeTagsAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'tag')
    list_editable = ('recipe', 'tag')


class UserRecipe(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    list_editable = ('user', 'recipe')


@admin.register(Favorite)
class FavoriteAdmin(UserRecipe):
    pass


@admin.register(ShoppingCart)
class ShoppingCartAdmin(UserRecipe):
    pass
