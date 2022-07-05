
from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic import RedirectView
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='api/')),
    path('api/', include('picstore.api.urls', namespace="picstore")),
    path('api-auth/', include('rest_framework.urls')),


]
