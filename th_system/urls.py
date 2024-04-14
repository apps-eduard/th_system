# urls.py

from django.contrib import admin
from django.urls import path, include
from accounts.views import login_view


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', login_view, name='login'),
    path('', include('accounts.urls', namespace='accounts')),  # Include the 'accounts' app URLs with namespace
    path('monitoring/', include('monitoring.urls', namespace='monitoring')),
]

