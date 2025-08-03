from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static
from CommissionZero import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('CommissionZeroApp.urls')),
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

