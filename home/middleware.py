from django.shortcuts import redirect


class BlockDirectAccessMiddleware:
    """
    Middleware to block direct access to specific paths
    unless they are HTMX requests.

    This middleware checks if the incoming request is for certain defined paths
    and redirects to the home page if the request is not made via HTMX.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Process the view before actually calling the view function.
        """
        blocked_paths = ['/accounts/login/',
                         '/accounts/signup/',
                         '/accounts/email/']

        # Check if the request is an HTMX request
        is_htmx = request.META.get('HTTP_HX_REQUEST', False)

        if request.path in blocked_paths and not is_htmx:
            return redirect('/')
