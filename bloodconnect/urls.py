from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('eligibility/', views.eligibility_checker, name='eligibility_checker'),
    path('blood-types/', views.blood_type_education, name='blood_type_education'),
    path('accounts/', include('accounts.urls')),
    path('donors/', include('donors.urls')),
    path('requests/', include('requests.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
