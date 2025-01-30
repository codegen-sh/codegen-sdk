from typing import Optional

import requests


class GistClient:
    def __init__(self, token: str):
        """Initialize the GistUpdater with your GitHub personal access token.

        Args:
            token (str): GitHub personal access token with gist scope
        """
        self.headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
        self.base_url = "https://api.github.com"

    def get_gist(self, gist_id: str) -> dict:
        """Fetch a specific gist.

        Args:
            gist_id (str): The ID of the gist to fetch

        Returns:
            Dict: The gist data
        """
        response = requests.get(f"{self.base_url}/gists/{gist_id}", headers=self.headers)
        response.raise_for_status()
        return response.json()

    def update_gist(self, gist_id: str, filename: str, content: str, description: Optional[str] = None) -> dict:
        """Update a specific file in a gist.

        Args:
            gist_id (str): The ID of the gist to update
            filename (str): The name of the file to update
            content (str): The new content for the file
            description (Optional[str]): New description for the gist

        Returns:
            Dict: The updated gist data
        """
        payload = {"files": {filename: {"content": content}}}

        if description:
            payload["description"] = description

        response = requests.patch(f"{self.base_url}/gists/{gist_id}", headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()
