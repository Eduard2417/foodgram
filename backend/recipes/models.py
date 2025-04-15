from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from .constants import (INGREDIENT_NAME_LENGTH, INGREDIENT_UNIT_LENGTH,
                        MIN_VALUE, RECIPE_NAME_LENGTH, TAG_MAX_LENGTH)

User = get_user_model()


class Tag(models.Model):
    '''Модель для представления тегов'''

    name = models.CharField('название', max_length=TAG_MAX_LENGTH, unique=True)
    slug = models.SlugField('слаг', max_length=TAG_MAX_LENGTH, unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    '''Модель для представления ингредиентов'''

    name = models.CharField('название', max_length=INGREDIENT_NAME_LENGTH)
    measurement_unit = models.CharField(
        'единица измерения', max_length=INGREDIENT_UNIT_LENGTH)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    '''Модель для представления рецептов'''

    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               verbose_name='автор',
                               related_name='recipe_author')
    name = models.CharField('название', max_length=RECIPE_NAME_LENGTH)
    image = models.ImageField('картинка', upload_to='recipe_images')
    text = models.TextField('текстовое описание')
    ingredients = models.ManyToManyField(
        Ingredient, through='RecipeIngredients')
    tags = models.ManyToManyField(Tag, through='RecipeTags')
    cooking_time = models.IntegerField(
        'время приготовления (в минутах)',
        validators=(MinValueValidator(MIN_VALUE),))
    pub_date = models.DateTimeField('дата публикации', auto_now_add=True)

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class RecipeIngredients(models.Model):
    '''Модель для представления ингредиентов рецептов'''

    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE,
                                   verbose_name='ингредиент')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               verbose_name='рецепт',
                               related_name='recipe_ingredients')
    amount = models.IntegerField(
        'количество', validators=(MinValueValidator(MIN_VALUE),))

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецептов'


class RecipeTags(models.Model):
    '''Модель для представления тегов рецептов'''

    tag = models.ForeignKey(Tag, on_delete=models.CASCADE,
                            verbose_name='тег')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               verbose_name='рецепт')

    class Meta:
        verbose_name = 'Тег рецепта'
        verbose_name_plural = 'Теги рецептов'


class UserRecipe(models.Model):
    '''Абстрактная модель для создания полей пользователя и рецепта'''

    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             verbose_name='владелец',
                             related_name='%(class)s_user')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               verbose_name='рецепт',
                               related_name='%(class)s_recipe')

    class Meta:
        abstract = True


class Favorite(UserRecipe):
    '''Модель для представления избранного'''

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = (
            models.UniqueConstraint(fields=('user', 'recipe'),
                                    name='unique_favorite'),
        )


class ShoppingCart(UserRecipe):
    '''Модель для представления списка покупок'''

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = (
            models.UniqueConstraint(fields=('user', 'recipe'),
                                    name='unique_shopping_cart'),
        )
