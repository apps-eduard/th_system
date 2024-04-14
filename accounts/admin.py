from django.contrib import admin
from .models import User  # Import your custom user model

# Register your models here.
admin.site.register(User)
