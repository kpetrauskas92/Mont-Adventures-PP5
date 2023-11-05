from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.views.static import serve
from home.sitemaps import (HomeSitemap,
                           MainTripPackagesSitemap,
                           IndividualTripSitemap,
                           FilteredByCountrySitemap
                           )

sitemaps = {
    'home': HomeSitemap,
    'main_trip_packages': MainTripPackagesSitemap,
    'individual_trips': IndividualTripSitemap,
    'filtered_by_country': FilteredByCountrySitemap
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('accounts/', include('profiles.urls')),
    path('', include('home.urls')),
    path('', include('trip_packages.urls')),
    path('cart/', include('cart.urls')),
    path('checkout/', include('checkout.urls')),
    path('', include('profiles.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps},
         name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', serve, {
        'path': 'robots.txt',
        'document_root': settings.STATIC_ROOT,
    }),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)

handler404 = 'home.views.error_404'
handler500 = 'home.views.error_500'
