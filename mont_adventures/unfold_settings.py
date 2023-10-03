from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
# Supported icon set: https://fonts.google.com/icons

UNFOLD = {
    "SITE_TITLE": "Mont Adventures",
    "SITE_HEADER": "Content Management System",
    "SITE_URL": "/",
    "SITE_ICON": lambda request: static("web_elements/logo/logo-white.webp"),
    "SITE_SYMBOL": "altitude",

    # "COLORS": {
    #     "primary": {
    #         "50": "250 245 255",
    #         "100": "243 232 255",
    #         "200": "233 213 255",
    #         "300": "216 180 254",
    #         "400": "192 132 252",
    #         "500": "168 85 247",
    #         "600": "147 51 234",
    #         "700": "126 34 206",
    #         "800": "107 33 168",
    #         "900": "88 28 135",
    #     },
    # },

    "SIDEBAR": {
        "show_search": False,
        "show_all_applications": False,
        "badge": "sample_app.badge_callback",
        "navigation": [
            {
                "title": _("Navigation"),
                "separator": True,  # Top border
                "items": [
                    {
                        "title": _("Dashboard"),
                        "icon": "dashboard",
                        "link": reverse_lazy("admin:index"),
                        "permission":
                        lambda request: request.user.is_superuser,
                    },
                    {
                        "title": _("Customers"),
                        "icon": "people",
                        "link": reverse_lazy(
                            "admin:profiles_userprofile_changelist"),
                    },
                    {
                        "title": _("Orders"),
                        "icon": "package",
                        "link": reverse_lazy(
                            "admin:checkout_order_changelist"),
                    },
                    {
                        "title": _("Trip Packages"),
                        "icon": "hiking",
                        "link": reverse_lazy(
                            "admin:trip_packages_trips_changelist"),
                    },
                    {
                        "title": _("Available Dates"),
                        "icon": "date_range",
                        "link": reverse_lazy(
                            "admin:trip_packages_availabledate_changelist"),
                    },
                ],
            },
        ],
    },
}


def badge_callback(request):
    return 3
