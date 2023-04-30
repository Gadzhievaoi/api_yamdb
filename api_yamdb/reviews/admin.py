from django.contrib import admin
from reviews.models import CustomUser
# from reviews.models import (Category, Comment, Genre, GenreTitle,
#                            Review, Title, CustomUser)


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', )
    list_editable = ('role', )
    search_fields = ('username',)


admin.site.register(CustomUser, UserAdmin)
# admin.site.register(Category)
# admin.site.register(Comment)
# admin.site.register(Genre)
# admin.site.register(GenreTitle)
# admin.site.register(Review)
# admin.site.register(Title)
