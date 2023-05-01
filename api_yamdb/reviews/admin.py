from django.contrib import admin

from reviews.models import CustomUser, Category, Genre, Title
# from reviews.models import (Category, Comment, Genre, Title,
#                            Review, CustomUser)


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', )
    list_editable = ('role', )
    search_fields = ('username',)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ("pk", "name", "slug")


class GenreAdmin(admin.ModelAdmin):
    list_display = ("pk", "name", "slug")


class GenreTitleAdmin(admin.ModelAdmin):
    list_display = ("pk", "name", "year", "description", "category")


admin.site.register(CustomUser, UserAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Title, GenreTitleAdmin)
