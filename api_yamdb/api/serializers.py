from rest_framework import serializers, validators
from django.shortcuts import get_object_or_404
from reviews.models import CustomUser


class UserCreateSerializer(serializers.ModelSerializer):
    username = serializers.RegexField(
        r'^[\w.@+-]+\Z',
        max_length=150,
        required=True,
        validators=[
            validators.UniqueValidator(
                queryset=CustomUser.objects.all(),
                message='Пользователь с таким именем уже существует.'
            )
        ]
    )
    email = serializers.EmailField(
        max_length=254,
        required=True,
        validators=[
            validators.UniqueValidator(
                queryset=CustomUser.objects.all(),
                message='Пользователь с таким email уже существует.'
            )
        ]
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')

    def validate(self, attrs):
        if attrs['username'].lower() == 'me':
            raise serializers.ValidationError(
                'Использовать имя "me" в качестве username запрещено.'
            )
        self.validate_unique_user(attrs['username'], attrs['email'])
        return attrs

    def validate_unique_user(self, username, email):
        if CustomUser.objects.filter(username=username, email=email).exists():
            return
        if CustomUser.objects.filter(username=username).exists():
            raise serializers.ValidationError({
                'username':
                'Пользователь с именем {} уже есть в базе.'.format(username)
            })
        if CustomUser.objects.filter(email=email).exists():
            raise serializers.ValidationError({
                'email':
                'Пользователь с email {} уже есть в базе.'.format(email)
            })


class ConfirmationSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=150,
        required=True,
    )
    confirmation_code = serializers.CharField(
        required=True,
    )

    class Meta:
        model = CustomUser
        fields = (
            'username',
            'confirmation_code'
        )

    def validate(self, attrs):
        user = get_object_or_404(CustomUser, username=attrs['username'])
        if not user.confirmation_code == attrs['confirmation_code']:
            raise serializers.ValidationError('Неверный код подтверждения.')
        return attrs
