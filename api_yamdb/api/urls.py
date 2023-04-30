from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import CategoryViewSet, GenreViewSet, GenreTitleViewSet

app_name = 'api'

router_v1 = DefaultRouter()

router_v1.register('categories', CategoryViewSet, basename='categories')
router_v1.register('genres', GenreViewSet, basename='genres')
router_v1.register('titles', GenreTitleViewSet)

urlpatterns = [
    path('v1/', include(router_v1.urls)),
]