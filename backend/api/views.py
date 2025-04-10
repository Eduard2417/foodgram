from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredients,
                            ShoppingCart, Tag)
from users.models import Subscribe, User

from .constants import RECIPE_URL
from .filters import IngredientFilter, RecipeFilter
from .pagination import CustomPaginator
from .permissions import IsAuthorOrReadOnly
from .serializers import (CreateRecipeSerializer, CustomUserCreateSerializer,
                          IngredientSerializer, ReadRecipeSerializer,
                          RecipeSerializer, SetPasswordSerializer,
                          SetUserAvatarSerializer, SubscribeSerializer,
                          TagSerializer, UserReadSerializer)


def manage_list_item(request, recipe, user,
                     model, error_message, delete_message):
    if request.method == 'POST':
        serializer = RecipeSerializer(recipe)
        if not model.objects.filter(user=user,
                                    recipe=recipe).exists():
            model.objects.create(user=user, recipe=recipe)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        return Response({'detail': error_message},
                        status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'DELETE':
        get_object_or_404(model, user=user,
                          recipe=recipe).delete()
        return Response({'detail': delete_message},
                        status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = CustomPaginator
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return ReadRecipeSerializer
        return CreateRecipeSerializer

    @action(methods=['POST', 'DELETE'], detail=True,
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        return manage_list_item(
            request, recipe, request.user,
            Favorite,
            error_message='Рецепт уже добавлен в избранное',
            delete_message='Рецепт успешно удален из избранного')

    @action(methods=['POST', 'DELETE'], detail=True,
            permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        return manage_list_item(
            request, recipe, request.user,
            ShoppingCart,
            error_message='Рецепт уже добавлен в список покупок',
            delete_message='Рецепт успешно удален из списка покупок')

    @action(methods=['GET'], detail=True, url_path='get-link')
    def get_link(self, request, **kwargs):
        url = RECIPE_URL + kwargs['pk']
        return Response({'short-link': url})

    @action(methods=['GET'], detail=False,
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        ingredients = RecipeIngredients.objects.filter(
            recipe__shoppingcart_recipe__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(final_sum=Sum('amount'))
        shopping_cart_txt = ''
        for ingredient in ingredients:
            print(ingredient)
            shopping_cart_txt += (
                f'{ingredient["ingredient__name"]}, '
                f'{ingredient["ingredient__measurement_unit"]}, '
                f'{ingredient["final_sum"]} \n'
            )
        return HttpResponse(shopping_cart_txt, content_type='text/plain')


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    pagination_class = CustomPaginator

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return UserReadSerializer
        return CustomUserCreateSerializer

    @action(methods=['POST'], detail=False,
            permission_classes=(IsAuthenticated,))
    def set_password(self, request,):
        serializer = SetPasswordSerializer(request.user, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response(
            {'detail': 'Пароль успешно изменен'},
            status=status.HTTP_204_NO_CONTENT)

    @action(methods=['PUT', 'DELETE'], detail=False,
            url_path='me/avatar', permission_classes=(IsAuthenticated,))
    def me_avatar(self, request):

        if request.method == 'PUT':
            serializer = SetUserAvatarSerializer(
                request.user, data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
            return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)

        if request.method == 'DELETE':
            request.user.avatar.delete()
            return Response(
                {'detail': 'Аватар успешно удален!'},
                status=status.HTTP_204_NO_CONTENT)

    @action(methods=['GET'], detail=False,
            permission_classes=(IsAuthenticated,))
    def me(self, request):
        serializer = UserReadSerializer(request.user,
                                        context={'request': self.request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['POST', 'DELETE'], detail=True,
            permission_classes=(IsAuthenticated,))
    def subscribe(self, request, **kwargs):
        author = get_object_or_404(User, id=kwargs['pk'])
        user = request.user

        if request.method == 'POST':
            if user == author:
                return Response({'detail': 'Нельзя подписаться на себя'},
                                status=status.HTTP_400_BAD_REQUEST)

            if Subscribe.objects.filter(user=user, author=author).exists():
                return Response(
                    {'detail': 'Вы уже подписанны на данного пользователя'},
                    status=status.HTTP_400_BAD_REQUEST)

            serializer = SubscribeSerializer(author, data=request.data,
                                             context={'request': request})

            if serializer.is_valid(raise_exception=True):
                Subscribe.objects.create(user=user, author=author)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            get_object_or_404(Subscribe, user=user, author=author).delete()
            return Response(
                {'detail': f'Вы отписались от пользователя {author.username}'},
                status=status.HTTP_204_NO_CONTENT)

    @action(methods=['GET'], detail=False,
            permission_classes=(IsAuthenticated,),
            pagination_class=CustomPaginator)
    def subscriptions(self, request):
        queryset = User.objects.filter(author__user=request.user)
        page = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(page, many=True,
                                         context={'request': request})
        return self.get_paginated_response(serializer.data)
