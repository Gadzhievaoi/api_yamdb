from rest_framework.filters import SearchFilter
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination

from .mixins import ModelMixinSet
from .serializers import (CategorySerializer, GenreSerializer, TitleSerializer)
from .permissions import IsAdminUserOrReadOnly
from reviews.models import Category, Genre, Title
from api.filters import TitleFilter


class CategoryViewSet(ModelMixinSet):
    """Получить список всех категорий."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsAdminUserOrReadOnly,)
    filter_backends = (SearchFilter, )
    search_fields = ('name', )
    lookup_field = 'slug'


class GenreViewSet(ModelMixinSet):
    """Получить список всех жанров."""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsAdminUserOrReadOnly,)
    filter_backends = (SearchFilter,)
    search_fields = ('name', )
    lookup_field = 'slug'


class TitleViewSet(ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsAdminUserOrReadOnly,)
    filter_backends = (DjangoFilterBackend)
    filterset_class = TitleFilter
