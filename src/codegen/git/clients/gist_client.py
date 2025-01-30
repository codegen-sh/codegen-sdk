from typing import Any, Optional
from urllib.parse import urljoin

import requests
from requests.exceptions import RequestException


class GistClientError(Exception):
    """Base exception for GistClient errors."""

    pass


class GistAuthenticationError(GistClientError):
    """Raised when authentication fails."""

    pass


class GistClient:
    """A client for interacting with GitHub Gists API.

    This client provides methods to read and update GitHub Gists using the GitHub API v3.
    It supports both authenticated and unauthenticated requests, though some operations
    require authentication.
    """

    def __init__(self, token: Optional[str] = None) -> None:
        """Initialize the GistClient with your GitHub personal access token.

        Args:
            token (Optional[str]): GitHub personal access token with gist scope

        Raises:
            GistAuthenticationError: If the provided token is invalid
        """
        self.base_url = "https://api.github.com"
        self.headers = {"Accept": "application/vnd.github.v3+json", "User-Agent": "GistClient"}

        if token:
            self.headers["Authorization"] = f"token {token}"

        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def _make_request(self, method: str, endpoint: str, **kwargs) -> dict[str, Any]:
        """Make an HTTP request to the GitHub API.

        Args:
            method (str): HTTP method to use
            endpoint (str): API endpoint to call
            **kwargs: Additional arguments to pass to requests

        Returns:
            Dict[str, Any]: JSON response from the API

        Raises:
            GistClientError: If the request fails
            GistAuthenticationError: If authentication fails
        """
        try:
            url = urljoin(self.base_url, endpoint)
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                msg = "Invalid authentication token"
                raise GistAuthenticationError(msg) from e
            msg = f"GitHub API request failed: {e!s}"
            raise GistClientError(msg) from e
        except RequestException as e:
            msg = f"Request failed: {e!s}"
            raise GistClientError(msg) from e

    def get_gist(self, gist_id: str) -> dict[str, Any]:
        """Fetch a specific gist.

        Args:
            gist_id (str): The ID of the gist to fetch

        Returns:
            Dict[str, Any]: The gist data
        """
        return self._make_request("GET", f"/gists/{gist_id}")

    def update_gist(self, gist_id: str, filename: str, content: str, description: Optional[str] = None) -> dict[str, Any]:
        """Update a specific file in a gist.

        Args:
            gist_id (str): The ID of the gist to update
            filename (str): The name of the file to update
            content (str): The new content for the file
            description (Optional[str]): New description for the gist

        Returns:
            Dict[str, Any]: The updated gist data

        Raises:
            GistAuthenticationError: If no authentication token was provided
        """
        if not self.headers.get("Authorization"):
            msg = "Authentication token required to update a gist"
            raise GistAuthenticationError(msg)

        payload = {"files": {filename: {"content": content}}}
        if description:
            payload["description"] = description

        return self._make_request("PATCH", f"/gists/{gist_id}", json=payload)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()
