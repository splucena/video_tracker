# Video Tracker API (FastAPI Version)

A simple RESTful API for tracking videos, built with FastAPI.

## Description

Video Tracker API is a lightweight service that allows you to create, read, update, and delete video entries. All data is stored in a CSV file, making it easy to deploy without database dependencies.

## Features

* RESTful API with FastAPI
* CRUD operations for video entries
* Sorting capabilities by name, date, or view count
* Data persistence using CSV storage
* Validation of input data using Pydantic models
* Automatic interactive API documentation

## Installation

### Prerequisites

* Python 3.8 or higher
* pip (Python package installer)

### Setup

1. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create the data directory:

```bash
mkdir -p data
```

## Running the Application

Start the development server:

```bash
python app.py
```

Or use Uvicorn directly:

```bash
uvicorn app:app --reload
```

The API will be available at `http://127.0.0.1:8000/`.

Interactive API documentation is available at:

* Swagger UI: `http://127.0.0.1:8000/docs`
* ReDoc: `http://127.0.0.1:8000/redoc`

## API Endpoints

### Get All Videos

```
GET /videos/
```

**Query Parameters:**

* `sort_by` (optional): Field to sort by (`name`, `post_date`, or `views_count`)
* `order` (optional): Sort order (`asc` or `desc`)

**Response:** List of all videos

### Add a New Video

```
POST /videos/
```

**Request Body:**

```json
{
  "video": {
    "id": 1,
    "name": "Sample Video",
    "href": "http://example.com/video",
    "post_date": "2025-05-01",
    "views_count": 100
  }
}
```

**Response:** The created video with a 201 status code

### Update a Video

```
PUT /videos/{id}/
```

**Path Parameters:**

* `id`: The ID of the video to update

**Request Body:**

```json
{
  "video": {
    "id": 1,
    "name": "Updated Video",
    "href": "http://example.com/updated-video",
    "post_date": "2025-05-02",
    "views_count": 200
  }
}
```

**Response:** The updated video with a 200 status code

### Delete a Video

```
DELETE /videos/{id}
```

**Path Parameters:**

* `id`: The ID of the video to delete

**Response:** Success message with a 200 status code

## Data Format

Videos have the following structure:

* `id` (integer): Unique identifier for the video
* `name` (string): The title of the video
* `href` (string): URL to the video
* `post_date` (string): Date when the video was posted (format: YYYY-MM-DD)
* `views_count` (integer): Number of views

## Error Handling

The API returns appropriate HTTP status codes:

* `200 OK`: The request was successful
* `201 Created`: A resource was successfully created
* `400 Bad Request`: The request was invalid
* `404 Not Found`: The requested resource was not found
* `409 Conflict`: The request conflicts with the current state (e.g., duplicate ID)
* `500 Internal Server Error`: An error occurred on the server

## Project Structure

```
video_tracker_fastapi/
├── app.py                 # Main FastAPI application
├── models.py              # Pydantic models
├── csv_manager.py         # CSV data handling
├── data/                  # Data storage directory
│   └── videos.csv         # CSV file for video storage
├── requirements.txt       # Project dependencies
└── README.md              # This file
```

## License

This project is licensed under the MIT License.
