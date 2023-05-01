from rest_framework import serializers

from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueTogetherValidator
from django.db.models import Avg

from reviews.models import Review, Comment, Title
from reviews.models import Category, Genre, Title


class ReviewSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(slug_field='username', read_only=True,
                              default=serializers.CurrentUserDefault())
    title = serializers.HiddenField(
        default=Title.objects.get(
            id=serializers.context['request'].query_params.get('title_id')))

    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ('pub_date',)
        validators = [
            UniqueTogetherValidator(
                queryset=Review.objects.all(),
                fields=('author', 'title')
            )
        ]


class CommentSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(slug_field='username', read_only=True)
    review = serializers.HiddenField(
        default=Review.objects.get(
            id=serializers.context['request'].query_params.get('review_id')))

    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ('pub_date',)


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
