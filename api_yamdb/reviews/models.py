from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator

from .validators import validate_year


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


class Genre(models.Model):
    """Модель жанры."""
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.slug


class Category(models.Model):
    """Модель категории."""
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self) -> str:
        return self.slug


class Title(models.Model):
    """Модель Произведение."""

    name = models.CharField(
        'название',
        max_length=256,
        db_index=True
    )
    year = models.IntegerField(
        'Год релиза',
        validators=[validate_year],
        help_text='Введите год релиза'
    )
    genre = models.ManyToManyField(Genre, verbose_name='Жанр')
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        verbose_name='Категория',
        help_text='Введите категорию произведения',
        null=True,
        blank=True,
        related_name='titles'
    )
    description = models.TextField(
        null=True,
        verbose_name='Описание'
    )
    rating = models.IntegerField(null=True)

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self) -> str:
        return self.name


class Review(models.Model):
    text = models.TextField()
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name='reviews')
    author = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='reviews')
    score = models.IntegerField(
        validators=[
            MaxValueValidator(10),
            MinValueValidator(1)
        ],
    )
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        # constraints = [
        # models.UniqueConstraint(
        #    fields=['author', 'title'],
        #    name='unique_review'
        # )
        # ]
        unique_together = ('author', 'title')


class Comment(models.Model):
    text = models.TextField()
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='comments')
    pub_date = models.DateTimeField(auto_now_add=True)
