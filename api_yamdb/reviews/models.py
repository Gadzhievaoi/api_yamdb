from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    USER = 'user'
    ADMIN = 'admin'
    MODERATOR = 'moderator'

    ROLES = [
        (USER, 'Пользователь'),
        (ADMIN, 'Администратор'),
        (MODERATOR, 'Модератор'),
    ]

    username = models.TextField(
        max_length=150,
        unique=True,
        blank=True,
        verbose_name='Логин',
        help_text='Введите логин для регистрации, не более 150 символов'
                  'используя только буквы, цифры и @/./+/-/_ .',
    )
    email = models.EmailField(
        max_length=254,
        unique=True,
        blank=True,
        verbose_name='Адрес электронной почты',
        help_text='Введите адрес электронной почты для регистрации.',
    )
    confirmation_code = models.TextField(
        null=True,
        blank=True,
        verbose_name='Код подтверждения',
        help_text='Введите код подтверждения из письма'
                  'электронной почты, указанной при регистрации.',
    )
    first_name = models.TextField(
        max_length=150,
        verbose_name='Имя',
        help_text='Введите свое имя.',
    )
    last_name = models.TextField(
        max_length=150,
        verbose_name='Фамилия',
        help_text='Введите свою фамилию.',
    )
    bio = models.TextField(
        max_length=1000,
        verbose_name='Биография пользователя',
        help_text='Кратко опишите свою биографию.',
    )
    role = models.CharField(
        max_length=16,
        choices=ROLES,
        default=USER,
        verbose_name='Роль пользователя',
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    @property
    def is_moderator(self):
        return self.role == CustomUser.MODERATOR

    @property
    def is_admin(self):
        return (
            self.role == CustomUser.ADMIN
            or self.is_superuser
            or self.is_staff
        )

    def __str__(self):
        return self.username
