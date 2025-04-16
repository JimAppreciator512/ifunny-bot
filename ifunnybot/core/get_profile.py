import requests
from typing import Optional
from bs4 import BeautifulSoup as soup

from ifunnybot.core.logging import Logger
from ifunnybot.data import Headers
from ifunnybot.types import Profile
from ifunnybot.utils import IFUNNY_NO_PFP, get_username_from_url


def get_profile_by_name(username: str, _headers=Headers) -> Optional[Profile]:
    return _get_profile(username, _headers=_headers)


def get_profile_by_url(url: str, _headers=Headers) -> Optional[Profile]:
    if username := get_username_from_url(url):
        return _get_profile(username, _headers=_headers)
    Logger.error(f"Could not extract the user from {url}.")
    return None


def _get_profile(username: str, _headers=Headers) -> Optional[Profile]:

    # creating the url of the user
    url = f"https://ifunny.co/user/{username}"

    # creating the profile object
    profile = Profile(username=username)

    # getting the post, assuming that it is a proper link
    response = None
    try:
        response = requests.get(url, headers=_headers, allow_redirects=False)
    except Exception as e:
        Logger.error(f"There was an exception making a GET request to {url}: {e}")
        return None

    # testing the response code
    if response.status_code != requests.codes.ok:
        # do something here
        Logger.error(f"No such user at {url} exists.")
        return None

    # transforming the response into something useable
    dom = soup(response.text, "html.parser")
    if not dom.css:
        Logger.fatal(
            f"There was an internal error with BeautifulSoup, cannot use CSS selectors"
        )
        return None

    ## scraping information

    # getting the profile picture
    if icon_el := dom.css.select("span._4nz- > span.F6b- > img.k3q9"):
        # the user has a pfp
        profile.icon_url = icon_el[0].get("src")
    else:
        # the user does not have a pfp
        Logger.info(f"User {username} doesn't have a pfp.")
        profile.icon_url = IFUNNY_NO_PFP

    # getting the description
    if description_el := dom.css.select("div.Hi31 > div.vjX5"):
        # the user has a description
        profile.description = description_el[0].text.strip()
    else:
        profile.description = "No description."

    # getting the subscriber count
    if subscriber_el := dom.css.select("div.Hi31 > div[class='g+J7'] > a.sWk7"):
        profile.subscribers = subscriber_el[0].text.strip().split(" ")[0]
    else:
        profile.subscribers = "No subscribers."

    # getting the subscriptions
    if subscription_el := dom.css.select("div.Hi31 > div[class='g+J7'] > a.sWk7"):
        profile.subscriptions = subscription_el[1].text.strip().split(" ")[0]
    else:
        profile.subscriptions = "No subscriptions."

    # getting the features
    if features_el := dom.css.select("div.Hi31 > div._2tcI"):
        profile.features = features_el[0].text.strip().split(" ")[0]
    else:
        profile.features = "No features."

    # logging
    Logger.info(f"Retrieved from {url}: {profile}")

    # returning the collected information
    return profile
