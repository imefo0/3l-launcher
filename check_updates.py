import requests
import version_setting_lib as vslib

url = "https://api.github.com/repos/imefo0/3l-launcher-test/releases"


def update_versions():
    response = requests.get(url, params={"per_page": 100}, timeout=15)
    releases = response.json()

    versions = { "versions": {} }

    for release in releases:
        tag = release["tag_name"]
        published_at = release.get("published_at")
        is_prerelease = release.get("prerelease", False)

        versions["versions"][tag] = {
            "body": release.get("body", "Нет описания"),
            "published_at": published_at,
            "user_published_at": vslib.format_date(published_at) if published_at else "Время неизвестно",
            "prerelease": is_prerelease,
            "user_prerelease": "prerelease" if is_prerelease else "release"
        }

    vslib.write_versions(versions)
    print(versions)

    print("список версий обновлен")

    vslib.add_installed(versions)

    print("список установленных версий обновлен")