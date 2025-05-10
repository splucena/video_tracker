from flask_openapi3 import OpenAPI, Info
from http import HTTPStatus

from models import (
    Videos,
    MessageResponse,
    VideoWrapper,
    VideosSortParams,
    VideoIdParam,
)
from data_manager import get_videos, add_video, delete_video, update_video

# Initialize Flask with OpenAPI
info = Info(title="Video Tracker API", version="1.0.0")
app = OpenAPI(__name__, info=info)


# === API Routes ===
@app.post(
    "/videos/",
    responses={
        HTTPStatus.CREATED: VideoWrapper,
        HTTPStatus.BAD_REQUEST: MessageResponse,
        HTTPStatus.CONFLICT: MessageResponse,
    },
)
def add(body: VideoWrapper):
    """
    Add a new video to the tracker.

    This endpoint creates a new video entry in the system based on the provided
    video data. It checks for duplicate IDs before adding.

    Args:
        body (VideoRequest): The request body containing the video data

    Returns:
        tuple: A response containing either:
            - The created video and a 201 CREATED status
            - An error message and a 409 CONFLICT status for duplicate IDs
            - An error message and a 400 BAD REQUEST status for invalid data
    """
    try:
        result = add_video(body.video)

        if result:
            return {"video": body.video.model_dump()}, HTTPStatus.CREATED
        else:
            return {
                "message": f"Video with ID {body.video.id} already exists"
            }, HTTPStatus.CONFLICT

    except Exception as e:
        return (
            {"message": f"Error adding video: {str(e)}"},
            HTTPStatus.BAD_REQUEST,
        )


@app.delete(
    "/videos/<int:id>",
    responses={
        HTTPStatus.OK: MessageResponse,
        HTTPStatus.NOT_FOUND: MessageResponse,
    },
)
def delete(path: VideoIdParam):
    """
    Delete a video by its ID.

    This endpoint removes a video from the system based on the provided ID.

    Args:
        path (VideoIdParam): Object containing the ID path parameter

    Returns:
        tuple: A response containing either:
            - A success message and a 200 OK status
            - An error message and a 404 NOT FOUND status if the video
              doesn't exist
    """
    video_id = path.id
    result = delete_video(video_id)
    message = f"Video with ID {video_id}"
    if result:
        return {"message": f"{message} deleted successfully"}, HTTPStatus.OK
    else:
        return {"message": f"{message} not found"}, HTTPStatus.NOT_FOUND


@app.put(
    "/videos/<int:id>/",
    responses={
        HTTPStatus.OK: VideoWrapper,
        HTTPStatus.NOT_FOUND: MessageResponse,
    },
)
def patch(path: VideoIdParam, body: VideoWrapper):
    """
    Update a video's information by its ID.

    This endpoint updates an existing video in the system based on the provided
    ID and video data. It verifies the video exists before updating it.

    Args:
        path (VideoIdParam): Object containing the ID path parameter
        body (VideoWrapper): The request body containing the updated video data

    Returns:
        tuple: A response containing either:
            - The updated video and a 200 OK status
            - An error message and a 404 NOT FOUND status if the video doesn't
              exist
            - An error message and a 400 BAD REQUEST status for invalid data
    """
    try:
        video_id = path.id
        success, updated_video = update_video(video_id, body.video)

        if success and updated_video:
            return {"video": updated_video}, HTTPStatus.OK
        else:
            message = f"Video with ID {video_id} not found"
            return {"message": message}, HTTPStatus.NOT_FOUND

    except Exception as e:
        error_message = f"Error updating video: {str(e)}"
        print(error_message)
        return {"message": error_message}, HTTPStatus.BAD_REQUEST


@app.get("/videos/", responses={HTTPStatus.OK: Videos})
def videos(query: VideosSortParams):
    """
    Retrieve all videos from the tracker with optional sorting.

    This endpoint returns a list of all videos in the system.
    Results can be sorted based on the provided query parameters.

    Args:
        query (VideosSortParams): Object containing query parameters
            - sort_by: Field to sort by (name, post_date, or views_count)
            - order: Sort order (asc or desc)

    Returns:
        dict: A dictionary containing the list of videos, potentially sorted
              according to the provided parameters
    """
    sort_by = query.sort_by if query.sort_by else None
    order = query.order if query.order else "asc"

    return get_videos(sort_by=sort_by, order=order)
