from django.core.mail import send_mail
from rest_framework import filters, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from reviews.models import CustomUser
from api.serializers import ConfirmationSerializer, UserCreateSerializer
from api.permissions import IsAdmin


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
