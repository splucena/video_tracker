import os
import csv
import json
import shutil
from tempfile import mkdtemp
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from videos.csv_manager import (
    _get_csv_path,
    get_videos,
    add_video,
    delete_video,
    update_video,
)

# Create a temporary directory for test data
TEST_DATA_DIR = mkdtemp()


@override_settings(DATA_DIR=TEST_DATA_DIR)
class VideoAPITestCase(TestCase):
    """Test the Video API endpoints"""

    def setUp(self):
        """Setup for each test"""
        self.client = APIClient()
        self.videos_url = reverse("video-list")
        self.csv_path = _get_csv_path()

        # Sample video data
        self.video_data = {
            "video": {
                "id": 1,
                "name": "Test Video",
                "href": "http://example.com/test",
                "post_date": "2025-01-01",
                "views_count": 100,
            }
        }

        # Ensure test directory exists
        os.makedirs(TEST_DATA_DIR, exist_ok=True)

        # Create a test CSV file with headers
        with open(self.csv_path, "w", newline="") as csvfile:
            writer = csv.DictWriter(
                csvfile, fieldnames=["id", "name", "href", "post_date", "views_count"]
            )
            writer.writeheader()

    def tearDown(self):
        """Cleanup after each test"""
        # Remove test CSV file if it exists
        if os.path.exists(self.csv_path):
            os.remove(self.csv_path)

    @classmethod
    def tearDownClass(cls):
        """Cleanup after all tests"""
        # Remove the temporary directory
        shutil.rmtree(TEST_DATA_DIR)
        super().tearDownClass()

    # Test API endpoints
    def test_get_empty_videos_list(self):
        """Test getting an empty list of videos"""
        response = self.client.get(self.videos_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"videos": []})

    def test_create_video(self):
        """Test creating a new video"""
        response = self.client.post(
            self.videos_url,
            data=json.dumps(self.video_data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["video"]["name"], "Test Video")

        # Verify it was added to the CSV
        with open(self.csv_path, "r", newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            rows = list(reader)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["name"], "Test Video")

    def test_duplicate_video(self):
        """Test adding a duplicate video (same ID)"""
        # Add a video first
        add_video(self.video_data["video"])

        # Try to add the same video again
        response = self.client.post(
            self.videos_url,
            data=json.dumps(self.video_data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertIn("already exists", response.data["message"])

    def test_get_videos_list(self):
        """Test getting a list of videos"""
        # Add test videos
        add_video(
            {
                "id": 1,
                "name": "Test Video 1",
                "href": "http://example.com/1",
                "post_date": "2025-01-01",
                "views_count": 100,
            }
        )
        add_video(
            {
                "id": 2,
                "name": "Test Video 2",
                "href": "http://example.com/2",
                "post_date": "2025-01-02",
                "views_count": 200,
            }
        )

        response = self.client.get(self.videos_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["videos"]), 2)

    def test_update_video(self):
        """Test updating a video"""
        # Add a video first
        add_video(self.video_data["video"])

        # Update data
        updated_data = {
            "video": {
                "id": 1,
                "name": "Updated Video",
                "href": "http://example.com/updated",
                "post_date": "2025-02-01",
                "views_count": 200,
            }
        }

        response = self.client.put(
            f"{self.videos_url}1/",
            data=json.dumps(updated_data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["video"]["name"], "Updated Video")

        # Verify it was updated in the CSV
        with open(self.csv_path, "r", newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            rows = list(reader)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["name"], "Updated Video")

    def test_update_nonexistent_video(self):
        """Test updating a video that doesn't exist"""
        response = self.client.put(
            f"{self.videos_url}999/",
            data=json.dumps(self.video_data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_video(self):
        """Test deleting a video"""
        # Add a video first
        add_video(self.video_data["video"])

        response = self.client.delete(f"{self.videos_url}1/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify it was deleted from the CSV
        with open(self.csv_path, "r", newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            rows = list(reader)
            self.assertEqual(len(rows), 0)

    def test_delete_nonexistent_video(self):
        """Test deleting a video that doesn't exist"""
        response = self.client.delete(f"{self.videos_url}999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_videos_sorting(self):
        """Test getting videos with sorting"""
        # Add test videos
        add_video(
            {
                "id": 1,
                "name": "B Test Video",
                "href": "http://example.com/1",
                "post_date": "2025-01-02",
                "views_count": 100,
            }
        )
        add_video(
            {
                "id": 2,
                "name": "A Test Video",
                "href": "http://example.com/2",
                "post_date": "2025-01-01",
                "views_count": 200,
            }
        )

        # Test sort by name ascending
        response = self.client.get(f"{self.videos_url}?sort_by=name&order=asc")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["videos"][0]["name"], "A Test Video")

        # Test sort by name descending
        response = self.client.get(f"{self.videos_url}?sort_by=name&order=desc")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["videos"][0]["name"], "B Test Video")

        # Test sort by views_count ascending
        response = self.client.get(f"{self.videos_url}?sort_by=views_count&order=asc")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["videos"][0]["views_count"], 100)

        # Test sort by post_date descending
        response = self.client.get(f"{self.videos_url}?sort_by=post_date&order=desc")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["videos"][0]["post_date"], "2025-01-02")

    def test_invalid_video_data(self):
        """Test submitting invalid video data"""
        invalid_data = {
            "video": {
                "id": 1,
                "name": "Test Video",
                "href": "http://example.com/test",
                "post_date": "invalid-date",  # Invalid date format
                "views_count": 100,
            }
        }

        response = self.client.post(
            self.videos_url,
            data=json.dumps(invalid_data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


# Test CSV manager functions directly
@override_settings(DATA_DIR=TEST_DATA_DIR)
class CSVManagerTestCase(TestCase):
    """Test the CSV manager functions"""

    def setUp(self):
        """Setup for each test"""
        self.csv_path = _get_csv_path()

        # Ensure test directory exists
        os.makedirs(TEST_DATA_DIR, exist_ok=True)

        # Create a test CSV file with headers
        with open(self.csv_path, "w", newline="") as csvfile:
            writer = csv.DictWriter(
                csvfile, fieldnames=["id", "name", "href", "post_date", "views_count"]
            )
            writer.writeheader()

    def tearDown(self):
        """Cleanup after each test"""
        # Remove test CSV file if it exists
        if os.path.exists(self.csv_path):
            os.remove(self.csv_path)

    @classmethod
    def tearDownClass(cls):
        """Cleanup after all tests"""
        # Remove the temporary directory
        shutil.rmtree(TEST_DATA_DIR)
        super().tearDownClass()

    def test_get_empty_videos(self):
        """Test getting videos from an empty CSV"""
        result = get_videos()
        self.assertEqual(result, {"videos": []})

    def test_add_video(self):
        """Test adding a video to the CSV"""
        video_data = {
            "id": 1,
            "name": "Test Video",
            "href": "http://example.com/test",
            "post_date": "2025-01-01",
            "views_count": 100,
        }

        result = add_video(video_data)
        self.assertTrue(result)

        # Verify it was added
        result = get_videos()
        self.assertEqual(len(result["videos"]), 1)
        self.assertEqual(result["videos"][0]["name"], "Test Video")

    def test_update_video(self):
        """Test updating a video in the CSV"""
        # Add a video first
        original_video = {
            "id": 1,
            "name": "Original Video",
            "href": "http://example.com/original",
            "post_date": "2025-01-01",
            "views_count": 100,
        }
        add_video(original_video)

        # Update the video
        updated_video = {
            "id": 1,
            "name": "Updated Video",
            "href": "http://example.com/updated",
            "post_date": "2025-02-01",
            "views_count": 200,
        }

        success, result = update_video(1, updated_video)
        self.assertTrue(success)
        self.assertEqual(result["name"], "Updated Video")

        # Verify it was updated
        videos = get_videos()
        self.assertEqual(len(videos["videos"]), 1)
        self.assertEqual(videos["videos"][0]["name"], "Updated Video")

    def test_delete_video(self):
        """Test deleting a video from the CSV"""
        # Add a video first
        video_data = {
            "id": 1,
            "name": "Test Video",
            "href": "http://example.com/test",
            "post_date": "2025-01-01",
            "views_count": 100,
        }
        add_video(video_data)

        # Verify it exists
        videos = get_videos()
        self.assertEqual(len(videos["videos"]), 1)

        # Delete the video
        result = delete_video(1)
        self.assertTrue(result)

        # Verify it was deleted
        videos = get_videos()
        self.assertEqual(len(videos["videos"]), 0)
