import os
import requests

# здесь НЕТ github токена >:)
# there is NO github token >:)

def github_get(url, timeout=15, **kwargs):
    token = os.getenv("GITHUB_TOKEN")

    headers = kwargs.pop("headers", {})

    if token:
        headers["Authorization"] = f"Bearer {token}"

    print("Токен найден:", bool(token))
    print("Авторизация:", bool(headers.get("Authorization")))

    return requests.get(
        url,
        headers=headers,
        timeout=timeout,
        **kwargs
    )