from django_filters import rest_framework
from django_filters.rest_framework import FilterSet, filters

from recipes.models import Ingredient, Recipe, Tag


class IngredientFilter(FilterSet):
    '''
    Фильтр для представления ингредиентов
    по имени рецепта
    '''

    name = rest_framework.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(FilterSet):
    '''
    Фильтр для представления рецептов по тегам,
    авторам, наличию в списке покупок или избранном
    '''

    tags = filters.ModelMultipleChoiceFilter(queryset=Tag.objects.all(),
                                             field_name='tags__slug',
                                             to_field_name='slug')
    is_favorited = filters.BooleanFilter(method='get_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('tags', 'author')

    def get_is_favorited(self, queryset, name, value):
        if value:
            return queryset.filter(favorite_recipe__user=self.request.user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(shoppingcart_recipe__user=self.request.user)
        return queryset
