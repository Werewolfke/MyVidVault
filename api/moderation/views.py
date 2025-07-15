from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import ModeratorAssignment, ModeratorAuditLog
from operations.models import Report, Video
from users.models import Bookmark
from .serializers import (
    ReportSerializer,
    ModeratorAssignmentSerializer,
    ModeratorAuditLogSerializer,
    VideoSerializer,
    BookmarkSerializer,
)
from .permissions import IsModerator

class ReportListView(generics.ListAPIView):
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated, IsModerator]

    def get_queryset(self):
        # Only unresolved reports
        return Report.objects.filter(is_resolved=False).order_by('-created_at')

class AssignReportView(generics.UpdateAPIView):
    queryset = ModeratorAssignment.objects.all()
    serializer_class = ModeratorAssignmentSerializer
    permission_classes = [IsAuthenticated, IsModerator]

    def update(self, request, *args, **kwargs):
        report_id = request.data.get('report_id')
        if not report_id:
            return Response({'error': 'report_id required'}, status=status.HTTP_400_BAD_REQUEST)
        report = Report.objects.get(id=report_id)
        assignment, created = ModeratorAssignment.objects.get_or_create(report=report)
        assignment.moderator = request.user
        assignment.save()
        ModeratorAuditLog.objects.create(
            moderator=request.user,
            action='assign_report',
            report=report,
            details=f'Assigned report {report_id} to {request.user.username}'
        )
        return Response(ModeratorAssignmentSerializer(assignment).data)

class ApproveReportView(generics.UpdateAPIView):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated, IsModerator]

    def update(self, request, *args, **kwargs):
        report_id = request.data.get('report_id')
        report = Report.objects.get(id=report_id)
        report.is_resolved = True
        report.resolved_at = timezone.now()
        report.save(update_fields=['is_resolved', 'resolved_at'])
        ModeratorAuditLog.objects.create(
            moderator=request.user,
            action='approve_report',
            report=report,
            details=f'Approved report {report_id}'
        )
        return Response(ReportSerializer(report).data)

class DenyReportView(generics.UpdateAPIView):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated, IsModerator]

    def update(self, request, *args, **kwargs):
        report_id = request.data.get('report_id')
        report = Report.objects.get(id=report_id)
        report.is_resolved = True
        report.resolved_at = timezone.now()
        report.save(update_fields=['is_resolved', 'resolved_at'])
        ModeratorAuditLog.objects.create(
            moderator=request.user,
            action='deny_report',
            report=report,
            details=f'Denied report {report_id}'
        )
        return Response(ReportSerializer(report).data)

class EditBookmarkView(generics.UpdateAPIView):
    queryset = Bookmark.objects.all()
    serializer_class = BookmarkSerializer
    permission_classes = [IsAuthenticated, IsModerator]

    def update(self, request, *args, **kwargs):
        bookmark_id = request.data.get('bookmark_id')
        bookmark = Bookmark.objects.get(id=bookmark_id)
        for field, value in request.data.items():
            if hasattr(bookmark, field):
                setattr(bookmark, field, value)
        bookmark.save()
        ModeratorAuditLog.objects.create(
            moderator=request.user,
            action='edit_bookmark',
            bookmark=bookmark,
            details=f'Edited bookmark {bookmark_id}: {request.data}'
        )
        return Response(BookmarkSerializer(bookmark).data)

class EditVideoView(generics.UpdateAPIView):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    permission_classes = [IsAuthenticated, IsModerator]

    def update(self, request, *args, **kwargs):
        video_id = request.data.get('video_id')
        video = Video.objects.get(id=video_id)
        for field, value in request.data.items():
            if hasattr(video, field):
                setattr(video, field, value)
        video.save()
        ModeratorAuditLog.objects.create(
            moderator=request.user,
            action='edit_video',
            video=video,
            details=f'Edited video {video_id}: {request.data}'
        )
        return Response(VideoSerializer(video).data)

class LookupBookmarkView(generics.RetrieveAPIView):
    queryset = Bookmark.objects.all()
    serializer_class = BookmarkSerializer
    permission_classes = [IsAuthenticated, IsModerator]
    lookup_field = 'id'

class AuditLogListView(generics.ListAPIView):
    queryset = ModeratorAuditLog.objects.all().order_by('-created_at')
    serializer_class = ModeratorAuditLogSerializer
    from rest_framework.permissions import IsAdminUser
    permission_classes = [IsAuthenticated, IsAdminUser]
