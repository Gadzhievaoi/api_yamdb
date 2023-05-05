from django.contrib.auth import get_user_model
from rest_framework import serializers, validators
from rest_framework.relations import SlugRelatedField
# from rest_framework.validators import UniqueTogetherValidator
from django.shortcuts import get_object_or_404
# from django.db.models import Avg

from reviews.models import Category, Comment, CustomUser, Genre, Review, Title


CustomUser = get_user_model()


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

    def validate(self, value):
        if 'me' == value.get('username'):
            raise serializers.ValidationError(
                'Использовать имя "me" в качестве username запрещено.'
            )
        return value

    def validate_unique_user(self, attrs):
        username = attrs.get('username')
        email = attrs.get('email')
        if CustomUser.objects.filter(username=username, email=email).exists():
            return attrs
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
        return attrs


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
        if user.confirmation_code != attrs['confirmation_code']:
            raise serializers.ValidationError('Неверный код подтверждения.')
        return attrs


class ReviewSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(slug_field='username', read_only=True,
                              default=serializers.CurrentUserDefault())

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        read_only_fields = ('pub_date',)

    def validate(self, data):
        request = self.context.get('request')
        if request.method == 'POST':
            review = Review.objects.filter(
                title=self.context.get('view').kwargs.get('title_id'),
                author=self.context.get('request').user
            )
            if review.exists():
                raise serializers.ValidationError('Review already exists')
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(slug_field='username', read_only=True)
    # review = serializers.HiddenField(
    #    default=Review.objects.get(
    #        id=serializers.context['request'].query_params.get('review_id')))

    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ('pub_date', 'review')


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleReadSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(
        read_only=True,
        many=True
    )
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        fields = '__all__'
        model = Title


class TitleWriteSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True
    )

    class Meta:
        fields = '__all__'
        model = Title
