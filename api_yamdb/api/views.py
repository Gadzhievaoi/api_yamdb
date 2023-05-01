from django.core.mail import send_mail
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from rest_framework import filters, status, viewsets
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.viewsets import ModelViewSet

from reviews.models import CustomUser, Category, Genre, GenreTitle, Review, Title
from api.permissions import IsAdmin, IsAdminUserOrReadOnly
from api.mixins import ModelMixinSet
from api.serializers import (
    CategorySerializer,
    GenreSerializer,
    TitleSerializer,
    ReviewSerializer,
    CommentSerializer,
    ConfirmationSerializer,
    UserCreateSerializer,
)
from api.filters import GenreTitleFilter


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [IsAdmin]
    pagination_class = LimitOffsetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['^username']
    lookup_field = 'username'

    @action(
        methods=['GET', 'PATCH'],
        detail=False,
        permission_classes=[IsAuthenticated],
    )
    def me(self, request):
        if request.method.lower() == "GET":
            serializer = UserCreateSerializer(request.user)
            return Response(serializer.data, status.HTTP_200_OK)

        serializer = UserCreateSerializer(
            request.user, data=request.data, partial=True)
        if serializer.is_valid():
            if (
                'role' in serializer.validated_data
                and not request.user.is_admin
            ):
                serializer.validated_data['role'] = request.user.role
            serializer.save()
            return Response(serializer.validated_data,
                            status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserCreateViewSet(viewsets.ModelViewSet):

    def create(self, request):
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            if not CustomUser.objects.filter(
                username=serializer.validated_data['username']
            ).exists():
                serializer.save(role='user')
            user = CustomUser.objects.get(
                username=serializer.validated_data['username']
            )
            user.confirmation_code = str(RefreshToken.for_user(user))
            user.save(update_fields=['confirmation_code'])
            send_mail(
                'Confirmation code.',
                user.confirmation_code,
                'no_replay@yamdb.ru',
                [user.email, ],
                fail_silently=False,
            )
            return Response(
                serializer.validated_data,
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConfirmationViewSet(viewsets.ModelViewSet):

    def create(self, request):
        serializer = ConfirmationSerializer(data=request.data)
        if serializer.is_valid():
            user = CustomUser.objects.get(
                username=serializer.validated_data['username']
            )
            user.confirmation_code = ''
            user.save(update_fields=['confirmation_code'])
            return Response(
                {'token': str(RefreshToken.for_user(user).access_token)},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
