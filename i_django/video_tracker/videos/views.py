from rest_framework import viewsets, status
from rest_framework.response import Response

from .serializers import (
    VideoWrapperSerializer,
    VideoListSerializer,
)
from .csv_manager import get_videos, add_video, delete_video, update_video


class VideoViewSet(viewsets.ViewSet):
    """
    API endpoint that allows videos to be viewed or edited.
    """

    def list(self, request):
        """
        Retrieve all videos from the tracker with optional sorting.

        Query Parameters:
        - sort_by: Field to sort by (name, post_date, or views_count)
        - order: Sort order (asc or desc)
        """
        # Extract query parameters
        sort_by = request.query_params.get("sort_by")
        order = request.query_params.get("order", "asc")

        # Get videos with sorting
        result = get_videos(sort_by=sort_by, order=order)
        serializer = VideoListSerializer(result)
        return Response(serializer.data)

    def create(self, request):
        """
        Add a new video to the tracker.

        This endpoint creates a new video entry in the system.
        """
        serializer = VideoWrapperSerializer(data=request.data)
        if serializer.is_valid():
            # Add video using CSV manager
            video_data = serializer.validated_data["video"]
            result = add_video(video_data)

            if result:
                return Response(
                    {"video": video_data}, status=status.HTTP_201_CREATED
                )
            else:
                message = f"Video with ID {video_data['id']} already exists"
                return Response(
                    {"message": message},
                    status=status.HTTP_409_CONFLICT,
                )
        else:
            return Response(
                {"message": f"Error adding video: {serializer.errors}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def retrieve(self, request, pk=None):
        """
        Not implemented - would retrieve a specific video
        """
        return Response(
            {"message": "Not implemented"},
            status=status.HTTP_501_NOT_IMPLEMENTED
        )

    def update(self, request, pk=None):
        """
        Update a video's information by its ID.

        This endpoint updates an existing video in the system.
        """
        try:
            serializer = VideoWrapperSerializer(data=request.data)
            if serializer.is_valid():
                video_data = serializer.validated_data["video"]
                success, updated_video = update_video(int(pk), video_data)

                if success and updated_video:
                    return Response({"video": updated_video})
                else:
                    return Response(
                        {"message": f"Video with ID {pk} not found"},
                        status=status.HTTP_404_NOT_FOUND,
                    )
            else:
                return Response(
                    {"message": f"Error updating video: {serializer.errors}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as e:
            return Response(
                {"message": f"Error updating video: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def destroy(self, request, pk=None):
        """
        Delete a video by its ID.

        This endpoint removes a video from the system.
        """
        try:
            result = delete_video(int(pk))

            if result:
                return Response(
                    {"message": f"Video with ID {pk} deleted successfully"},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"message": f"Video with ID {pk} not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        except Exception as e:
            return Response(
                {"message": f"Error deleting video: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )