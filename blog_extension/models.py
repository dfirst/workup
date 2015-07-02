from django.db import models
from mezzanine.utils.models import upload_to
from mezzanine.core.models import Ownable
from mezzanine.utils.models import AdminThumbMixin

class BlogImage(Ownable, AdminThumbMixin):
    image = models.ImageField(upload_to=upload_to("blog.BlogPost.featured_image", "uploads/blog"))
    admin_thumb_field = "image"