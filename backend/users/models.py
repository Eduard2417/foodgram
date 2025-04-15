from django.contrib.auth.models import AbstractUser
from django.db import models

from .constants import MAX_EMAIL_VALUE


class User(AbstractUser):
    '''Модель для представления пользователя'''

    email = models.EmailField('электронная почта', max_length=MAX_EMAIL_VALUE)
    avatar = models.ImageField('аватар', upload_to='users_avatars', blank=True)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    def __str__(self):
        return self.username


class Subscribe(models.Model):
    '''Модель для представления подписок'''

    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             verbose_name='подписчик',
                             related_name='subscriber')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               verbose_name='автор',
                               related_name='author')

    class Meta:
        verbose_name = 'Подписчик'
        verbose_name_plural = 'Подписчики'

    def __str__(self):
        return f'{self.user}, {self.author}'
