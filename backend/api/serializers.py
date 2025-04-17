import base64

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredients,
                            ShoppingCart, Tag)
from users.models import Subscribe, User


class GetImageBase64(serializers.ImageField):
    '''Класс метод для управления изображениями в base64'''

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data'):
            format, string = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(string), name='temp.' + ext)

        return super().to_internal_value(data)


class BaseUserSerializer(serializers.ModelSerializer):
    '''
    Абстрактный класс сериализатора с
    полем аватарки и проверкой наличия подписки
    '''
    avatar = GetImageBase64(read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        abstract = True

    def get_is_subscribed(self, obj):
        '''Метод для проверки наличия подписки'''

        user = self.context.get('request').user
        if (user.is_authenticated and Subscribe.objects.filter(
                user=user, author=obj).exists()):
            return True
        return False


class CustomUserCreateSerializer(UserCreateSerializer):
    '''Сериализатор для создания пользователя'''

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'password')
        extra_kwargs = {
            'first_name': {'required': True, 'allow_blank': False},
            'last_name': {'required': True, 'allow_blank': False},
            'password': {'write_only': True}
        }


class UserReadSerializer(BaseUserSerializer):
    '''Сериализатор для чтения пользователя'''

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'is_subscribed', 'avatar')


class SetPasswordSerializer(serializers.Serializer):
    '''Сериализатор для изменения пароля'''

    current_password = serializers.CharField()
    new_password = serializers.CharField()

    def validate(self, attrs):
        try:
            validate_password(attrs['new_password'])
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return super().validate(attrs)

    def update(self, instance, validated_data):
        if not instance.check_password(validated_data['current_password']):
            raise serializers.ValidationError('Неверный пароль')

        if (validated_data['new_password']
           == validated_data['current_password']):
            raise serializers.ValidationError(
                'Новый пароль не должен совпадать с текущим')
        instance.set_password(validated_data['new_password'])
        instance.save()
        return validated_data


class SetUserAvatarSerializer(serializers.Serializer):
    '''Сериализатор для изменения аватарки пользователя'''

    avatar = GetImageBase64()

    def update(self, instance, validated_data):
        instance.avatar = validated_data['avatar']
        instance.save()
        return instance


class TagSerializer(serializers.ModelSerializer):
    '''Сериализатор для тегов'''

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    '''Сериализатор для ингредиентов'''

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    '''Сериализатор для ингредиентов рецепта'''

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def validate(self, attrs):
        if attrs['amount'] == 0:
            raise serializers.ValidationError('ну не')
        return super().validate(attrs)


class ReadRecipeSerializer(serializers.ModelSerializer):
    '''Сериализатор для чтения рецепта'''

    image = GetImageBase64()
    author = UserReadSerializer()
    ingredients = RecipeIngredientSerializer(
        source='recipe_ingredients', many=True)
    tags = TagSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')

    def get_is_favorited(self, obj):
        '''Метод проверяющий наличие рецепта в избранном'''

        return (
            self.context.get('request').user.is_authenticated
            and Favorite.objects.filter(user=self.context['request'].user,
                                        recipe=obj).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        '''Метод проверяющий наличие рецепта в списке покупок'''

        return (self.context.get('request').user.is_authenticated
                and ShoppingCart.objects.filter(
                    user=self.context['request'].user,
                    recipe=obj).exists()
                )


class CreateIngredientToRecipe(serializers.ModelSerializer):
    '''Сериализатор для создания ингредиента для рецепта'''

    id = serializers.IntegerField()

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'amount')

    def validate(self, attrs):
        if attrs['amount'] == 0:
            raise serializers.ValidationError('ну не')
        return super().validate(attrs)


class CreateRecipeSerializer(serializers.ModelSerializer):
    '''Сериализатор для создания рецепта'''

    image = GetImageBase64()
    tags = serializers.PrimaryKeyRelatedField(many=True,
                                              queryset=Tag.objects.all())
    ingredients = CreateIngredientToRecipe(many=True)
    author = UserReadSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'image',
                  'name', 'text', 'cooking_time', 'author')

    def create_tag_and_ingredient(self, recipe, tags, ingredients):
        '''
        Метод для создания записей в модели
        тегов рецепта и ингредиентов рецепта
        '''
        recipe.tags.set(tags)

        for ingredient in ingredients:
            ingredient_obj = Ingredient.objects.get(id=ingredient['id'])
            RecipeIngredients.objects.create(amount=ingredient['amount'],
                                             recipe=recipe,
                                             ingredient=ingredient_obj)

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=self.context['request'].user,
                                       **validated_data)

        self.create_tag_and_ingredient(recipe, tags, ingredients)

        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time)
        instance.image = validated_data.get(
            'image', instance.image)
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        RecipeIngredients.objects.filter(
            recipe=instance,
            ingredient__in=instance.ingredients.all()).delete()
        instance.save()
        self.create_tag_and_ingredient(instance, tags, ingredients)
        return instance

    def to_representation(self, instance):

        serializer = ReadRecipeSerializer(
            instance,
            context={
                'request': self.context.get('request')
            }
        )
        return serializer.data


class RecipeSerializer(serializers.ModelSerializer):
    '''Сериализатор для краткой информации о рецепте'''

    image = GetImageBase64()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeSerializer(BaseUserSerializer):
    '''Сериализатор для чтения подписок'''

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField(source='recipe_author')
    username = serializers.ReadOnlyField()
    email = serializers.ReadOnlyField()
    first_name = serializers.ReadOnlyField()
    last_name = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name',
                  'recipes', 'avatar', 'recipes_count', 'is_subscribed')

    def get_recipes_count(self, obj):
        '''Метод для получения солличества рецептов автора'''

        return obj.recipe_author.count()

    def get_recipes(self, obj):
        '''Метод для ограничения колличества рецептов на странице'''

        request = self.context.get('request')
        limit = request.data.get('recipes_limit')
        recipes = obj.recipe_author.all()

        if limit:
            recipes = recipes[:limit]
        return RecipeSerializer(recipes, many=True).data


class SubscribeCreateSerializer(serializers.ModelSerializer):
    '''Метод для создания подписки'''

    class Meta:
        model = Subscribe
        fields = ('user', 'author')

    def validate(self, attrs):
        user = attrs['user']
        author = attrs['author']

        if user == author:
            raise serializers.ValidationError('Нельзя подписаться на себя')

        if Subscribe.objects.filter(user=user, author=author).exists():
            raise serializers.ValidationError(
                'Вы уже подписанны на данного пользователя')
        return super().validate(attrs)

    def create(self, validated_data):
        subscribe = Subscribe.objects.create(**validated_data)
        return subscribe

    def to_representation(self, instance):
        serializer = SubscribeSerializer(instance.author, context=self.context)
        return serializer.data
