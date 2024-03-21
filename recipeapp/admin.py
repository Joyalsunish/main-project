from django.contrib import admin

# Register your models here.

from .models import Profile,Recipe,Comment
admin.site.register(Profile)
admin.site.register(Recipe)
admin.site.register(Comment)
