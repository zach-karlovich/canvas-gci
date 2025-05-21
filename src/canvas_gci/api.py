import logging
import os
import time
from typing import List

import requests

from .models import CanvasModule


class CanvasAPIError(Exception):
    pass


class CanvasAPINotFound(CanvasAPIError):
    pass


class CanvasAPIUnauthorized(CanvasAPIError):
    pass


class CanvasAPI:
    def __init__(self, api_root: str = "https://canvas.instructure.com/api/v1"):
        self.api_root = api_root.rstrip("/")
        self.token = os.getenv("CANVAS_TOKEN")
        if not self.token:
            raise RuntimeError("CANVAS_TOKEN environment variable is required.")
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/json",
            }
        )

    def get_modules(self, course_id: int) -> List[CanvasModule]:
        url: str | None = f"{self.api_root}/courses/{course_id}/modules"
        params = {"per_page": 100}
        modules: List[CanvasModule] = []
        retries = 0
        while url:
            try:
                logging.debug(f"GET {url} params={params if retries == 0 else None}")
                resp = self.session.get(url, params=params if retries == 0 else None)
                if resp.status_code == 404:
                    raise CanvasAPINotFound(f"Course ID {course_id} not found (404).")
                if resp.status_code == 401 or resp.status_code == 403:
                    raise CanvasAPIUnauthorized(
                        f"Unauthorized or forbidden (status {resp.status_code}). "
                        "Check your CANVAS_TOKEN permissions."
                    )
                if resp.status_code >= 500:
                    if retries < 3:
                        retries += 1
                        logging.warning(
                            f"Server error {resp.status_code}, " f"retry {retries}..."
                        )
                        time.sleep(2**retries)
                        continue
                    else:
                        resp.raise_for_status()
                resp.raise_for_status()
                data = resp.json()
                modules.extend(CanvasModule.model_validate(m) for m in data)
                # Pagination: Canvas uses Link header
                next_url = None
                if "Link" in resp.headers:
                    links = resp.headers["Link"].split(",")
                    for link in links:
                        if 'rel="next"' in link:
                            next_url = link[link.find("<") + 1 : link.find(">")]
                            break
                url = next_url
                retries = 0
            except requests.RequestException as e:
                logging.error(f"Network or HTTP error: {e}")
                raise CanvasAPIError(f"Network or HTTP error: {e}")
        if not modules:
            logging.warning("No modules found for this course.")
        return modules


__all__ = [
    "CanvasAPI",
    "CanvasAPIError",
    "CanvasAPINotFound",
    "CanvasAPIUnauthorized",
]
