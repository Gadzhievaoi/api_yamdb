from rest_framework.routers import DefaultRouter
from django.urls import include, path

from api.views import ConfirmationViewSet, UserCreateViewSet, UserViewSet

router_v1 = DefaultRouter()
router_v1.register('auth', UserCreateViewSet)
router_v1.register('users', UserViewSet)

urlpatterns = [
    path('v1/auth/signup/', UserCreateViewSet.as_view(), name='user_create'),
    path('v1/auth/token/', ConfirmationViewSet.as_view(), name='confirm_user'),
    path('v1/', include(router_v1.urls)),
]
