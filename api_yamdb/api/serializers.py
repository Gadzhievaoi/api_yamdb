from rest_framework import serializers, validators
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueTogetherValidator
from django.shortcuts import get_object_or_404
from django.db.models import Avg

from reviews.models import Category, Comment, CustomUser, Genre, Review, Title


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


class ReviewSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(slug_field='username', read_only=True,
                              default=serializers.CurrentUserDefault())
    # title = serializers.HiddenField(
    #    default=Title.objects.get(
    #        id=serializers.context['request'].query_params.get('title_id')))

    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ('pub_date', 'title')
        validators = [
            UniqueTogetherValidator(
                queryset=Review.objects.all(),
                fields=('author', 'title')
            )
        ]


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


class TitleSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field='slug', many=False, queryset=Category.objects.all()
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        many=True,
        required=False,
        queryset=Genre.objects.all()
    )
    rating = serializers.IntegerField(read_only=True)

    def get_rating(self, obj):
        return round(obj.reviews.aggregate(Avg("score")))

    class Meta:
        model = Title
        fields = '__all__'
