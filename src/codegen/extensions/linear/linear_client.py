import json
import logging
import os
from typing import Optional

import requests
from pydantic import BaseModel

logger = logging.getLogger(__name__)


# --- TYPES


class LinearUser(BaseModel):
    id: str
    name: str


class LinearComment(BaseModel):
    id: str
    body: str
    user: LinearUser | None = None


class LinearIssue(BaseModel):
    id: str
    title: str
    description: str | None = None


class LinearClient:
    api_headers: dict
    api_endpoint = "https://api.linear.app/graphql"

    def __init__(self, access_token: Optional[str] = None):
        if not access_token:
            access_token = os.getenv("LINEAR_ACCESS_TOKEN")
            if not access_token:
                msg = "access_token is required"
                raise ValueError(msg)
        self.access_token = access_token
        self.api_headers = {
            "Content-Type": "application/json",
            "Authorization": self.access_token,
        }

    def get_issue(self, issue_id: str) -> LinearIssue:
        query = """
            query getIssue($issueId: String!) {
                issue(id: $issueId) {
                    id
                    title
                    description
                }
            }
        """
        variables = {"issueId": issue_id}
        response = requests.post(self.api_endpoint, headers=self.api_headers, json={"query": query, "variables": variables})
        data = response.json()
        issue_data = data["data"]["issue"]
        return LinearIssue(id=issue_data["id"], title=issue_data["title"], description=issue_data["description"])

    def get_issue_comments(self, issue_id: str) -> list[LinearComment]:
        query = """
            query getIssueComments($issueId: String!) {
                issue(id: $issueId) {
                    comments {
                    nodes {
                        id
                        body
                        user {
                            id
                            name
                        }
                    }

                    }
                }
            }
        """
        variables = {"issueId": issue_id}
        response = requests.post(self.api_endpoint, headers=self.api_headers, json={"query": query, "variables": variables})
        data = response.json()
        comments = data["data"]["issue"]["comments"]["nodes"]

        # Parse comments into list of LinearComment objects
        parsed_comments = []
        for comment in comments:
            user = comment.get("user", None)
            parsed_comment = LinearComment(id=comment["id"], body=comment["body"], user=LinearUser(id=user.get("id"), name=user.get("name")) if user else None)
            parsed_comments.append(parsed_comment)

        # Convert raw comments to LinearComment objects
        return parsed_comments

    def comment_on_issue(self, issue_id: str, body: str) -> dict:
        """issue_id is our internal issue ID"""
        query = """mutation makeComment($issueId: String!, $body: String!) {
          commentCreate(input: {issueId: $issueId, body: $body}) {
            comment {
              id
              body
              url
              user {
                id
                name
              }
            }
          }
        }
        """
        variables = {"issueId": issue_id, "body": body}
        response = requests.post(
            self.api_endpoint,
            headers=self.api_headers,
            data=json.dumps({"query": query, "variables": variables}),
        )
        data = response.json()
        try:
            comment_data = data["data"]["commentCreate"]["comment"]

            return comment_data
        except Exception as e:
            msg = f"Error creating comment\n{data}\n{e}"
            raise Exception(msg)

    def register_webhook(self, webhook_url: str, team_id: str, secret: str, enabled: bool, resource_types: list[str]):
        mutation = """
            mutation createWebhook($input: WebhookCreateInput!) {
                webhookCreate(input: $input) {
                    success
                    webhook {
                    id
                    enabled
                    }
                }
            }
        """

        variables = {
            "input": {
                "url": webhook_url,
                "teamId": team_id,
                "resourceTypes": resource_types,
                "enabled": enabled,
                "secret": secret,
            }
        }

        response = requests.post(self.api_endpoint, headers=self.api_headers, json={"query": mutation, "variables": variables})
        body = response.json()
        return body

    def search_issues(self, query: str, limit: int = 10) -> list[LinearIssue]:
        """Search for issues using a query string.

        Args:
            query: Search query string
            limit: Maximum number of issues to return (default: 10)

        Returns:
            List of LinearIssue objects matching the search query
        """
        graphql_query = """
            query searchIssues($query: String!, $limit: Int!) {
                issueSearch(query: $query, first: $limit) {
                    nodes {
                        id
                        title
                        description
                    }
                }
            }
        """
        variables = {"query": query, "limit": limit}
        response = requests.post(
            self.api_endpoint,
            headers=self.api_headers,
            json={"query": graphql_query, "variables": variables},
        )
        data = response.json()

        try:
            issues_data = data["data"]["issueSearch"]["nodes"]
            return [
                LinearIssue(
                    id=issue["id"],
                    title=issue["title"],
                    description=issue["description"],
                )
                for issue in issues_data
            ]
        except Exception as e:
            msg = f"Error searching issues\n{data}\n{e}"
            raise Exception(msg)
