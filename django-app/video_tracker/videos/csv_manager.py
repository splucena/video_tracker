import os
import csv
from typing import Optional, Dict, Tuple
from django.conf import settings


def _get_csv_path() -> str:
    """Get the path to the videos CSV file"""
    # Ensure the data directory exists
    os.makedirs(settings.DATA_DIR, exist_ok=True)
    return os.path.join(settings.DATA_DIR, "videos.csv")


def _file_exists(csv_path: str) -> bool:
    """Check if the CSV file exists and has content"""
    return os.path.exists(csv_path) and os.path.getsize(csv_path) > 0


def get_videos(sort_by=None, order="asc"):
    """Get videos with optional sorting"""
    try:
        csv_path = _get_csv_path()

        if not _file_exists(csv_path):
            return {"videos": []}

        videos = []
        with open(csv_path, "r", newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    if "views_count" in row:
                        row["views_count"] = int(row["views_count"])

                    # Convert to proper structure
                    video = {
                        "id": int(row["id"]),
                        "name": row["name"],
                        "href": row["href"],
                        "post_date": row["post_date"],
                        "views_count": int(row["views_count"]),
                    }
                    videos.append(video)
                except (ValueError, KeyError) as e:
                    print(f"Skipping invalid row: {row}. Error: {e}")

        if sort_by in ["name", "post_date", "views_count"]:

            def sort_key(video):
                if sort_by == "views_count":
                    return int(video[sort_by])
                elif sort_by == "post_date":
                    return video[sort_by]
                else:
                    return video[sort_by].lower()

            videos.sort(key=sort_key, reverse=(order.lower() == "desc"))

        return {"videos": videos}

    except Exception as e:
        print(f"Error retrieving videos: {str(e)}")
        return {"videos": []}


def delete_video(id: int) -> bool:
    """Delete a video with the specified ID"""
    try:
        csv_path = _get_csv_path()

        if not _file_exists(csv_path):
            return False

        videos_to_keep = []
        found = False

        with open(csv_path, "r", newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            fieldnames = reader.fieldnames

            for row in reader:
                if row.get("id") == str(id):
                    found = True
                else:
                    videos_to_keep.append(row)

        if not found:
            return False

        with open(csv_path, "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(videos_to_keep)
            return True

    except Exception as e:
        error = f"Error deleting video with id {id}"
        print(f"{error}: {str(e)}")
        return False


def update_video(
        id: int,
        updated_video_data: Dict,
) -> Tuple[bool, Optional[Dict]]:
    """Update a video with the specified ID"""
    try:
        csv_path = _get_csv_path()

        if not _file_exists(csv_path):
            return False, None

        updated_rows = []
        found = False
        updated_row = None

        with open(csv_path, "r", newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            fieldnames = reader.fieldnames

            for row in reader:
                if row.get("id") == str(id):
                    found = True
                    updated_row = {
                        "id": str(id),
                        "name": updated_video_data.get("name"),
                        "href": updated_video_data.get("href"),
                        "post_date": updated_video_data.get("post_date"),
                        "views_count": str(
                            updated_video_data.get("views_count")
                        ),
                    }
                    updated_rows.append(updated_row)
                else:
                    updated_rows.append(row)

        if not found:
            return False, None

        with open(csv_path, "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(updated_rows)

        # Return with proper types
        return True, {
            "id": int(updated_row["id"]),
            "name": updated_row["name"],
            "href": updated_row["href"],
            "post_date": updated_row["post_date"],
            "views_count": int(updated_row["views_count"]),
        }

    except Exception as e:
        error = f"Error updating video with id {id}"
        print(f"{error}: {str(e)}")
        return False, None


def add_video(video_data: Dict) -> bool:
    """Add a new video to the CSV file"""
    try:
        csv_path = _get_csv_path()
        fieldnames = ["id", "name", "href", "post_date", "views_count"]

        file_exists = _file_exists(csv_path)

        # Prepare the data for CSV
        video_dict = {
            "id": str(video_data.get("id")),
            "name": video_data.get("name"),
            "href": video_data.get("href"),
            "post_date": video_data.get("post_date"),
            "views_count": str(video_data.get("views_count")),
        }

        if file_exists:
            # Check for duplicates
            with open(csv_path, "r", newline="") as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if row.get("id") == video_dict["id"]:
                        return False

        if not file_exists:
            # Create a new file with header
            with open(csv_path, "w", newline="") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerow(video_dict)
        else:
            # Append to existing file
            with open(csv_path, "a", newline="") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writerow(video_dict)

        return True

    except Exception as e:
        print(f"Error adding video: {str(e)}")
        return False
