import pytest

from codegen.git.utils.clone_url import add_access_token_to_url


@pytest.mark.parametrize(
    "url, token, expected",
    [
        ("https://github.com/owner/repo.git", "token", "https://x-access-token:token@github.com/owner/repo.git"),  # https url with token
        ("https://github.com/owner/repo.git", None, "https://github.com/owner/repo.git"),  # https url without token
        ("https://github.com/owner/repo.git", "", "https://github.com/owner/repo.git"),  # https url with empty token
        ("github.com/owner/repo", "token", "https://x-access-token:token@github.com/owner/repo"),  # scheme missing with token
        ("github.com/owner/repo", None, "https://github.com/owner/repo"),  # scheme missing without token
        ("github.com/owner/repo", "", "https://github.com/owner/repo"),  # scheme missing with empty token
    ],
)
def test_add_access_token_to_url(url, token, expected):
    assert add_access_token_to_url(url, token) == expected
