from fastapi import FastAPI, HTTPException, Path
from fastapi.responses import JSONResponse
from typing import Literal, Optional

from models import VideoWrapper, Videos, MessageResponse
from csv_manager import get_videos, add_video, delete_video, update_video

app = FastAPI(
    title="Video Tracker API",
    description="A simple API for tracking videos",
    version="1.0.0",
)


@app.get("/videos/", response_model=Videos, tags=["videos"])
async def list_videos(
    sort_by: Optional[Literal["name", "post_date", "views_count"]] = None,
    order: Optional[Literal["asc", "desc"]] = "asc",
):
    """
    Retrieve all videos from the tracker with optional sorting.

    - **sort_by**: Field to sort by (name, post_date, or views_count)
    - **order**: Sort order (asc or desc)
    """
    return get_videos(sort_by=sort_by, order=order)


@app.post(
    "/videos/",
    response_model=VideoWrapper,
    status_code=201,
    tags=["videos"],
    responses={409: {"model": MessageResponse}},
)
async def create_video(video_data: VideoWrapper):
    """
    Add a new video to the tracker.

    This endpoint creates a new video entry in the system based on the provided
    video data. It checks for duplicate IDs before adding.
    """
    result = add_video(video_data.video.dict())

    if result:
        return {"video": video_data.video}
    else:
        message = f"Video with ID {video_data.video.id} already exists"
        return JSONResponse(
            status_code=409,
            content={"message": message},
        )


@app.put(
    "/videos/{id}/",
    response_model=VideoWrapper,
    tags=["videos"],
    responses={404: {"model": MessageResponse}},
)
async def update_video_by_id(
    id: int = Path(..., description="The ID of the video to update"),
    video_data: VideoWrapper = None,
):
    """
    Update a video's information by its ID.

    This endpoint updates an existing video in the system based on the provided
    ID and video data. It verifies the video exists before updating it.
    """
    success, updated_video = update_video(id, video_data.video.dict())

    if success and updated_video:
        return {"video": updated_video}
    else:
        raise HTTPException(
            status_code=404, detail=f"Video with ID {id} not found"
        )


@app.delete(
    "/videos/{id}",
    response_model=MessageResponse,
    tags=["videos"],
    responses={404: {"model": MessageResponse}},
)
async def delete_video_by_id(
    id: int = Path(..., description="The ID of the video to delete")
):
    """
    Delete a video by its ID.

    This endpoint removes a video from the system based on the provided ID.
    """
    result = delete_video(id)

    if result:
        return {"message": f"Video with ID {id} deleted successfully"}
    else:
        raise HTTPException(
            status_code=404, detail=f"Video with ID {id} not found"
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
