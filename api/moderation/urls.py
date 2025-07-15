from django.urls import path
from .views import (
    ReportListView,
    AssignReportView,
    ApproveReportView,
    DenyReportView,
    EditBookmarkView,
    EditVideoView,
    LookupBookmarkView,
    AuditLogListView,
)

urlpatterns = [
    path('reports/', ReportListView.as_view(), name='moderator-report-list'),
    path('assign/', AssignReportView.as_view(), name='moderator-assign-report'),
    path('approve/', ApproveReportView.as_view(), name='moderator-approve-report'),
    path('deny/', DenyReportView.as_view(), name='moderator-deny-report'),
    path('edit-bookmark/', EditBookmarkView.as_view(), name='moderator-edit-bookmark'),
    path('edit-video/', EditVideoView.as_view(), name='moderator-edit-video'),
    path('lookup-bookmark/<int:id>/', LookupBookmarkView.as_view(), name='moderator-lookup-bookmark'),
    path('audit-log/', AuditLogListView.as_view(), name='moderator-audit-log'),
]
