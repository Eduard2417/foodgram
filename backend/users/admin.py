from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from rest_framework.authtoken.admin import TokenProxy

from .models import Subscribe, User


@admin.register(User)
class MyUserAdmin(UserAdmin):
    '''Админский интерфейс для модели пользователя'''

    list_display = (
        'id', 'username', 'email', 'first_name', 'last_name'
    )
    list_editable = (
        'username', 'email', 'first_name', 'last_name'
    )
    search_fields = ('email', 'username')


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    '''Админский интерфейс для модели подписок'''

    list_display = (
        'id', 'user', 'author'
    )
    list_editable = (
        'user', 'author',
    )


admin.site.unregister(Group)
admin.site.unregister(TokenProxy)
