import base64

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredients,
                            ShoppingCart, Tag)
from users.models import Subscribe, User

from .constants import DOMAIN_URL


def get_subscriptions(obj, context):
    user = context.get('request').user
    if (user.is_authenticated and Subscribe.objects.filter(
            user=user, author=obj).exists()):
        return True
    return False


class GetImageBase64(serializers.ImageField):

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data'):
            format, string = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(string), name='temp.' + ext)

        return super().to_internal_value(data)

    def to_representation(self, value):
        if value:
            return DOMAIN_URL + value.url


class CustomUserCreateSerializer(UserCreateSerializer):

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'password')
        extra_kwargs = {
            'first_name': {'required': True, 'allow_blank': False},
            'last_name': {'required': True, 'allow_blank': False},
            'password': {'write_only': True}
        }


class UserReadSerializer(UserSerializer):
    avatar = GetImageBase64()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'is_subscribed', 'avatar')

    def get_is_subscribed(self, obj):
        return get_subscriptions(obj, self.context)


class SetPasswordSerializer(serializers.Serializer):
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
    avatar = GetImageBase64()

    def update(self, instance, validated_data):
        instance.avatar = validated_data['avatar']
        instance.save()
        return instance


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'name', 'measurement_unit', 'amount')


class ReadRecipeSerializer(serializers.ModelSerializer):
    image = GetImageBase64()
    author = UserReadSerializer()
    ingredients = RecipeIngredientSerializer(
        source='recipe_ingredienys', many=True)
    tags = TagSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')

    def get_is_favorited(self, obj):
        return (
            self.context.get('request').user.is_authenticated
            and Favorite.objects.filter(user=self.context['request'].user,
                                        recipe=obj).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        return (self.context.get('request').user.is_authenticated
                and ShoppingCart.objects.filter(
                    user=self.context['request'].user,
                    recipe=obj).exists()
                )


class CreateIngredientToRecipe(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'amount')


class CreateRecipeSerializer(serializers.ModelSerializer):
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
    image = GetImageBase64()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeSerializer(serializers.ModelSerializer):
    avatar = GetImageBase64(read_only=True)
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField(source='recipe_author')
    is_subscribed = serializers.SerializerMethodField()
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
        return obj.recipe_author.count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.data.get('recipes_limit')
        recipes = obj.recipe_author.all()

        if limit:
            recipes = recipes[:limit]
        return RecipeSerializer(recipes, many=True).data

    def get_is_subscribed(self, obj):
        return get_subscriptions(obj, self.context)
