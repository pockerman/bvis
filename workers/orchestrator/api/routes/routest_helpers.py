import requests


def send_post_request(data: dict, url: str, api_version: str) -> None:
    response = requests.post(url=url,
                             headers={"api-version": api_version},
                             json=data)
