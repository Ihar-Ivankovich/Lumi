from django.contrib import admin
from .models import Post, Comment, RecipeReaction

admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(RecipeReaction)

