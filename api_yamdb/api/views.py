from rest_framework import viewsets
from rest_framework.filters import SearchFilter
from rest_framework.viewsets import ModelViewSet
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404

from api.mixins import ModelMixinSet
from api.serializers import (
    CategorySerializer,
    GenreSerializer,
    TitleSerializer,
    ReviewSerializer,
    CommentSerializer,
)
from api.permissions import IsAdminUserOrReadOnly
from api.filters import GenreTitleFilter
from reviews.models import Category, Genre, GenreTitle, Review, Title


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer

    def get_title_obj(self):
        return get_object_or_404(Title, pk=self.kwargs.get('title_id'))

    def get_queryset(self):
        title = self.get_title_obj()
        return title.reviews

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer

    def get_review_obj(self):
        return get_object_or_404(Review, pk=self.kwargs.get('review_id'))

    def get_queryset(self):
        review = self.get_review_obj()
        return review.comments

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


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
    queryset = GenreTitle.objects.all()
    serializer_class = TitleSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsAdminUserOrReadOnly,)
    filter_backends = (DjangoFilterBackend)
    filterset_class = GenreTitleFilter

