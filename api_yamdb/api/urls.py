from rest_framework.routers import DefaultRouter
from django.urls import include, path

from api.views import (
    ConfirmationViewSet,
    UserCreateViewSet,
    UserViewSet,
    CategoryViewSet,
    GenreViewSet,
    TitleViewSet,
    ReviewViewSet,
    CommentViewSet,
)    

app_name = 'api'

router_v1 = DefaultRouter()

router_v1.register('auth', UserCreateViewSet)
router_v1.register('users', UserViewSet)
router_v1.register('categories', CategoryViewSet, basename='categories')
router_v1.register('genres', GenreViewSet, basename='genres')
router_v1.register('titles', TitleViewSet)
router_v1.register(r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet,
                   basename='review')

router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comment')

urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('v1/auth/signup/', UserCreateViewSet.as_view(), name='user_create'),
    path('v1/auth/token/', ConfirmationViewSet.as_view(), name='confirm_user'),
]
