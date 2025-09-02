import uuid
from django.shortcuts import render


def _base_ctx(request):
    return {"incident_id": uuid.uuid4()}


def page_not_found(request, exception):
    """ 404 handler"""
    return render(request, "errors/404.html", _base_ctx(request), status=404)


def server_error(request):
    """ 500 handler"""
    return render(request, "errors/500.html", _base_ctx(request), status=500)


def permission_denied(request, exception):
    """ 403 handler"""
    return render(request, "errors/403.html", _base_ctx(request), status=403)


def bad_request(request, exception):
    """ 400 handler"""
    return render(request, "errors/400.html", _base_ctx(request), status=400)


def csrf_failure(request, reason=""):
    """ Custom CSRF failure handler """
    ctx = _base_ctx(request) | {"reason": reason}
    return render(request, "errors/403.html", ctx, status=403)
