from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from trip_packages.models import Trips


class HomeSitemap(Sitemap):
    priority = 1.0
    changefreq = "daily"

    def items(self):
        return ['home']

    def location(self, item):
        return reverse(item)


class MainTripPackagesSitemap(Sitemap):
    priority = 1.0
    changefreq = "daily"

    def items(self):
        return ['trip_packages']

    def location(self, item):
        return reverse(item)


class IndividualTripSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Trips.objects.all()

    def location(self, obj):
        return reverse('trip_details', args=[obj.pk])


class FilteredByCountrySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Trips.objects.values_list('location', flat=True).distinct()

    def location(self, country_code):
        return reverse('trip_packages') + f'?filter=on&location={country_code}'
