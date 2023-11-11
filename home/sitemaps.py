from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from trip_packages.models import Trips


class HomeSitemap(Sitemap):
    """
    Sitemap for the home page.
    """
    priority = 1.0
    changefreq = "daily"

    def items(self):
        return ['home']

    def location(self, item):
        return reverse(item)


class MainTripPackagesSitemap(Sitemap):
    """
    Sitemap for the main trip packages page.
    """
    priority = 1.0
    changefreq = "daily"

    def items(self):
        return ['trip_packages']

    def location(self, item):
        return reverse(item)


class IndividualTripSitemap(Sitemap):
    """
    Sitemap for individual trip detail pages.
    """
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Trips.objects.all()

    def location(self, obj):
        return reverse('trip_details', args=[obj.pk])


class FilteredByCountrySitemap(Sitemap):
    """
    Sitemap for pages displaying trips filtered by country.
    """
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Trips.objects.values_list('location', flat=True).distinct()

    def location(self, country_code):
        return reverse('trip_packages') + f'?filter=on&location={country_code}'
