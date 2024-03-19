import requests
from typing import Optional
from bs4 import BeautifulSoup as soup

from ifunnybot.core.logging import Logger
from ifunnybot.data.headers import Headers
from ifunnybot.types.post import Post
from ifunnybot.types.post_type import PostType
from ifunnybot.utils.urls import get_datatype
from ifunnybot.utils.html import html_selectors

def get_post(url: str, _headers=Headers) -> Optional[Post]:

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
        Logger.error(f"There was an error making the HTTP request to {url}")
        return

    # transforming the response into something useable
    dom = soup(response.text, "html.parser")
    if not dom.css:
        Logger.fatal(f"There was an internal error with BeautifulSoup, cannot use CSS selectors")
        return

    ## the response was OK, now scraping information
    info = Post()

    # saving the url
    info.url = url

    # getting the datatype of the url
    datatype = get_datatype(url)
    if not datatype:
        # do something here
        Logger.error(f"Could not find any content at {url}.")
        return

    # logging
    Logger.info(f"Found {datatype} at {url}")

    # setting the data type of the post
    info.post_type = datatype

    # the targeted HTML element
    element = None

    ## getting the content of the post
    if info.post_type != PostType.MEME:
        # getting selectors & attributes
        selector, attribute = html_selectors[info.post_type]

        # using BeautifulSoup to get what I want
        element = dom.css.select(selector)
        if not element:
            Logger.error(f"Could not grab the content from {url}")
            return

        info.content_url = element[0].get(attribute)
    else:
        # need to iterate through all the selectors to find the proper
        # one because ifunny lol
        for _type in html_selectors.keys():
            ## searching for the right one

            # getting selectors & attributes
            selector, attribute = html_selectors[_type]

            # using BeautifulSoup to get what I want
            element = dom.css.select(selector)
            if not element:
                Logger.debug(f"Post at {url} is not {_type}")
                continue

            
            # breaking early because we found the correct selector
            Logger.debug(f"Post at {url} is {_type}")
            info.post_type = _type
            info.content_url = element[0].get(attribute)

            break

    ## scraping other info about the post
    info.username = dom.css.select("div._9JPE > a.WiQc > span.IfB6")[0].text.replace(" ", "")
    info.icon_url = dom.css.select("div._9JPE > a.WiQc > img.dLxH")[0].get("data-src")
    info.likes = dom.css.select("div._9JPE > button.Cgfc > span.Y2eM > span")[0].text
    info.comments = dom.css.select("div._9JPE > button.Cgfc > span.Y2eM > span")[1].text

    # logging
    Logger.info(f"Retrieved from {url}: {info}")

    # getting the content of the post
    info.retrieve_content()

    # if the post is an image, crop it
    if info.post_type == PostType.PICTURE:
        info.crop_watermark()

    # returning the collected information
    return info

