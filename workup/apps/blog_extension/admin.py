from django.contrib import admin
from .models import BlogImage


class BlogImageAdmin(admin.ModelAdmin):
    list_display = ('image', 'user', 'admin_thumb', 'status')
admin.site.register(BlogImage, BlogImageAdmin)
