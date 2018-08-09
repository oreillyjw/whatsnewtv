from django.contrib import admin
from .models import Comment, MovieDBInfo,Favorites, Tags

# Register your models here.
admin.site.register(Comment)
admin.site.register(MovieDBInfo)
admin.site.register(Favorites)
admin.site.register(Tags)
