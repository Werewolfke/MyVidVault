from rest_framework import serializers
from .models import ModeratorAssignment, ModeratorAuditLog
from operations.models import Report, Video
from users.models import Bookmark

class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = '__all__'

class ModeratorAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModeratorAssignment
        fields = '__all__'

class ModeratorAuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModeratorAuditLog
        fields = '__all__'

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = '__all__'

class BookmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bookmark
        fields = '__all__'
