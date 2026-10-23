from rest_framework.permissions import SAFE_METHODS, BasePermission

from .services import context_for_request


class IsActiveStaff(BasePermission):
    """Any active employee may log a concern and look a student up."""

    message = "Safeguarding: an active staff account is required."

    def has_permission(self, request, view):
        return context_for_request(request).is_staff


class IsSafeguardingTeam(BasePermission):
    message = "Safeguarding: DSL or deputy role required."

    def has_permission(self, request, view):
        ctx = context_for_request(request)
        return ctx.is_staff and ctx.is_team


class IsDSL(BasePermission):
    message = "Safeguarding: DSL role required."

    def has_permission(self, request, view):
        ctx = context_for_request(request)
        return ctx.is_staff and ctx.is_dsl


class IsDSLOrReadOnly(BasePermission):
    """Configuration lists are readable by all staff (the form needs them); only DSLs change them."""

    def has_permission(self, request, view):
        ctx = context_for_request(request)
        if not ctx.is_staff:
            return False
        return request.method in SAFE_METHODS or ctx.is_dsl
