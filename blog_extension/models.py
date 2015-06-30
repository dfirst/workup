from django.db import models
from mezzanine.utils.models import upload_to


class BlogImage(models.Model):
    image = models.ImageField(upload_to=upload_to("blog.BlogPost.featured_image", "uploads/blog"))