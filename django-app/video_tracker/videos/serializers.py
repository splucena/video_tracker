from rest_framework import serializers
from datetime import datetime
import re


class Video:
    """Class representing a video"""

    def __init__(self, id, name, href, post_date, views_count):
        self.id = id
        self.name = name
        self.href = href
        self.post_date = post_date
        self.views_count = views_count


class VideoSerializer(serializers.Serializer):
    """Serializer for a video object"""

    id = serializers.IntegerField()
    name = serializers.CharField()
    href = serializers.CharField()
    post_date = serializers.CharField()
    views_count = serializers.IntegerField()

    def validate_post_date(self, value):
        """Ensure post_date is in YYYY-MM-DD format"""
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", value):
            raise serializers.ValidationError(
                "post_date must be a valid date in YYYY-MM-DD format"
            )

        try:
            datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            raise serializers.ValidationError(
                "post_date must be a valid date in YYYY-MM-DD format"
            )

        return value


class VideoWrapperSerializer(serializers.Serializer):
    """Container for a single video object, used in requests and responses"""

    video = VideoSerializer()


class MessageResponseSerializer(serializers.Serializer):
    """Response containing a simple message string"""

    message = serializers.CharField()


class VideoListSerializer(serializers.Serializer):
    """Serializer for multiple videos response"""

    videos = VideoSerializer(many=True)
