from django.conf import settings


class SafeguardingNoStoreMiddleware:
    """Stops browsers and proxies caching safeguarding responses."""

    def __init__(self, get_response):
        self.get_response = get_response
        self.prefix = getattr(settings, "SG_API_PREFIX", "/api/v1/safeguarding/")

    def __call__(self, request):
        response = self.get_response(request)
        if request.path.startswith(self.prefix):
            response["Cache-Control"] = "no-store, private"
            response["Pragma"] = "no-cache"
            response["X-Content-Type-Options"] = "nosniff"
        return response
