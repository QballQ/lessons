"""Mount in the project urls:  path("api/v1/safeguarding/", include("safeguarding.urls"))"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "safeguarding"

router = DefaultRouter()
router.register("incidents", views.IncidentViewSet, basename="incident")
router.register("categories", views.CategoryViewSet, basename="category")
router.register("locations", views.LocationViewSet, basename="location")
router.register("time-bands", views.TimeBandViewSet, basename="timeband")
router.register("alert-groups", views.AlertGroupViewSet, basename="alertgroup")
router.register("roles", views.RoleAssignmentViewSet, basename="role")

urlpatterns = [
    path("me/", views.MeView.as_view(), name="me"),
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
    path("students/lookup/", views.StudentLookupView.as_view(), name="student-lookup"),
    path("context/", views.ContextView.as_view(), name="context"),
    path("alerts/mine/", views.MyAlertsView.as_view(), name="my-alerts"),
    path("attachments/<int:pk>/download/", views.AttachmentDownloadView.as_view(), name="attachment-download"),
    path("", include(router.urls)),
]
