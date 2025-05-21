# NOTE: This is a manual test script and not part of the automated test suite.
# It was used for initial API connectivity testing for modules.

import requests
import os
from dotenv import load_dotenv
from typing import Optional # Added for type hints if needed, though not strictly for this fix


def get_course_modules(canvas_base_url: str, access_token: str, course_id: str) -> None:
    """
    Fetches modules for a specific course from the Canvas API.

    Args:
        canvas_base_url: The base URL of your Canvas instance (e.g., "https://canvas.its.virginia.edu/api/v1").
        access_token: Your Canvas API access token.
        course_id: The ID of the course to fetch modules for.
    """
    # Note: canvas_base_url is expected to be like "https://.../api/v1"
    api_url = f"{canvas_base_url}/courses/{course_id}/modules"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    params = {
        "per_page": 10
    }

    print(f"Fetching modules for course {course_id} from {api_url}")
    print(f"Params: {params}")

    try:
        response = requests.get(api_url, headers=headers, params=params)
        response.raise_for_status()  # Raises an HTTPError for bad responses

        print(f"Status Code: {response.status_code}")
        print("Response JSON:")
        try:
            print(response.json())
        except requests.exceptions.JSONDecodeError:
            print("Could not decode JSON. Raw response text:")
            print(response.text)

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        response_text = "No response object"
        if 'response' in locals() and hasattr(response, 'text'):
            response_text = response.text
        print(f"Response Text: {response_text}")
    except requests.exceptions.RequestException as err:
        print(f"Other error occurred: {err}")


if __name__ == "__main__":
    load_dotenv()

    CANVAS_BASE_URL_OPT = os.getenv("PYTEST_CANVAS_API_ROOT")
    ACCESS_TOKEN_OPT = os.getenv("CANVAS_TOKEN")
    COURSE_ID_OPT = os.getenv("PYTEST_VALID_COURSE_ID")

    if not all([CANVAS_BASE_URL_OPT, ACCESS_TOKEN_OPT, COURSE_ID_OPT]):
        print(
            "Please ensure PYTEST_CANVAS_API_ROOT, CANVAS_TOKEN, and "
            "PYTEST_VALID_COURSE_ID are set in your .env file."
        )
    else:
        # Assert that the variables are not None after the check
        CANVAS_BASE_URL: str = CANVAS_BASE_URL_OPT # type: ignore
        ACCESS_TOKEN: str = ACCESS_TOKEN_OPT       # type: ignore
        COURSE_ID: str = COURSE_ID_OPT             # type: ignore
        get_course_modules(CANVAS_BASE_URL, ACCESS_TOKEN, COURSE_ID)
